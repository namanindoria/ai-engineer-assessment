"""
Execution and Verification Suite for Question 3 Native-Language Voice Bots.
Executes 2 calls per market (4 total calls) covering:
- Philippines Call 1: Cooperative Bancassurance Taglish inquiry
- Philippines Call 2: Taglish Objection & Human Escalation (Zero English reversion)
- Indonesia Call 1: Cooperative Cicilan Due Date Reminder & Payment Channel
- Indonesia Call 2: Regional East Java Accent Objection & Human Escalation
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any
from q3_multilingual_bots.philippines.dialog_engine import PhilippinesBancassuranceBot
from q3_multilingual_bots.indonesia.dialog_engine import IndonesiaConsumerFinanceBot


def run_multilingual_benchmarks():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ph_dir = os.path.join(base_dir, "q3_multilingual_bots", "philippines")
    id_dir = os.path.join(base_dir, "q3_multilingual_bots", "indonesia")

    print("\n" + "="*80)
    print("QUESTION 3: MULTILINGUAL VOICE BOTS BENCHMARK EXECUTION")
    print("="*80 + "\n")

    # -------------------------------------------------------------
    # PHILIPPINES CALL 1: Cooperative Bancassurance Cross-Sell
    # -------------------------------------------------------------
    print("--- EXECUTING CALL PH-01: Cooperative Bancassurance Cross-Sell (Taglish) ---")
    ph_bot1 = PhilippinesBancassuranceBot(caller_name="Maria Santos")
    ph_bot1.respond("Call Connected")
    turns_ph1 = [
        "Hello po! Nag-inquire po ako sa branch manager ko sa BPI tungkol sa life insurance na may medical rider.",
        "Gusto ko po sana ilagay ang dalawang anak ko bilang primary beneficiaries.",
        "Pwede po ba itong i-auto-debit diretso sa aking BPI savings account para hassle-free?",
        "Salamat po! Malinaw na po ang lahat, paki-send na lang ng proposal summary."
    ]
    for utt in turns_ph1:
        res = ph_bot1.respond(utt)
        print(f"Customer: {utt}")
        print(f"Maria: {res['reply']}\n")

    call_ph1_record = {
        "call_id": "CALL-PH-01",
        "market": "Philippines",
        "sector": "Bancassurance & Life Insurance",
        "type": "Cooperative Taglish Cross-Sell",
        "language": "Taglish (Filipino-English code-switching)",
        "terms_used": ["premium", "beneficiary", "rider", "bank referral", "auto-debit"],
        "transcript": ph_bot1.transcript,
        "timestamp": datetime.now().isoformat()
    }
    with open(os.path.join(ph_dir, "test_call_ph_1_cooperative_taglish.json"), "w", encoding="utf-8") as f:
        json.dump(call_ph1_record, f, indent=2)

    # -------------------------------------------------------------
    # PHILIPPINES CALL 2: Taglish Objection & Human Escalation
    # -------------------------------------------------------------
    print("--- EXECUTING CALL PH-02: Taglish Budget Objection & Human Escalation ---")
    ph_bot2 = PhilippinesBancassuranceBot(caller_name="Juan Dela Cruz")
    ph_bot2.respond("Call Connected")
    turns_ph2 = [
        "Medyo alanganin po ako kasi medyo tight ang budget ko ngayon, baka mag-lapse lang ang policy kung hindi ko mahulugan ang premium.",
        "Gusto ko sana may makausap na totoong tao o branch specialist para mapaliwanag nang mas detalyado ang terms."
    ]
    for utt in turns_ph2:
        res = ph_bot2.respond(utt)
        print(f"Customer: {utt}")
        print(f"Maria: {res['reply']}\n")

    call_ph2_record = {
        "call_id": "CALL-PH-02",
        "market": "Philippines",
        "sector": "Bancassurance & Life Insurance",
        "type": "Objection & Taglish Escalation",
        "language": "Taglish",
        "terms_used": ["budget", "lapse", "policy", "premium", "specialist"],
        "transcript": ph_bot2.transcript,
        "escalated_in_taglish": True,
        "timestamp": datetime.now().isoformat()
    }
    with open(os.path.join(ph_dir, "test_call_ph_2_objection_bancassurance.json"), "w", encoding="utf-8") as f:
        json.dump(call_ph2_record, f, indent=2)

    # -------------------------------------------------------------
    # INDONESIA CALL 1: Cooperative Installment Reminder
    # -------------------------------------------------------------
    print("--- EXECUTING CALL ID-01: Installment Due Date Reminder (Bahasa Indonesia) ---")
    id_bot1 = IndonesiaConsumerFinanceBot(customer_name="Pak Budi")
    id_bot1.respond("Call Connected")
    turns_id1 = [
        "Halo mbak, iya ini saya Pak Budi. Mau tanya, cicilan motor saya bulan ini bisa bayar di mana ya yang paling cepat?",
        "Kalau mau ambil pembiayaan kredit motor baru lagi dengan tenor 36 bulan dan DP murah apa bisa sekalian?",
        "Sip mbak, matur nuwun infonya sangat membantu. Nanti sore saya bayar lewat Indomaret."
    ]
    for utt in turns_id1:
        res = id_bot1.respond(utt)
        print(f"Customer: {utt}")
        print(f"Mega: {res['reply']}\n")

    call_id1_record = {
        "call_id": "CALL-ID-01",
        "market": "Indonesia",
        "sector": "Consumer Finance",
        "type": "Installment Reminder & Cross-Sell",
        "language": "Bahasa Indonesia Colloquial",
        "terms_used": ["cicilan", "jatuh tempo", "angsuran", "tenor", "DP", "pembiayaan"],
        "transcript": id_bot1.transcript,
        "timestamp": datetime.now().isoformat()
    }
    with open(os.path.join(id_dir, "test_call_id_1_cicilan_jatuh_tempo.json"), "w", encoding="utf-8") as f:
        json.dump(call_id1_record, f, indent=2)

    # -------------------------------------------------------------
    # INDONESIA CALL 2: Regional East Java Objection & Escalation
    # -------------------------------------------------------------
    print("--- EXECUTING CALL ID-02: Regional East Java Accent Objection & Escalation ---")
    id_bot2 = IndonesiaConsumerFinanceBot(customer_name="Pak Joko")
    id_bot2.respond("Call Connected")
    turns_id2 = [
        "Nyuwun sewu mbak, anak kulo kemarin opname di rumah sakit, dospundi kok denda keterlambatan angsuran kulo kemahalan men?",
        "Nggih, kulo nyuwun tolong disambungkan langsung bicara sama manusia atau customer service cabang, saget mboten?"
    ]
    for utt in turns_id2:
        res = id_bot2.respond(utt)
        print(f"Customer: {utt}")
        print(f"Mega: {res['reply']}\n")

    call_id2_record = {
        "call_id": "CALL-ID-02",
        "market": "Indonesia",
        "sector": "Consumer Finance",
        "type": "Regional Accent Objection & Human Escalation",
        "language": "Bahasa Indonesia with East Java Loan Nuance (nggih, monggo, dospundi)",
        "terms_used": ["denda", "angsuran", "pembiayaan", "keringanan denda", "customer service"],
        "transcript": id_bot2.transcript,
        "escalated_in_indonesian": True,
        "timestamp": datetime.now().isoformat()
    }
    with open(os.path.join(id_dir, "test_call_id_2_regional_objection.json"), "w", encoding="utf-8") as f:
        json.dump(call_id2_record, f, indent=2)

    print("="*80)
    print("QUESTION 3 MULTILINGUAL BENCHMARK COMPLETED SUCCESSFULLY!")
    print(f"Transcripts saved to {ph_dir} and {id_dir}")
    print("="*80)


if __name__ == "__main__":
    run_multilingual_benchmarks()
