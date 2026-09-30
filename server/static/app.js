/**
 * Interactive Frontend Controller for AI Engineer Assessment Dashboard.
 * Powers Voice Agent Calling, Hybrid KB Explorer, Multilingual Bots,
 * and Real-Time Live Nudges Pipeline.
 */

let currentSessionId = null;
let callTimerInterval = null;
let callSeconds = 0;
let isCallActive = false;
let speechRecognition = null;
let currentMarket = "ph";
let q4Scenarios = [];
let isQ4Streaming = false;

// -------------------------------------------------------------
// TAB NAVIGATION
// -------------------------------------------------------------
function switchTab(tabId) {
  document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".tab-btn").forEach(el => el.classList.remove("active"));

  const targetTab = document.getElementById(tabId);
  if (targetTab) targetTab.classList.add("active");

  const activeBtn = Array.from(document.querySelectorAll(".tab-btn")).find(b => b.getAttribute("onclick").includes(tabId));
  if (activeBtn) activeBtn.classList.add("active");

  if (tabId === "q2-tab") {
    loadQ2AuditTable();
    performQ2Search();
  } else if (tabId === "q3-tab") {
    loadQ3MarketData(currentMarket);
  } else if (tabId === "q4-tab") {
    loadQ4InitialData();
  }
}

// -------------------------------------------------------------
// QUESTION 1: VOICE AGENT & CALLING
// -------------------------------------------------------------
function speakText(text) {
  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.05;
    utterance.pitch = 1.0;
    const voices = window.speechSynthesis.getVoices();
    const engVoice = voices.find(v => v.lang.startsWith("en") && (v.name.includes("Natural") || v.name.includes("Google") || v.name.includes("Zira")));
    if (engVoice) utterance.voice = engVoice;
    window.speechSynthesis.speak(utterance);
  }
}

async function toggleQ1Call() {
  const btn = document.getElementById("btn-call-toggle");
  const micBtn = document.getElementById("btn-mic-toggle");
  const input = document.getElementById("q1-text-input");
  const sendBtn = document.getElementById("btn-send");
  const escBtn = document.getElementById("btn-esc");
  const statusBadge = document.getElementById("call-status-badge");
  const waveform = document.getElementById("waveform-anim");

  if (!isCallActive) {
    // Start Call
    btn.textContent = "⏹ End Call";
    btn.className = "btn btn-rose";
    micBtn.disabled = false;
    input.disabled = false;
    sendBtn.disabled = false;
    escBtn.disabled = false;
    isCallActive = true;
    waveform.style.opacity = "1";

    statusBadge.innerHTML = "<span>CALL IN PROGRESS</span>";
    statusBadge.style.background = "rgba(16, 185, 129, 0.15)";
    statusBadge.style.color = "var(--accent-emerald)";

    // Start timer
    callSeconds = 0;
    clearInterval(callTimerInterval);
    callTimerInterval = setInterval(() => {
      callSeconds++;
      const mins = String(Math.floor(callSeconds / 60)).padStart(2, "0");
      const secs = String(callSeconds % 60).padStart(2, "0");
      document.getElementById("q1-call-timer").textContent = `${mins}:${secs}`;
    }, 1000);

    // Call API
    try {
      const resp = await fetch("/api/q1/call/start", { method: "POST" });
      const data = await resp.json();
      currentSessionId = data.session_id;
      document.getElementById("q1-session-label").textContent = currentSessionId;

      appendChatMessage("agent", "ApexCare AI Concierge (Alex)", data.initial_message);
      speakText(data.initial_message);
    } catch (e) {
      console.error("Failed to start call:", e);
    }
  } else {
    // End Call
    isCallActive = false;
    clearInterval(callTimerInterval);
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    btn.textContent = "▶ Start Call";
    btn.className = "btn btn-emerald";
    micBtn.disabled = true;
    input.disabled = true;
    sendBtn.disabled = true;
    escBtn.disabled = true;
    waveform.style.opacity = "0.2";

    statusBadge.innerHTML = "<span>CALL DISCONNECTED</span>";
    statusBadge.style.background = "rgba(156, 163, 175, 0.15)";
    statusBadge.style.color = "var(--text-muted)";
    appendChatMessage("agent", "System", "Call ended by user.");
  }
}

