import json
import datetime
import os
from collections import Counter
import re

# Import settings
try:
    from settings_loader import settings
except ImportError:
    class DummySettings:
        def get(self, key, default=None):
            return default
    settings = DummySettings()

class AiraaAnalytics:
    def __init__(self, log_dir=None, db_dir=None):
        if log_dir is None:
            log_dir = settings.get('paths.logs_dir', "C:\\airaa\\logs")
        if db_dir is None:
            db_dir = settings.get('paths.db_dir', "C:\\airaa\\db")
            
        self.log_dir = log_dir
        self.db_dir = db_dir
        self.retention_days = settings.get('analytics.analytics_retention_days', 30)
        self.track_interactions = settings.get('analytics.track_interactions', True)
        self.track_file_changes = settings.get('analytics.track_file_changes', True)
        
        # Buat direktori jika belum ada
        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(db_dir, exist_ok=True)
        
    def get_statistik(self, hari=7):
        """Dapatkan statistik keseluruhan"""
        if not settings.get('analytics.enabled', True):
            return {"status": "Analytics disabled"}
            
        stats = {
            "total_interaksi": 0,
            "total_memori": 0,
            "belajar_hari_ini": 0,
            "pertanyaan_hari_ini": 0,
            "pengingat_aktif": 0,
            "topik_favorit": "Belum ada data",
            "aktivitas_mingguan": "Belum ada data"
        }
        
        # Hitung interaksi dari log
        if self.track_interactions:
            try:
                total_interaksi = 0
                belajar_hari_ini = 0
                pertanyaan_hari_ini = 0
                jenis_counter = Counter()
                
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                
                # Baca log 7 hari terakhir
                for i in range(hari):
                    tanggal = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
                    file_log = os.path.join(self.log_dir, f"interaksi_{tanggal}.json")
                    
                    try:
                        with open(file_log, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        for entry in data:
                            total_interaksi += 1
                            jenis = entry.get('jenis', 'unknown')
                            jenis_counter[jenis] += 1
                            
                            if tanggal == today:
                                if jenis == 'belajar_file':
                                    belajar_hari_ini += 1
                                elif jenis == 'tanya_memori':
                                    pertanyaan_hari_ini += 1
                                    
                    except:
                        pass
                        
                stats["total_interaksi"] = total_interaksi
                stats["belajar_hari_ini"] = belajar_hari_ini
                stats["pertanyaan_hari_ini"] = pertanyaan_hari_ini
                
                # Topik favorit dari metadata
                if total_interaksi > 0:
                    # Cari topik dari tanya_memori
                    topik_list = []
                    for i in range(hari):
                        tanggal = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
                        file_log = os.path.join(self.log_dir, f"interaksi_{tanggal}.json")
                        try:
                            with open(file_log, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                for entry in data:
                                    if entry.get('jenis') == 'tanya_memori':
                                        # Ekstrak kata kunci
                                        konten = entry.get('konten', '')
                                        words = re.findall(r'\w+', konten.lower())
                                        topik_list.extend([w for w in words if len(w) > 3])
                        except:
                            pass
                            
                    if topik_list:
                        top_3 = Counter(topik_list).most_common(3)
                        stats["topik_favorit"] = ", ".join([f"{t[0]} ({t[1]}x)" for t in top_3])
                        
            except Exception as e:
                print(f"❌ Error analytics: {e}")
                
        # Jumlah memori dari ChromaDB
        try:
            import chromadb
            client = chromadb.PersistentClient(path=self.db_dir)
            collection = client.get_or_create_collection(name="airaa_memory")
            stats["total_memori"] = collection.count()
        except:
            stats["total_memori"] = 0
            
        # Pengingat aktif
        try:
            with open(os.path.join(self.db_dir, "reminders.json"), 'r') as f:
                reminders = json.load(f)
                stats["pengingat_aktif"] = len([r for r in reminders if r.get('aktif', True)])
        except:
            stats["pengingat_aktif"] = 0
            
        # Aktivitas mingguan (7 hari terakhir)
        if self.track_interactions:
            aktivitas = []
            for i in range(hari):
                tanggal = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
                file_log = os.path.join(self.log_dir, f"interaksi_{tanggal}.json")
                count = 0
                try:
                    with open(file_log, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        count = len(data)
                except:
                    pass
                hari_nama = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%a")
                aktivitas.append(f"{hari_nama}: {count}")
                
            stats["aktivitas_mingguan"] = "\n".join(aktivitas)
            
        return stats
        
    def get_analisis_harian(self):
        """Dapatkan analisis harian dalam bentuk teks"""
        stats = self.get_statistik()
        
        if "status" in stats:
            return "📊 Analytics dinonaktifkan di settings."
            
        text = f"""
📊 ANALISIS AKTIVITAS HARI INI
{'='*40}

📚 Total pengetahuan: {stats['total_memori']} dokumen
💬 Total interaksi: {stats['total_interaksi']} kali
🔄 Belajar hari ini: {stats['belajar_hari_ini']} file
❓ Pertanyaan hari ini: {stats['pertanyaan_hari_ini']} kali
⏰ Pengingat aktif: {stats['pengingat_aktif']}
🎯 Topik favorit: {stats['topik_favorit']}

📈 Aktivitas 7 hari terakhir:
{stats['aktivitas_mingguan']}

😇 AIRAA siap membantu Emen!
"""
        return text

if __name__ == "__main__":
    analytics = AiraaAnalytics()
    print(analytics.get_analisis_harian())