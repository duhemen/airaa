# airaa_watcher.py - FIXED
import time
import os
import requests
import threading
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from plyer import notification

# Impor alat
try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
    print("✅ Docling tersedia")
except ImportError:
    DOCLING_AVAILABLE = False
    print("⚠️ Docling tidak tersedia")
    DocumentConverter = None

from airaa_brain import AiraaBrain
from airaa_logger import AiraaLogger

# Import settings
try:
    from settings_loader import settings
except ImportError:
    class DummySettings:
        def get(self, key, default=None):
            return default
    settings = DummySettings()


class AiraaMultimodalWatcher(FileSystemEventHandler):
    def __init__(self):
        self.brain = AiraaBrain()
        self.logger = AiraaLogger()
        
        # Ollama dari settings
        ollama_base = settings.get('ollama.base_url', "http://localhost:11434")
        self.ollama_chat_url = f"{ollama_base}/api/generate"
        self.chat_model = settings.get('ollama.chat_model', 'qwen2.5:7b-instruct')
        self.timeout = settings.get('ollama.timeout', 60)
        
        # Watcher settings
        self.debounce_seconds = settings.get('watcher.debounce_seconds', 5)
        self.process_knowledge = settings.get('watcher.process_knownledge_files', True)
        self.audit_python = settings.get('watcher.audit_python_files', True)
        
        print("😇 AIRAA: Membuka sensor penglihatan...")
        if DOCLING_AVAILABLE and DocumentConverter:
            self.doc_converter = DocumentConverter()
        else:
            self.doc_converter = None
        
        # FIXED: Tambahkan whisper_model_path
        self.whisper_model_path = "base"
        
        # Cache proses file untuk menghindari duplicate
        self.riwayat_proses = {}
        self.proses_lock = threading.Lock()
        
        # Supported extensions dari settings
        ext_config = settings.get('watcher.supported_extensions', {})
        self.document_exts = set(ext_config.get('documents', ['.pdf', '.docx', '.xlsx', '.pptx', '.txt', '.md']))
        self.image_exts = set(ext_config.get('images', ['.jpg', '.jpeg', '.png', '.gif', '.bmp']))
        self.media_exts = set(ext_config.get('media', ['.mp3', '.mp4', '.wav', '.avi', '.mov']))
        self.code_exts = set(ext_config.get('code', ['.py', '.js', '.html', '.css', '.json', '.yaml', '.yml']))
        
        self.all_exts = self.document_exts | self.image_exts | self.media_exts | self.code_exts
        self.knowledge_exts = set(settings.get('memory.knowledge_extensions', 
                                               ['.pdf', '.docx', '.xlsx', '.pptx', '.txt', '.md', '.py', '.jpg', '.png', '.mp3', '.mp4']))
        
        # Exclude patterns
        self.exclude_patterns = settings.get('watcher.exclude_patterns', ["~$*", "*.tmp", "*.log", "*.cache"])
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # Skip temp files berdasarkan exclude patterns
        for pattern in self.exclude_patterns:
            if pattern.startswith('*'):
                if event.src_path.endswith(pattern[1:]):
                    return
            elif pattern.endswith('*'):
                if event.src_path.startswith(pattern[:-1]):
                    return
            elif pattern in event.src_path:
                return

        # Cek ekstensi
        ekstensi = os.path.splitext(event.src_path)[1].lower()
        if ekstensi not in self.all_exts:
            return
            
        waktu_sekarang = time.time()
        path_berkas = event.src_path
        
        # Debounce: skip jika terlalu cepat
        with self.proses_lock:
            if path_berkas in self.riwayat_proses:
                if waktu_sekarang - self.riwayat_proses[path_berkas] < self.debounce_seconds:
                    return
            self.riwayat_proses[path_berkas] = waktu_sekarang
            
        # Log perubahan
        self.logger.catat_interaksi("file_change", f"Perubahan terdeteksi: {os.path.basename(path_berkas)}")
        
        # Proses di background
        threading.Thread(target=self.proses_berkas, args=(path_berkas,), daemon=True).start()

    def extract_pdf_text(self, file_path):
        """Ekstrak teks dari PDF dengan berbagai metode"""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages[:20]:
                    text += page.extract_text() + "\n"
            return text
        except:
            pass
    
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages[:20]:
                    text += page.extract_text() + "\n"
            return text
        except:
            pass
    
        # Fallback: Docling
        try:
            if DOCLING_AVAILABLE and self.doc_converter:
                result = self.doc_converter.convert(file_path)
                return result.document.export_to_markdown()
        except:
            pass
        return ""

    def proses_berkas(self, file_path):
        """Proses file dengan berbagai metode"""
        nama_berkas = os.path.basename(file_path)
        ekstensi = os.path.splitext(nama_berkas)[1].lower()
        konten_teks = ""
        
        # Cek apakah file di folder knowledge
        is_knowledge = "knowledge" in file_path.lower()
        
        try:
            # 1. Dokumen & Gambar via Docling
            if ekstensi in (self.document_exts | self.image_exts):
                if self.doc_converter:
                    print(f"📖 AIRAA membaca: {nama_berkas}")
                    result = self.doc_converter.convert(file_path)
                    konten_teks = result.document.export_to_markdown()
                else:
                    # Fallback untuk PDF
                    if ekstensi == '.pdf':
                        konten_teks = self.extract_pdf_text(file_path)
                    else:
                        konten_teks = f"[DOCUMENT] {nama_berkas} - Docling tidak tersedia"
                    
            # 2. Media audio/video via Whisper
            elif ekstensi in self.media_exts:
                print(f"🎙️ AIRAA mentranskrip: {nama_berkas}")
                try:
                    from faster_whisper import WhisperModel
                    model = WhisperModel(self.whisper_model_path, device="cpu", compute_type="int8")
                    segments, info = model.transcribe(file_path, beam_size=5, language="id")
                    konten_teks = " ".join([segment.text for segment in segments])
                except ImportError:
                    konten_teks = f"[AUDIO FILE] {nama_berkas} - Butuh faster-whisper untuk transkripsi"
                except Exception as e:
                    konten_teks = f"[AUDIO FILE] {nama_berkas} - Error: {e}"
                    
            # 3. Text files
            elif ekstensi in self.code_exts:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        konten_teks = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            konten_teks = f.read()
                    except:
                        konten_teks = f"[BINARY FILE] {nama_berkas}"
            
            # Proses berdasarkan lokasi
            if is_knowledge and self.process_knowledge and konten_teks.strip():
                # Simpan ke memori
                self.brain.simpan_ilmu_baru(nama_berkas, konten_teks)
                self.logger.catat_interaksi("belajar_file", f"Belajar dari {nama_berkas}", {
                    "size": len(konten_teks),
                    "type": ekstensi
                })
                print(f"✨ AIRAA belajar dari '{nama_berkas}'")
                
                # Notifikasi
                try:
                    notification.notify(
                        title="😇 AIRAA Ilmu Baru Terpatri!",
                        message=f"Emen, aku sudah selesai mempelajari '{nama_berkas}'",
                        app_name="AIRAA Core",
                        timeout=5
                    )
                except:
                    pass
                
            elif ekstensi == '.py' and not is_knowledge and self.audit_python:
                # Audit kode Python
                self.audit_kode_python(file_path, nama_berkas, konten_teks)
                
        except Exception as e:
            print(f"❌ Gagal proses {nama_berkas}: {e}")
            self.logger.catat_interaksi("error", f"Gagal proses {nama_berkas}: {str(e)}")

    def audit_kode_python(self, file_path, nama_berkas, konten=None):
        """Audit kode Python dengan AI"""
        if konten is None:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    konten = f.read()
            except:
                return

        # Cek apakah features code_audit diaktifkan
        if not settings.get('features.code_audit', True):
            return

        prompt = f"""
        Kamu adalah AIRAA, asisten coding malaikat untuk Emen.
        
        Periksa file Python berikut: {nama_berkas}
        
        ANALISIS:
        1. ✅ Error/Bug potensial
        2. ⚡ Optimasi performa
        3. 🛡️ Security issues
        4. 📝 Best practices
        
        Format jawaban:
        - Jika AMAN: cukup "✅ AMAN - Kode sudah baik!"
        - Jika perlu perbaikan: jelaskan dengan singkat (maks 100 kata)
        
        Kode:
        {konten[:2000]}
        """

        payload = {
            "model": self.chat_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": settings.get('llm.temperature', 0.7),
                "top_p": settings.get('llm.top_p', 0.9),
                "max_tokens": settings.get('llm.max_tokens', 500)
            }
        }

        try:
            res = requests.post(self.ollama_chat_url, json=payload, timeout=self.timeout)
            analisis = res.json()['response'].strip()
            
            if "AMAN" not in analisis:
                print(f"😇 AIRAA: Saran untuk {nama_berkas}:\n{analisis}\n")
                self.logger.catat_interaksi("code_audit", f"Saran untuk {nama_berkas}", {
                    "saran": analisis[:200]
                })
                
                # Notifikasi untuk kode audit
                try:
                    notification.notify(
                        title=f"⚠️ AIRAA Koreksi: {nama_berkas}",
                        message=analisis[:250],
                        app_name="AIRAA Core",
                        timeout=8
                    )
                except:
                    pass
            else:
                print(f"✅ {nama_berkas} - AMAN")
                
        except Exception as e:
            print(f"❌ Gagal audit {nama_berkas}: {e}")


def jalankan_pemantau():
    """Jalankan file watcher"""
    watch_path = settings.get('watcher.watch_path', "C:\\airaa")
    recursive = settings.get('watcher.recursive', True)
    scan_interval = settings.get('watcher.scan_interval', 2)
    
    event_handler = AiraaMultimodalWatcher()
    observer = Observer()
    observer.schedule(event_handler, path=watch_path, recursive=recursive)
    observer.start()
    
    print(f"📡 AIRAA Pemantau aktif! Mengawasi: {watch_path}")
    
    try:
        while True:
            time.sleep(scan_interval)
    except KeyboardInterrupt:
        observer.stop()
        print("\n😇 AIRAA Pemantau dinonaktifkan.")
    observer.join()


if __name__ == "__main__":
    jalankan_pemantau()