async function sendQ1Utterance(explicitText = null) {
  const input = document.getElementById("q1-text-input");
  const text = (explicitText !== null ? explicitText : input.value).trim();
  if (!text || !currentSessionId) return;

  if (explicitText === null) input.value = "";
  appendChatMessage("customer", "You (Customer)", text);

  try {
    const resp = await fetch("/api/q1/call/step", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: currentSessionId, utterance: text })
    });
    const data = await resp.json();

    appendChatMessage("agent", "ApexCare AI Concierge (Alex)", data.reply, data.citation);
    speakText(data.reply);

    // Update Grounding Card
    const groundingCard = document.getElementById("q1-grounding-display");
    if (data.citation) {
      groundingCard.innerHTML = `
        <div style="background: rgba(6,182,212,0.1); border: 1px solid rgba(6,182,212,0.3); border-radius: 6px; padding: 0.6rem;">
          <strong style="color: var(--accent-cyan); display: block; margin-bottom: 0.25rem;">Grounded Citation Verified:</strong>
          <span style="font-family: monospace; font-size: 0.8rem; color: #a5f3fc;">${data.citation}</span>
        </div>
      `;
    }

    // Update CRM Business Action Card
    const crmCard = document.getElementById("q1-crm-display");
    if (data.action) {
      const act = data.action;
      crmCard.innerHTML = `
        <div style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 6px; padding: 0.6rem;">
          <strong style="color: var(--accent-emerald); display: block; margin-bottom: 0.25rem;">Action Dispatched: ${act.action || act.type}</strong>
          <p style="font-size: 0.8rem; margin: 0.2rem 0;">Lead ID: <code>${act.lead_id || act.ticket_id || 'N/A'}</code></p>
          <p style="font-size: 0.8rem; color: var(--text-muted);">${act.message || act.details || ''}</p>
        </div>
      `;
    }

    if (data.escalated) {
      const statusBadge = document.getElementById("call-status-badge");
      statusBadge.innerHTML = "<span>WARM ESCALATION TRIGGERED</span>";
      statusBadge.style.background = "rgba(244, 63, 94, 0.2)";
      statusBadge.style.color = "var(--accent-rose)";
    }
  } catch (e) {
    console.error("Step call failed:", e);
  }
}

function triggerQ1Escalation() {
  sendQ1Utterance("I demand to speak with a human underwriting specialist right now.");
}

