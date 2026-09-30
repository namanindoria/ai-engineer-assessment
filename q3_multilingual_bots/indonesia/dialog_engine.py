"""
Indonesia Multifinance Dialogue Engine for Consumer Finance.
Handles formal and colloquial Bahasa Indonesia, finance loanwords (tenor, DP, cicilan),
regional East Java accent nuance (nggih, monggo), and pure Indonesian escalation.
"""

import re
from typing import Dict, Any, List, Optional


class IndonesiaConsumerFinanceBot:
    """
    Simulates a localized Consumer Finance & Installment Reminder Voice Bot in Indonesia.
    Handles colloquial markers (nih, dong, kok), regional Javanese loan speech (nggih, monggo),
    and maintains cultural politeness (Bapak/Ibu/Mas) throughout.
    """

    def __init__(self, customer_name: Optional[str] = "Pak Budi"):
        self.customer_name = customer_name or "Pak Budi"
        self.current_state = "INIT"
        self.cicilan_nominal = "Rp 1.250.000"
        self.tenor_months = 24
        self.jatuh_tempo_date = "Tanggal 5 tiap bulan"
        self.transcript: List[Dict[str, str]] = []

    def respond(self, user_utterance: str) -> Dict[str, Any]:
        """Processes customer utterance in colloquial/regional Bahasa Indonesia."""
        self.transcript.append({"speaker": "Customer", "text": user_utterance})
        u_lower = user_utterance.lower()

        # Dynamic honorific
        name = self.customer_name

        # Check for Human Escalation intent
        if any(w in u_lower for w in ["bicara sama manusia", "petugas", "manajer", "operator", "customer service", "orang asli", "hubungkan"]):
            self.current_state = "ESCALATED"
            reply = (
                f"Baik, {name}. Kami sangat memahami kebutuhan {name} untuk berbicara langsung. "
                "Panggilan ini akan segera saya sambungkan langsung ke Petugas Layanan Pelanggan (Customer Service) "
                "Mega Finansial cabang terdekat. Mohon ditunggu sebentar nggih, jangan ditutup teleponnya."
            )
            self.transcript.append({"speaker": "Mega (Bot)", "text": reply})
            return {
                "reply": reply,
                "state": "ESCALATED",
                "escalated": True,
                "action": "TRANSFER_TO_HUMAN_COLLECTOR"
            }

        # Check for gratitude / closing statement
        if any(w in u_lower for w in ["matur nuwun", "terima kasih", "makasih", "sip mbak", "sampun", "lunas nanti"]):
            reply = (
                f"Sami-sami / sama-sama {name}, matur nuwun kembali. Semoga urusannya selalu lancar dan rezekinya berkah. "
                "Selamat beraktivitas kembali nggih, salam sehat selalu dari Mega Finansial."
            )
            self.transcript.append({"speaker": "Mega (Bot)", "text": reply})
            return {
                "reply": reply,
                "state": "COMPLETED",
                "escalated": False,
                "action": "CALL_CLOSED"
            }

        # Check for Objection: Late fee / Denda objection with regional accent
        if any(w in u_lower for w in ["denda", "kemahalan", "keberatan", "sakit", "rumah sakit", "keringanan"]):
            reply = (
                f"Nggih, matur nuwun infonya {name}, kami sangat memahami situasi darurat yang dialami. "
                "Mengenai denda keterlambatan, sistem kami memang menghitung denda harian sesuai aturan OJK. "
                f"Namun karena {name} memiliki riwayat pembayaran angsuran yang baik sebelumnya, kami bisa bantu "
                "ajukan permohonan keringanan denda atau restrukturisasi cicilan ke tim analis pembiayaan kami."
            )
            self.transcript.append({"speaker": "Mega (Bot)", "text": reply})
            return {
                "reply": reply,
                "state": "OBJECTION_HANDLED",
                "escalated": False,
                "action": "SUBMIT_WAIVER_REQUEST"
            }

        # Check for Payment Channel (Indomaret / Alfamart / Virtual Account)
        if any(w in u_lower for w in ["bayar di mana", "indomaret", "bca", "transfer", "virtual account", "cara bayar"]):
            reply = (
                f"Pembayaran angsuran sangat mudah kok, {name}. Bisa langsung lewat Virtual Account BCA, Mandiri, "
                "atau tinggal tunjukkan nomor kontrak pembiayaan di kasir Indomaret maupun Alfamart terdekat. "
                "Struk pembayaran resmi akan langsung terbit dan cicilan langsung tercatat lunas real-time."
            )
            self.transcript.append({"speaker": "Mega (Bot)", "text": reply})
            return {
                "reply": reply,
                "state": "PAYMENT_METHOD_EXPLAINED",
                "escalated": False,
                "action": "SEND_VA_SMS"
            }

        # Check for DP / Tenor / Pembiayaan Baru
        if any(w in u_lower for w in ["dp", "tenor", "ambil lagi", "tambah pinjaman", "kredit baru"]):
            reply = (
                f"Kabar gembira, {name}! Untuk pelanggan setia seperti {name}, kami ada promo DP ringan mulai 10% "
                "dengan pilihan tenor panjang sampai 36 bulan untuk pembiayaan motor baru atau pinjaman dana multiguna. "
                "Proses verifikasinya cepat tanpa survei ulang."
            )
            self.transcript.append({"speaker": "Mega (Bot)", "text": reply})
            return {
                "reply": reply,
                "state": "CROSS_SELL_OFFERED",
                "escalated": False,
                "action": "LOG_CROSS_SELL_INTEREST"
            }

        # Default Greeting / Due Date Reminder
        if self.current_state == "INIT":
            self.current_state = "AWAITING_INPUT"
            reply = (
                f"Halo, sugeng siang / selamat siang dengan {name}? Saya Mega, asisten virtual dari Mega Finansial. "
                "Hanya ingin menginformasikan bahwa cicilan motor untuk nomor kontrak 88201 akan jatuh tempo pada "
                f"tanggal 5 lusa sebesar Rp 1.250.000. Apakah ada yang bisa kami bantu terkait pembayaran angsuran bulan ini, {name}?"
            )
        else:
            reply = (
                f"Baik, {name}, terima kasih atas kerjasamanya. Semoga urusannya selalu dilancarkan dan sehat selalu. "
                f"Jika tidak ada pertanyaan lain, selamat beraktivitas kembali nggih, {name}."
            )

        self.transcript.append({"speaker": "Mega (Bot)", "text": reply})
        return {
            "reply": reply,
            "state": self.current_state,
            "escalated": False,
            "action": None
        }
