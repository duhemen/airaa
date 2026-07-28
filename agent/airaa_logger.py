import json
import datetime
import os
import threading
from collections import deque

class AiraaLogger:
    def __init__(self, log_dir="C:\\airaa\\logs", max_entries_per_file=1000):
        self.log_dir = log_dir
        self.max_entries = max_entries_per_file
        os.makedirs(log_dir, exist_ok=True)
        
        # Cache untuk performa
        self.cache = deque(maxlen=100)
        self.lock = threading.Lock()
        
    def catat_interaksi(self, jenis, konten, metadata=None):
        """Catat interaksi ke log"""
        tanggal = datetime.datetime.now().strftime("%Y-%m-%d")
        file_log = os.path.join(self.log_dir, f"interaksi_{tanggal}.json")
        
        entry = {
            "waktu": datetime.datetime.now().isoformat(),
            "jenis": jenis,
            "konten": konten,
            "metadata": metadata or {}
        }
        
        # Simpan ke cache
        with self.lock:
            self.cache.append(entry)
            
        # Simpan ke file
        try:
            with self.lock:
                # Baca existing
                try:
                    with open(file_log, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except:
                    data = []
                
                # Append
                data.append(entry)
                
                # Limit entries
                if len(data) > self.max_entries:
                    data = data[-self.max_entries:]
                
                # Write
                with open(file_log, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    
        except Exception as e:
            print(f"❌ Gagal menulis log: {e}")
            
    def baca_log_terbaru(self, tanggal=None, limit=100, jenis=None):
        """Baca log terbaru dengan filter"""
        if tanggal is None:
            tanggal = datetime.datetime.now().strftime("%Y-%m-%d")
            
        file_log = os.path.join(self.log_dir, f"interaksi_{tanggal}.json")
        
        try:
            with open(file_log, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Filter jenis
            if jenis:
                data = [d for d in data if d.get('jenis') == jenis]
                
            # Return terbaru
            return data[-limit:] if data else []
        except:
            return []
            
    def get_statistik_harian(self, tanggal=None):
        """Dapatkan statistik interaksi harian"""
        if tanggal is None:
            tanggal = datetime.datetime.now().strftime("%Y-%m-%d")
            
        entries = self.baca_log_terbaru(tanggal, limit=10000)
        
        stat = {
            "total": len(entries),
            "jenis": {},
            "topik": []
        }
        
        for entry in entries:
            jenis = entry.get('jenis', 'unknown')
            stat['jenis'][jenis] = stat['jenis'].get(jenis, 0) + 1
            
        return stat

if __name__ == "__main__":
    logger = AiraaLogger()
    logger.catat_interaksi("test", "Logging test berhasil")
    print("✅ Logger berhasil diuji")