function appendChatMessage(type, sender, text, citation = null) {
  const box = document.getElementById("q1-chat-box");
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${type}`;
  bubble.innerHTML = `
    <div class="chat-sender">${sender}</div>
    <div>${text}</div>
    ${citation ? `<div class="citation-badge">📌 ${citation}</div>` : ""}
  `;
  box.appendChild(bubble);
  box.scrollTop = box.scrollHeight;
}

function toggleMicrophone() {
  const micBtn = document.getElementById("btn-mic-toggle");
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRec) {
    alert("Web Speech Recognition API is not supported in this browser. Please type customer responses.");
    return;
  }

  if (speechRecognition) {
    speechRecognition.stop();
    speechRecognition = null;
    micBtn.textContent = "🎤 Speak";
    micBtn.className = "btn btn-outline";
    return;
  }

  speechRecognition = new SpeechRec();
  speechRecognition.continuous = false;
  speechRecognition.interimResults = false;
  speechRecognition.lang = "en-US";

  speechRecognition.onstart = () => {
    micBtn.textContent = "🔴 Listening...";
    micBtn.className = "btn btn-rose";
  };

  speechRecognition.onresult = (evt) => {
    const transcript = evt.results[0][0].transcript;
    document.getElementById("q1-text-input").value = transcript;
    sendQ1Utterance(transcript);
  };

  speechRecognition.onerror = (err) => {
    console.error("Mic error:", err);
    micBtn.textContent = "🎤 Speak";
    micBtn.className = "btn btn-outline";
    speechRecognition = null;
  };

  speechRecognition.onend = () => {
    micBtn.textContent = "🎤 Speak";
    micBtn.className = "btn btn-outline";
    speechRecognition = null;
  };

  speechRecognition.start();
}

async function loadQ1RecordedCalls() {
  try {
    const resp = await fetch("/api/q1/test-calls");
    const calls = await resp.json();
    const container = document.getElementById("q1-recorded-calls-grid");
    container.innerHTML = "";

    const audioMap = {
      "CALL-01-COOPERATIVE": "/audio/q1/call_01_cooperative.wav",
      "CALL-02-OBJECTIONS": "/audio/q1/call_02_objections.wav",
      "CALL-03-CONFLICTING-OUTOFSCOPE": "/audio/q1/call_03_conflicting_out_of_scope.wav",
      "CALL-04-HUMAN-ESCALATION": "/audio/q1/call_04_human_escalation.wav"
    };

    calls.forEach(call => {
      const audioUrl = audioMap[call.call_id] || "";
      const card = document.createElement("div");
      card.style.background = "rgba(0,0,0,0.3)";
      card.style.padding = "1rem";
      card.style.borderRadius = "8px";
      card.style.border = "1px solid var(--border-color)";

      let transcriptHtml = call.transcript.map(t => `
        <div style="margin-bottom: 0.4rem; font-size: 0.8rem;">
          <strong style="color: ${t.speaker === 'Agent' ? 'var(--accent-indigo)' : 'var(--accent-cyan)'};">${t.speaker}:</strong>
          ${t.text}
        </div>
      `).join("");

      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
          <strong style="color: var(--accent-cyan); font-size: 0.95rem;">${call.call_id}: ${call.caller_profile.category}</strong>
          <span style="font-size: 0.75rem; color: var(--text-muted);">${call.call_duration_seconds}s | Final: ${call.final_state}</span>
        </div>
        <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.75rem;">${call.description}</p>
        <audio controls class="audio-player-custom" src="${audioUrl}" style="margin-bottom: 0.75rem;"></audio>
        <details>
          <summary style="font-size: 0.8rem; cursor: pointer; color: var(--accent-indigo); margin-bottom: 0.5rem;">View Full Conversation Transcript (${call.transcript.length} turns)</summary>
          <div style="max-height: 180px; overflow-y: auto; background: rgba(0,0,0,0.4); padding: 0.5rem; border-radius: 6px;">
            ${transcriptHtml}
          </div>
        </details>
      `;
      container.appendChild(card);
    });
  } catch (e) {
    console.error("Failed to load Q1 recorded calls:", e);
  }
}

// -------------------------------------------------------------
// QUESTION 2: KNOWLEDGE BASE SEARCH & AUDIT
// -------------------------------------------------------------
async function performQ2Search() {
  const query = document.getElementById("q2-search-input").value.trim();
  if (!query) return;

  const container = document.getElementById("q2-search-results");
  container.innerHTML = `<span style="font-size: 0.85rem; color: var(--text-muted);">Searching knowledge base...</span>`;

  try {
    const resp = await fetch(`/api/q2/search?q=${encodeURIComponent(query)}&top_k=2`);
    const results = await resp.json();
    container.innerHTML = "";

    if (results.length === 0) {
      container.innerHTML = `<span style="font-size: 0.85rem; color: var(--accent-amber);">No matching records found above threshold.</span>`;
      return;
    }

    results.forEach(rec => {
      const card = document.createElement("div");
      card.style.background = "rgba(0,0,0,0.3)";
      card.style.border = "1px solid var(--border-color)";
      card.style.borderRadius = "8px";
      card.style.padding = "0.85rem";

      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
          <strong style="color: var(--accent-cyan); font-size: 0.9rem;">[${rec.record_id}] ${rec.title}</strong>
          <span style="font-family: monospace; font-size: 0.8rem; color: var(--accent-emerald);">Hybrid: ${(rec.score * 100).toFixed(1)}%</span>
        </div>
        <p style="font-size: 0.82rem; color: var(--text-main); margin-bottom: 0.5rem; line-height: 1.4;">${rec.content}</p>
        <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: var(--text-muted); border-top: 1px solid rgba(255,255,255,0.05); padding-top: 0.4rem;">
          <span>BM25: ${(rec.bm25_score * 100).toFixed(1)}% | Dense: ${(rec.dense_score * 100).toFixed(1)}%</span>
          <span>Source: ${rec.source_file}</span>
        </div>
        <div class="citation-badge" style="margin-top: 0.4rem;">${rec.citation}</div>
      `;
      container.appendChild(card);
    });
  } catch (e) {
    console.error("Q2 search failed:", e);
  }
}

async function loadQ2AuditTable() {
  const tbody = document.querySelector("#q2-audit-table tbody");
  tbody.innerHTML = `<tr><td colspan="7">Loading retrieval audit benchmark...</td></tr>`;

  try {
    const resp = await fetch("/api/q2/audit-benchmark");
    const data = await resp.json();
    tbody.innerHTML = "";

    data.forEach(item => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td><strong>${item.test_id}</strong></td>
        <td>${item.category}</td>
        <td>${item.user_question}</td>
        <td><code>${item.retrieved_record_id}</code></td>
        <td style="font-family: monospace; color: var(--accent-cyan);">${(item.confidence_score * 100).toFixed(1)}%</td>
        <td><span style="font-size: 0.75rem; color: var(--text-muted);">${item.source_reference}</span></td>
        <td><strong class="verdict-pass">${item.verdict}</strong></td>
      `;
      tbody.appendChild(row);
    });
  } catch (e) {
    console.error("Failed to load Q2 audit table:", e);
  }
}

