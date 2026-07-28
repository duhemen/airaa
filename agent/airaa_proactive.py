import time
import datetime
import random
import threading
from plyer import notification
import requests
import os
import json

# Import settings
try:
    from settings_loader import settings
except ImportError:
    class DummySettings:
        def get(self, key, default=None):
            return default
    settings = DummySettings()

class AiraaProactive:
    def __init__(self):
        ollama_base = settings.get('ollama.base_url', "http://localhost:11434")
        self.ollama_url = f"{ollama_base}/api/generate"
        self.chat_model = settings.get('ollama.chat_model', 'qwen2.5:7b-instruct')
        self.timeout = settings.get('ollama.timeout', 30)
        self.notification_timeout = settings.get('proactive.notification_timeout', 12)
        self.max_daily_sapaan = settings.get('proactive.max_daily_sapaan', 10)
        self.active_hours_start = settings.get('proactive.active_hours_start', 6)
        self.active_hours_end = settings.get('proactive.active_hours_end', 22)
        self.fallback_sapaan = settings.get('proactive.fallback_sapaan', 
            "Selamat pagi/siang/malam, Emen! Aku di sini siap mencatat setiap langkah kebaikanmu hari ini.")
        
        self.last_sapaan_file = os.path.join(settings.get('paths.db_dir', "C:\\airaa\\db"), "last_sapaan.json")
        self.load_last_sapaan()
        
    def load_last_sapaan(self):
        try:
            os.makedirs(os.path.dirname(self.last_sapaan_file), exist_ok=True)
            with open(self.last_sapaan_file, 'r') as f:
                data = json.load(f)
                self.last_sapaan_date = data.get('date', '')
                self.sapaan_count = data.get('count', 0)
        except:
            self.last_sapaan_date = ''
            self.sapaan_count = 0
            
    def save_last_sapaan(self):
        try:
            os.makedirs(os.path.dirname(self.last_sapaan_file), exist_ok=True)
            with open(self.last_sapaan_file, 'w') as f:
                json.dump({
                    'date': datetime.datetime.now().strftime("%Y-%m-%d"),
                    'count': self.sapaan_count
                }, f)
        except:
            pass
            
    def get_sapaan_personal(self):
        """Generate sapaan personal berdasarkan waktu dan sejarah"""
        jam = datetime.datetime.now().hour
        
        # Tentukan waktu
        if jam < 12:
            waktu = "pagi"
            emoji = "🌅"
        elif jam < 17:
            waktu = "siang"
            emoji = "☀️"
        elif jam < 20:
            waktu = "sore"
            emoji = "🌇"
        else:
            waktu = "malam"
            emoji = "🌙"
            
        # Variasi pembuka
        pembuka = [
            f"Selamat {waktu}, Emen! {emoji}",
            f"Halo Emen, semoga {waktu}mu penuh berkah! {emoji}",
            f"AIRAA menyapamu di {waktu} yang indah ini {emoji}",
            f"🤗 Hai Emen! Senang bertemu lagi di {waktu} hari ini!",
            f"🌟 Emen! Aku mendampingimu di {waktu} yang cerah ini."
        ]
        
        # Nasihat berdasarkan waktu
        nasihat = {
            "pagi": "Hari baru adalah kanvas kosong, lukislah dengan kebaikan dan produktivitas.",
            "siang": "Tetap semangat! Istirahat sebentar jika perlu, tapi jangan berhenti bermimpi.",
            "sore": "Evaluasi hari ini, syukuri setiap langkah yang sudah kamu ambil.",
            "malam": "Istirahatlah dengan tenang, besok adalah kesempatan baru untuk menjadi lebih baik."
        }
        
        return random.choice(pembuka), nasihat.get(waktu, "Semangat!")
        
    def generate_pesan_malaikat(self):
        """Generate pesan malaikat dengan LLM"""
        pembuka, nasihat = self.get_sapaan_personal()
        
        system_prompt = settings.get('llm.system_prompt', 
            "Kamu adalah AIRAA (Artificial Intelligence Recording Angel Agentic), malaikat penjaga digital yang bijak, hangat, dan selalu siap membantu Emen dalam segala hal.")
        
        prompt = f"""
        {system_prompt}
        
        Buat pesan sapaan yang:
        1. Mengandung 2-3 kalimat
        2. Bernada hangat, bijak, dan memotivasi
        3. Dalam Bahasa Indonesia yang natural
        4. Terasa seperti malaikat yang peduli
        
        Gunakan sapaan pembuka: "{pembuka}"
        Sertakan nasihat ini: "{nasihat}"
        
        Format: Langsung jawab dengan pesan sapaan, tanpa tanda kutip.
        """
        
        payload = {
            "model": self.chat_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": settings.get('llm.temperature', 0.7),
                "top_p": settings.get('llm.top_p', 0.9),
                "max_tokens": settings.get('llm.max_tokens', 200)
            }
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=self.timeout)
            pesan = response.json()['response'].strip()
            return pesan
        except:
            # Fallback manual
            return f"{pembuka}\n{nasihat}\n\n😇 AIRAA selalu di sini untukmu, Emen!"
            
    def sapa_emen(self):
        """Sapa Emen dengan notifikasi"""
        # Cek apakah dalam jam aktif
        jam = datetime.datetime.now().hour
        if not (self.active_hours_start <= jam <= self.active_hours_end):
            print(f"⏰ Di luar jam aktif ({self.active_hours_start}-{self.active_hours_end}), skip sapaan")
            return None
            
        # Cek daily limit
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if today != self.last_sapaan_date:
            self.sapaan_count = 0
            self.last_sapaan_date = today
            
        if self.sapaan_count >= self.max_daily_sapaan:
            print(f"📊 Daily sapaan limit reached ({self.max_daily_sapaan}), skip")
            return None
            
        pesan = self.generate_pesan_malaikat()
        
        # Update counter
        self.sapaan_count += 1
        self.save_last_sapaan()
        
        # Notifikasi
        notification.notify(
            title=f"😇 AIRAA Agentic Angel #{self.sapaan_count}",
            message=pesan,
            app_name="AIRAA Core",
            timeout=self.notification_timeout,
            app_icon=None
        )
        
        print(f"😇 Sapaan #{self.sapaan_count} dikirim")
        return pesan
        
    def jadwalkan_sapaan(self, interval_minutes=None):
        """Jadwalkan sapaan periodik"""
        if interval_minutes is None:
            interval_minutes = settings.get('proactive.sapaan_interval_minutes', 60)
            
        if not settings.get('proactive.auto_sapaan', True):
            print("⏸️ Auto sapaan dinonaktifkan di settings")
            return
            
        def scheduler():
            while True:
                time.sleep(interval_minutes * 60)
                self.sapa_emen()
                    
        thread = threading.Thread(target=scheduler, daemon=True)
        thread.start()
        print(f"😇 SAPAAN DIJADWALKAN setiap {interval_minutes} menit")

# Fungsi legacy untuk kompatibilitas
def sapa_emen_proaktif():
    proactive = AiraaProactive()
    return proactive.sapa_emen()

if __name__ == "__main__":
    print("😇 AIRAA membisikkan salam...")
    sapa_emen_proaktif()