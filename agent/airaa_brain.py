# airaa_brain.py - WITH FOCUS MODE SUPPORT
import os
import requests
import chromadb
import hashlib
import json
from datetime import datetime

# Import settings
try:
    from settings_loader import settings
except ImportError:
    class DummySettings:
        def get(self, key, default=None):
            return default
    settings = DummySettings()


class AiraaBrain:
    """Otak AIRAA - RAG + Memory + Focus Mode"""
    
    # ============================================
    # CLASS VARIABLES (Shared across instances)
    # ============================================
    _focus_mode = False  # Flag untuk fokus mode
    _original_settings = {}  # Backup settings saat fokus
    
    def __init__(self, db_path=None):
        """Inisialisasi otak AIRAA dengan cache dan RAG"""
        
        # Gunakan settings untuk path
        if db_path is None:
            db_path = settings.get('paths.db_dir', "C:\\airaa\\db")
            
        self.db_path = db_path
        os.makedirs(db_path, exist_ok=True)
        
        # ChromaDB Client
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection(name="airaa_memory")
        
        # Ollama endpoints dari settings
        ollama_base = settings.get('ollama.base_url', "http://localhost:11434")
        self.ollama_emb_url = f"{ollama_base}/api/embeddings"
        self.ollama_gen_url = f"{ollama_base}/api/generate"
        
        # Model dari settings
        self.embedding_model = settings.get('ollama.embedding_model', 'nomic-embed-text')
        self.chat_model = settings.get('ollama.chat_model', 'qwen2.5:7b-instruct')
        self.timeout = settings.get('ollama.timeout', 60)
        
        # Cache embedding untuk performa
        self.cache_enabled = settings.get('memory.cache_enabled', True)
        self.cache_embedding = {}
        self.cache_file = os.path.join(db_path, "embedding_cache.json")
        self.muat_cache()
        
        # Max document length dari settings
        self.max_doc_length = settings.get('memory.max_document_length', 3000)
        
        # Track pengetahuan
        self.knowledge_path = settings.get('paths.knowledge_dir', "C:\\airaa\\knowledge")
        os.makedirs(self.knowledge_path, exist_ok=True)
        
        print("🧠 Otak AIRAA siap beroperasi!")
    
    # ============================================
    # FOKUS MODE METHODS
    # ============================================
    
    @classmethod
    def set_focus_mode(cls, enabled: bool):
        """
        Set mode fokus untuk semua instance AiraaBrain.
        Saat fokus mode ON, resource dimatikan/dikurangi untuk performa maksimal.
        """
        cls._focus_mode = enabled
        
        if enabled:
            print("🧠 Fokus Mode: ON - Optimasi resource untuk jawaban cepat")
            # Simpan settings original
            cls._original_settings = {
                'cache_enabled': settings.get('memory.cache_enabled', True),
                'max_doc_length': settings.get('memory.max_document_length', 3000),
                'timeout': settings.get('ollama.timeout', 60)
            }
            # Optimasi untuk fokus mode
            # - Gunakan cache lebih agresif
            # - Kurangi timeout untuk response cepat
            # - Batasi panjang dokumen untuk kecepatan
            settings.set('memory.cache_enabled', True)
            settings.set('memory.max_document_length', 1500)
            settings.set('ollama.timeout', 30)
        else:
            print("🧠 Fokus Mode: OFF - Resource normal")
            # Restore settings
            if cls._original_settings:
                settings.set('memory.cache_enabled', cls._original_settings.get('cache_enabled', True))
                settings.set('memory.max_document_length', cls._original_settings.get('max_doc_length', 3000))
                settings.set('ollama.timeout', cls._original_settings.get('timeout', 60))
                cls._original_settings = {}
    
    @classmethod
    def is_focus_mode(cls) -> bool:
        """Cek apakah dalam mode fokus"""
        return cls._focus_mode
    
    # ============================================
    # CACHE METHODS
    # ============================================
    
    def muat_cache(self):
        """Muat cache embedding dari file"""
        if not self.cache_enabled:
            return
        try:
            with open(self.cache_file, 'r') as f:
                self.cache_embedding = json.load(f)
        except:
            self.cache_embedding = {}
            
    def simpan_cache(self):
        """Simpan cache embedding ke file"""
        if not self.cache_enabled:
            return
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache_embedding, f)
        except:
            pass
    
    # ============================================
    # CORE METHODS
    # ============================================
    
    def _get_embedding(self, text):
        """Dapatkan embedding dengan cache"""
        # Hash text untuk cache key
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Cek cache
        if self.cache_enabled and text_hash in self.cache_embedding:
            return self.cache_embedding[text_hash]
            
        # Generate embedding baru
        payload = {"model": self.embedding_model, "prompt": text}
        try:
            response = requests.post(self.ollama_emb_url, json=payload, timeout=self.timeout)
            embedding = response.json()["embedding"]
            
            # Simpan ke cache
            if self.cache_enabled:
                self.cache_embedding[text_hash] = embedding
                self.simpan_cache()
            return embedding
        except Exception as e:
            print(f"❌ Gagal membuat embedding: {e}")
            return None

    def _get_ollama_response(self, prompt, model=None):
        """Dapatkan response dari Ollama"""
        if model is None:
            model = self.chat_model
            
        # Gunakan timeout yang sudah dioptimasi (bisa berubah saat fokus mode)
        timeout = self.timeout
            
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": settings.get('llm.temperature', 0.7),
                "top_p": settings.get('llm.top_p', 0.9),
                "top_k": settings.get('llm.top_k', 40),
                "repeat_penalty": settings.get('llm.repeat_penalty', 1.1),
                # Saat fokus mode, kurangi max_tokens untuk response cepat
                "max_tokens": 300 if self.is_focus_mode() else settings.get('llm.max_tokens', 500)
            }
        }
        try:
            response = requests.post(self.ollama_gen_url, json=payload, timeout=timeout)
            return response.json()['response'].strip()
        except Exception as e:
            print(f"❌ Gagal mendapatkan response dari Ollama: {e}")
            return None

    def simpan_ilmu_baru(self, file_name, isi_teks, metadata=None):
        """Menyimpan pengetahuan baru ke memori jangka panjang"""
        # Batasi panjang teks jika terlalu panjang
        max_len = self.max_doc_length
        if len(isi_teks) > max_len:
            isi_teks = isi_teks[:max_len] + "..."
            
        vector = self._get_embedding(isi_teks)
        if vector:
            metadata = metadata or {}
            metadata.update({
                "source": file_name,
                "timestamp": datetime.now().isoformat(),
                "size": len(isi_teks),
                "focus_mode": self.is_focus_mode()  # Tandai jika diproses saat fokus
            })
            
            try:
                # Gunakan ID yang unik
                doc_id = f"{file_name}_{datetime.now().timestamp()}"
                # Cek apakah ID sudah ada
                existing = self.collection.get(ids=[doc_id])
                if existing and existing['ids']:
                    # Jika sudah ada, update
                    self.collection.update(
                        ids=[doc_id],
                        embeddings=[vector],
                        documents=[isi_teks],
                        metadatas=[metadata]
                    )
                else:
                    self.collection.add(
                        embeddings=[vector],
                        documents=[isi_teks],
                        metadatas=[metadata],
                        ids=[doc_id]
                    )
                print(f"😇 AIRAA: Aku telah merekam ilmu baru dari '{file_name}' ke ingatanku.")
                return True
            except Exception as e:
                print(f"❌ Gagal menyimpan ke ChromaDB: {e}")
                return False
        return False

    def ingat_kembali(self, pertanyaan, n_results=None):
        """Mencari informasi relevan di memori"""
        if n_results is None:
            # Saat fokus mode, cari lebih sedikit dokumen untuk kecepatan
            if self.is_focus_mode():
                n_results = 2  # Lebih sedikit = lebih cepat
            else:
                n_results = settings.get('memory.default_results', 3)
            
        vector = self._get_embedding(pertanyaan)
        if not vector:
            return ""
        
        try:
            hasil = self.collection.query(query_embeddings=[vector], n_results=n_results)
            if hasil and hasil['documents'] and hasil['documents'][0]:
                # Gabungkan hasil jika multiple
                if len(hasil['documents'][0]) > 1:
                    context = "\n\n---\n\n".join(hasil['documents'][0])
                    
                    # Saat fokus mode, gunakan LLM untuk merangkum (lebih cepat)
                    if self.is_focus_mode() and len(context) > 500:
                        prompt = f"""
                        Ringkas informasi berikut dengan sangat singkat dan jelas (maks 3 kalimat):
                        
                        {context[:1000]}
                        
                        Jawaban singkat:
                        """
                        summary = self._get_ollama_response(prompt)
                        if summary:
                            return f"[RINGKASAN FOKUS]\n{summary}\n\n[DETAIL]\n{context[:500]}..."
                    
                    return context
                return hasil['documents'][0][0]
        except Exception as e:
            print(f"❌ Gagal query memori: {e}")
        return ""

    def belajar_dari_url(self, url):
        """AIRAA belajar dari konten web"""
        try:
            from bs4 import BeautifulSoup
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts dan styles
            for script in soup(["script", "style"]):
                script.decompose()
                
            # Extract text
            teks = soup.get_text()
            lines = (line.strip() for line in teks.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            teks_bersih = ' '.join(chunk for chunk in chunks if chunk)
            
            if len(teks_bersih) > 100:
                nama_file = f"web_{hashlib.md5(url.encode()).hexdigest()[:10]}"
                return self.simpan_ilmu_baru(nama_file, teks_bersih[:self.max_doc_length], {"url": url})
            return False
        except Exception as e:
            print(f"❌ Gagal belajar dari URL {url}: {e}")
            return False

    def get_statistik_memori(self):
        """Dapatkan statistik memori"""
        try:
            count = self.collection.count()
            return {
                "total_dokumen": count,
                "last_updated": datetime.now().isoformat(),
                "focus_mode": self.is_focus_mode()
            }
        except:
            return {"total_dokumen": 0}
    
    # ============================================
    # CLEANUP
    # ============================================
    
    def cleanup(self):
        """Bersihkan resource jika perlu"""
        self.simpan_cache()
        print("🧠 Cache disimpan")


if __name__ == "__main__":
    # Test
    brain = AiraaBrain()
    print("🧠 Otak AIRAA siap beroperasi.")
    print(f"📚 Total memori: {brain.collection.count()} dokumen")
    print(f"🎯 Fokus Mode: {brain.is_focus_mode()}")