// -------------------------------------------------------------
// QUESTION 3: MULTILINGUAL BOTS
// -------------------------------------------------------------
function switchMarket(mkt) {
  currentMarket = mkt;
  document.getElementById("btn-mkt-ph").className = mkt === "ph" ? "btn btn-cyan" : "btn btn-outline";
  document.getElementById("btn-mkt-id").className = mkt === "id" ? "btn btn-cyan" : "btn btn-outline";
  loadQ3MarketData(mkt);
}

async function loadQ3MarketData(mkt) {
  try {
    const cfgResp = await fetch("/api/q3/configs");
    const configs = await cfgResp.json();
    const callsResp = await fetch("/api/q3/calls");
    const calls = await callsResp.json();

    const titleEl = document.getElementById("mkt-config-title");
    const bodyEl = document.getElementById("mkt-config-body");
    const audioContainer = document.getElementById("mkt-audio-player-container");
    const caseStudiesGrid = document.getElementById("mkt-case-studies-grid");

    if (mkt === "ph") {
      const cfg = configs.philippines;
      titleEl.innerHTML = `⚙️ Philippines Market: ${cfg.sector}`;
      bodyEl.innerHTML = `
        <p><strong>Bot Name:</strong> ${cfg.bot_name}</p>
        <p><strong>Languages:</strong> ${cfg.supported_languages.join(", ")}</p>
        <p><strong>ASR Configuration:</strong> ${cfg.asr_configuration.recommended_provider} (${cfg.asr_configuration.language_code})</p>
        <p><strong>TTS Voice:</strong> ${cfg.tts_configuration.recommended_voice}</p>
        <p><strong>Acoustic Notes:</strong> ${cfg.asr_configuration.acoustic_model_notes}</p>
        <p><strong>Technical Compromise:</strong> ${cfg.tts_configuration.compromises}</p>
      `;

      // Audio players for PH
      audioContainer.innerHTML = "";
      const phCalls = [
        { id: "PH-01", data: calls.ph_01, audio: "/audio/q3/ph/call_ph_01_cooperative_taglish.wav" },
        { id: "PH-02", data: calls.ph_02, audio: "/audio/q3/ph/call_ph_02_objection_bancassurance.wav" }
      ];
      phCalls.forEach(c => {
        if (!c.data) return;
        const div = document.createElement("div");
        div.style.background = "rgba(0,0,0,0.3)";
        div.style.padding = "0.75rem";
        div.style.borderRadius = "8px";
        div.innerHTML = `
          <strong style="color: var(--accent-cyan); display: block; margin-bottom: 0.35rem;">${c.id}: ${c.data.type}</strong>
          <audio controls class="audio-player-custom" src="${c.audio}" style="margin-bottom: 0.5rem;"></audio>
          <details>
            <summary style="font-size: 0.78rem; cursor: pointer; color: var(--accent-indigo);">View Taglish Transcript</summary>
            <div style="font-size: 0.78rem; max-height: 120px; overflow-y: auto; padding: 0.4rem; background: rgba(0,0,0,0.3); border-radius: 4px; margin-top: 0.3rem;">
              ${c.data.transcript.map(t => `<div><strong>${t.speaker}:</strong> ${t.text}</div>`).join("")}
            </div>
          </details>
        `;
        audioContainer.appendChild(div);
      });

      // Case Studies for PH
      caseStudiesGrid.innerHTML = `
        <div class="card" style="background: rgba(0,0,0,0.25);">
          <strong style="color: var(--accent-cyan);">Case 1: Beneficiary Framing</strong>
          <p style="font-size: 0.75rem; color: #fca5a5; margin-top: 0.4rem;"><strong>Literal:</strong> "Sino tatanggap kapag namatay ka?" (Offensive, bad omen).</p>
          <p style="font-size: 0.75rem; color: #86efac; margin-top: 0.3rem;"><strong>Taglish:</strong> "Primary beneficiaries para secured ang education at kinabukasan ng mga anak."</p>
        </div>
        <div class="card" style="background: rgba(0,0,0,0.25);">
          <strong style="color: var(--accent-cyan);">Case 2: Budget Objection (Malasakit)</strong>
          <p style="font-size: 0.75rem; color: #fca5a5; margin-top: 0.4rem;"><strong>Literal:</strong> "Wala kang sapat na pera? Mura lang ito." (Condescending).</p>
          <p style="font-size: 0.75rem; color: #86efac; margin-top: 0.3rem;"><strong>Taglish:</strong> "May 31-day grace period at Premium Holiday rider para hindi mag-lapse."</p>
        </div>
        <div class="card" style="background: rgba(0,0,0,0.25);">
          <strong style="color: var(--accent-cyan);">Case 3: Bank Referral Trust</strong>
          <p style="font-size: 0.75rem; color: #fca5a5; margin-top: 0.4rem;"><strong>Literal:</strong> "Sisingilin ng bangko ang iyong account nang kusa." (Coercive).</p>
          <p style="font-size: 0.75rem; color: #86efac; margin-top: 0.3rem;"><strong>Taglish:</strong> "Zero-fee automatic debit mula sa savings account—hindi na kailangang pumila."</p>
        </div>
      `;
    } else {
      // Indonesia
      const cfg = configs.indonesia;
      titleEl.innerHTML = `⚙️ Indonesia Market: ${cfg.sector}`;
      bodyEl.innerHTML = `
        <p><strong>Bot Name:</strong> ${cfg.bot_name}</p>
        <p><strong>Languages:</strong> ${cfg.supported_languages.join(", ")}</p>
        <p><strong>ASR Configuration:</strong> ${cfg.asr_configuration.recommended_provider} (${cfg.asr_configuration.language_code})</p>
        <p><strong>TTS Voice:</strong> ${cfg.tts_configuration.recommended_voice}</p>
        <p><strong>Acoustic Notes:</strong> ${cfg.asr_configuration.acoustic_model_notes}</p>
        <p><strong>Regional Accent:</strong> East Java dialect loanwords (nggih, monggo, dospundi, matur nuwun).</p>
      `;

      audioContainer.innerHTML = "";
      const idCalls = [
        { id: "ID-01", data: calls.id_01, audio: "/audio/q3/id/call_id_01_cicilan_jatuh_tempo.wav" },
        { id: "ID-02", data: calls.id_02, audio: "/audio/q3/id/call_id_02_regional_objection.wav" }
      ];
      idCalls.forEach(c => {
        if (!c.data) return;
        const div = document.createElement("div");
        div.style.background = "rgba(0,0,0,0.3)";
        div.style.padding = "0.75rem";
        div.style.borderRadius = "8px";
        div.innerHTML = `
          <strong style="color: var(--accent-cyan); display: block; margin-bottom: 0.35rem;">${c.id}: ${c.data.type}</strong>
          <audio controls class="audio-player-custom" src="${c.audio}" style="margin-bottom: 0.5rem;"></audio>
          <details>
            <summary style="font-size: 0.78rem; cursor: pointer; color: var(--accent-indigo);">View Indonesian Transcript</summary>
            <div style="font-size: 0.78rem; max-height: 120px; overflow-y: auto; padding: 0.4rem; background: rgba(0,0,0,0.3); border-radius: 4px; margin-top: 0.3rem;">
              ${c.data.transcript.map(t => `<div><strong>${t.speaker}:</strong> ${t.text}</div>`).join("")}
            </div>
          </details>
        `;
        audioContainer.appendChild(div);
      });

      // Case Studies for ID
      caseStudiesGrid.innerHTML = `
        <div class="card" style="background: rgba(0,0,0,0.25);">
          <strong style="color: var(--accent-cyan);">Case 1: Cicilan Jatuh Tempo</strong>
          <p style="font-size: 0.75rem; color: #fca5a5; margin-top: 0.4rem;"><strong>Literal:</strong> "Bayar hutangmu sebelum tanggal lima atau kamu dihukum." (OJK violation).</p>
          <p style="font-size: 0.75rem; color: #86efac; margin-top: 0.3rem;"><strong>Localized:</strong> "Cicilan motor nomor 88201 akan jatuh tempo tanggal 5 lusa, ada yang bisa dibantu?"</p>
        </div>
        <div class="card" style="background: rgba(0,0,0,0.25);">
          <strong style="color: var(--accent-cyan);">Case 2: Regional Late Fee Objection</strong>
          <p style="font-size: 0.75rem; color: #fca5a5; margin-top: 0.4rem;"><strong>Literal:</strong> "Denda adalah denda. Anda harus bayar." (Confrontational).</p>
          <p style="font-size: 0.75rem; color: #86efac; margin-top: 0.3rem;"><strong>Localized:</strong> "Nggih matur nuwun infonya Pak, kami bantu ajukan permohonan keringanan denda ke tim analis."</p>
        </div>
        <div class="card" style="background: rgba(0,0,0,0.25);">
          <strong style="color: var(--accent-cyan);">Case 3: Cash Payment Channels</strong>
          <p style="font-size: 0.75rem; color: #fca5a5; margin-top: 0.4rem;"><strong>Literal:</strong> "Kirim uang ke nomor rekening virtual komersial." (Abstract).</p>
          <p style="font-size: 0.75rem; color: #86efac; margin-top: 0.3rem;"><strong>Localized:</strong> "Cukup tunjukkan nomor kontrak di kasir Indomaret/Alfamart, struk resmi terbit lunas."</p>
        </div>
      `;
    }
  } catch (e) {
    console.error("Failed to load Q3 market data:", e);
  }
}

// -------------------------------------------------------------
// QUESTION 4: REAL-TIME LIVE NUDGES
// -------------------------------------------------------------
async function loadQ4InitialData() {
  try {
    const scResp = await fetch("/api/q4/scenarios");
    q4Scenarios = await scResp.json();
    const latResp = await fetch("/api/q4/latency-report");
    const latData = await latResp.json();

    if (latData.latency_metrics && latData.latency_metrics.metrics) {
      const e2e = latData.latency_metrics.metrics.end_to_end;
      document.getElementById("q4-p50-val").textContent = `${e2e.p50_ms}ms`;
      document.getElementById("q4-p95-val").textContent = `${e2e.p95_ms}ms`;
    }
  } catch (e) {
    console.error("Failed to load Q4 initial data:", e);
  }
}

function loadQ4Scenario() {
  const selIdx = parseInt(document.getElementById("q4-scenario-select").value);
  const scenario = q4Scenarios[selIdx];
  const transcriptBox = document.getElementById("q4-stream-transcript");
  transcriptBox.innerHTML = `
    <div style="font-size: 0.85rem; color: var(--text-muted); text-align: center; margin-top: 4rem;">
      Ready to stream: <strong>${scenario.title}</strong><br>
      Expected Event: <code>${scenario.expected_signal}</code> (${scenario.chunks.length} chunks)<br>
      Click "Stream Live Call" to start audio playback and real-time inference.
    </div>
  `;
  document.getElementById("q4-nudges-feed").innerHTML = "";
  document.getElementById("active-nudges-count").textContent = "0 ACTIVE";
}

function resetQ4Stream() {
  isQ4Streaming = false;
  loadQ4Scenario();
}

async function startStreamingSimulation() {
  if (isQ4Streaming) return;
  isQ4Streaming = true;

  const selIdx = parseInt(document.getElementById("q4-scenario-select").value);
  const scenario = q4Scenarios[selIdx];
  const transcriptBox = document.getElementById("q4-stream-transcript");
  const nudgesFeed = document.getElementById("q4-nudges-feed");
  const statusPill = document.getElementById("q4-stream-status");

  transcriptBox.innerHTML = "";
  nudgesFeed.innerHTML = "";
  statusPill.textContent = "STREAMING CHUNKS...";
  statusPill.style.background = "rgba(6,182,212,0.15)";
  statusPill.style.color = "var(--accent-cyan)";

  for (let i = 0; i < scenario.chunks.length; i++) {
    if (!isQ4Streaming) break;
    const chunk = scenario.chunks[i];

    // Call stream API
    try {
      const resp = await fetch("/api/q4/stream-chunk", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ speaker: chunk.speaker, text: chunk.text })
      });
      const data = await resp.json();

      // Render Speaker Transcript
      const bubble = document.createElement("div");
      bubble.style.padding = "0.5rem 0.75rem";
      bubble.style.borderRadius = "6px";
      bubble.style.marginBottom = "0.5rem";
      bubble.style.fontSize = "0.82rem";
      bubble.style.background = chunk.speaker === "Agent" ? "rgba(99,102,241,0.15)" : "rgba(6,182,212,0.15)";
      bubble.style.border = `1px solid ${chunk.speaker === 'Agent' ? 'rgba(99,102,241,0.3)' : 'rgba(6,182,212,0.3)'}`;

      bubble.innerHTML = `
        <div style="font-size: 0.7rem; font-weight: 700; color: ${chunk.speaker === 'Agent' ? 'var(--accent-indigo)' : 'var(--accent-cyan)'}; margin-bottom: 0.2rem;">
          [${data.chunk_id}] ${chunk.speaker} (Latency: ${data.latency.asr_ms}ms)
        </div>
        <div>"${data.transcription}"</div>
      `;
      transcriptBox.appendChild(bubble);
      transcriptBox.scrollTop = transcriptBox.scrollHeight;

      // Render Nudge if generated
      if (data.nudge) {
        const ndg = data.nudge;
        const pClass = ndg.priority.startsWith("P0") ? "p0" : (ndg.priority.startsWith("P1") ? "p1" : "p2");
        const tagClass = ndg.priority.startsWith("P0") ? "tag-p0" : (ndg.priority.startsWith("P1") ? "tag-p1" : "tag-p2");

        const nudgeEl = document.createElement("div");
        nudgeEl.className = `nudge-item ${pClass}`;
        nudgeEl.id = `ndg-${ndg.nudge_id}`;
        nudgeEl.innerHTML = `
          <div class="nudge-header">
            <span class="nudge-tag ${tagClass}">${ndg.priority} • ${ndg.category}</span>
            <span style="font-family: monospace; font-size: 0.75rem; color: var(--accent-cyan);">Latency: ${data.latency.end_to_end_ms}ms</span>
          </div>
          <div class="nudge-action">${ndg.action_text}</div>
          <div class="nudge-evidence">Context: "${ndg.evidence}"</div>
          <div style="display: flex; gap: 0.4rem; margin-top: 0.35rem;">
            <button class="btn btn-emerald" style="padding: 0.25rem 0.55rem; font-size: 0.72rem;" onclick="dismissNudge('${ndg.nudge_id}', true)">✓ Applied by Agent</button>
            <button class="btn btn-outline" style="padding: 0.25rem 0.55rem; font-size: 0.72rem;" onclick="dismissNudge('${ndg.nudge_id}', false)">✕ Dismiss</button>
          </div>
        `;
        nudgesFeed.prepend(nudgeEl);
        document.getElementById("active-nudges-count").textContent = `${nudgesFeed.children.length} ACTIVE`;
      }

      // Wait 1.8 seconds between chunks to simulate real-time speaking pace
      await new Promise(r => setTimeout(r, 1800));
    } catch (e) {
      console.error("Chunk streaming failed:", e);
    }
  }

  isQ4Streaming = false;
  statusPill.textContent = "CALL COMPLETED";
  statusPill.style.background = "rgba(16,185,129,0.15)";
  statusPill.style.color = "var(--accent-emerald)";
}

function dismissNudge(nudgeId, wasApplied) {
  const el = document.getElementById(`ndg-${nudgeId}`);
  if (el) {
    el.style.opacity = "0.5";
    el.style.pointerEvents = "none";
    el.innerHTML += `<div style="font-size: 0.72rem; color: ${wasApplied ? 'var(--accent-emerald)' : 'var(--text-muted)'}; margin-top: 0.2rem;">${wasApplied ? '✓ Action logged in CRM audit' : 'Dismissed by agent'}</div>`;
  }
}

// -------------------------------------------------------------
// INITIALIZATION
// -------------------------------------------------------------
window.addEventListener("DOMContentLoaded", () => {
  loadQ1RecordedCalls();
  loadQ2AuditTable();
  performQ2Search();
  loadQ3MarketData("ph");
  loadQ4InitialData();
});
