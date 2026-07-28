# airaa_agent_council.py - FIXED WITH CUDA SUPPORT
import asyncio
import os
import threading
import time
from datetime import datetime
import json
import warnings

# ============================================
# CUDA CHECK
# ============================================
try:
    import torch
    CUDA_AVAILABLE = torch.cuda.is_available()
    if CUDA_AVAILABLE:
        print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠️ CUDA not available - using CPU")
except ImportError:
    CUDA_AVAILABLE = False
    print("⚠️ PyTorch not installed - using CPU")

# ============================================
# AUTOGEN IMPORTS - PAKAI VERSI YANG BENAR
# ============================================
try:
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
    from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
    from autogen_agentchat.ui import Console
    from autogen_core import CancellationToken
    AUTOGEN_AVAILABLE = True
    print("✅ AutoGen loaded successfully")
except ImportError as e:
    print(f"⚠️ AutoGen import error: {e}")
    AUTOGEN_AVAILABLE = False

# ============================================
# OLLAMA CLIENT - PAKAI autogen_ext.models.ollama
# ============================================
try:
    from autogen_ext.models.ollama import OllamaChatCompletionClient
    OLLAMA_CLIENT_AVAILABLE = True
    print("✅ Ollama Client loaded")
except ImportError as e:
    print(f"⚠️ Ollama Client error: {e}")
    print("💡 Install: pip install autogen-ext[ollama]")
    OLLAMA_CLIENT_AVAILABLE = False

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
    print("✅ Tiktoken loaded")
except ImportError as e:
    print(f"⚠️ Tiktoken not available: {e}")
    TIKTOKEN_AVAILABLE = False

# ============================================
# AIRAA MODULES
# ============================================
from airaa_brain import AiraaBrain
from airaa_logger import AiraaLogger

try:
    from airaa_screen_watcher import AiraaScreenWatcher
    SCREEN_WATCHER_AVAILABLE = True
except ImportError:
    SCREEN_WATCHER_AVAILABLE = False
    print("⚠️ Screen Watcher not available")

try:
    from airaa_audio_watcher import AiraaAudioWatcher
    AUDIO_WATCHER_AVAILABLE = True
except ImportError:
    AUDIO_WATCHER_AVAILABLE = False
    print("⚠️ Audio Watcher not available")


class AngelicCouncil:
    """The Angelic Council - Multi-Agent System with Ollama + CUDA"""
    
    def __init__(self, use_ollama=True, fallback_to_brain=True, use_gpu=True):
        self.brain = AiraaBrain()
        self.logger = AiraaLogger()
        self.fallback_to_brain = fallback_to_brain
        self.use_gpu = use_gpu and CUDA_AVAILABLE
        
        if self.use_gpu:
            print("🎮 GPU mode enabled for AutoGen")
        
        # ============================================
        # INISIALISASI WATCHER
        # ============================================
        self.screen_watcher = None
        self.audio_watcher = None
        
        if SCREEN_WATCHER_AVAILABLE:
            try:
                self.screen_watcher = AiraaScreenWatcher()
                print("👁️ Screen Watcher initialized")
            except Exception as e:
                print(f"⚠️ Screen Watcher init error: {e}")
                
        if AUDIO_WATCHER_AVAILABLE:
            try:
                self.audio_watcher = AiraaAudioWatcher()
                print("👂 Audio Watcher initialized")
            except Exception as e:
                print(f"⚠️ Audio Watcher init error: {e}")
        
        # ============================================
        # INISIALISASI AUTOGEN DENGAN OLLAMA
        # ============================================
        self.use_ollama = use_ollama
        self.model_client = None
        self.agents = []
        self.team = None
        self.is_available = False
        
        # Coba setup Ollama client
        if self.use_ollama and OLLAMA_CLIENT_AVAILABLE:
            self._setup_ollama_client()
        
        # Jika Ollama client berhasil, buat agents
        if self.model_client:
            try:
                self._create_agents()
                self._create_team()
                self.is_available = True
                print("🧠 Angelic Council initialized with Ollama + GPU!")
            except Exception as e:
                print(f"⚠️ AutoGen init error: {e}")
                self.is_available = False
                print("💡 Running in fallback mode (using brain only)")
        else:
            print("⚠️ No model client available")
            print("💡 Running in fallback mode (using brain only)")
        
    def _setup_ollama_client(self):
        """Setup Ollama client dengan autogen_ext.models.ollama"""
        if not OLLAMA_CLIENT_AVAILABLE:
            print("⚠️ Ollama Client not available")
            return
            
        try:
            # ============================================
            # OLLAMA CLIENT UNTUK AUTOGEN
            # ============================================
            # AutoGen v0.2+ menggunakan autogen_ext.models.ollama
            
            # Coba test koneksi ke Ollama
            try:
                import requests
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    print("✅ Ollama server is running")
                    # Cek apakah model tersedia
                    models = response.json().get('models', [])
                    model_names = [m.get('name', '') for m in models]
                    if not any('qwen2.5:7b' in name for name in model_names):
                        print(f"⚠️ Model 'qwen2.5:7b-instruct' not found in Ollama")
                        print(f"📦 Available models: {', '.join(model_names[:3])}...")
                else:
                    print(f"⚠️ Ollama server returned: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Cannot connect to Ollama server: {e}")
                print("💡 Make sure Ollama is running: 'ollama serve'")
            
            # ============================================
            # CREATE OLLAMA CLIENT
            # ============================================
            self.model_client = OllamaChatCompletionClient(
                model="qwen2.5:7b-instruct",
                base_url="http://localhost:11434",
                temperature=0.7,
                max_tokens=500,
                timeout=60
            )
            
            print("✅ Ollama client configured (model: qwen2.5:7b-instruct)")
            
            # Test dengan request sederhana
            try:
                # Test sync request
                test_response = self.model_client.create(
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10
                )
                print("✅ Ollama client test successful")
            except Exception as e:
                print(f"⚠️ Ollama client test failed: {e}")
                print("💡 The client may still work for simple requests")
                
        except Exception as e:
            print(f"⚠️ Ollama client error: {e}")
            self.model_client = None
            
    def _create_agents(self):
        """Buat agen-agen spesialis"""
        if not self.model_client:
            return
            
        try:
            # System prompt yang lebih baik untuk setiap agen
            observer_prompt = """Kamu adalah 👁️ OBSERVER, malaikat yang selalu melihat dan mendengar.
            Tugasmu:
            1. Berikan ringkasan SINGKAT aktivitas Emen dari layar dan suara
            2. Identifikasi hal penting yang terjadi
            3. Beri konteks untuk agen lain

            Mulai jawabanmu dengan '👁️ OBSERVER:' 
            Untuk sapaan sederhana seperti "selamat sore", cukup jawab langsung dengan hangat tanpa analisis berlebihan.
            """

            analyst_prompt = """Kamu adalah 🧠 ANALYST, malaikat yang berpikir dalam.
            Tugasmu:
            1. Analisis informasi dari Observer
            2. Cari pola dan insight dari aktivitas Emen
            3. Berikan rekomendasi awal

            Mulai jawabanmu dengan '🧠 ANALYST:'
            Untuk sapaan sederhana, langsung sambut dengan hangat dan tanyakan kabar Emen.
            """

            critic_prompt = """Kamu adalah ⚖️ CRITIC, malaikat yang selalu waspada.
            Tugasmu:
            1. Evaluasi analisis dari Analyst
            2. Identifikasi risiko atau kelemahan
            3. Berikan saran perbaikan

            Mulai jawabanmu dengan '⚖️ CRITIC:'
            Untuk sapaan sederhana, akhiri dengan '✅ APPROVED' dan biarkan Guardian yang merespon.
            """

            guardian_prompt = """Kamu adalah 🛡️ GUARDIAN, malaikat yang mengingatkan.
            Tugasmu:
            1. Catat insight penting ke memori jangka panjang
            2. Buat ringkasan akhir dari diskusi
            3. Berikan rekomendasi tindakan

            Mulai jawabanmu dengan '🛡️ GUARDIAN:'
            Untuk sapaan sederhana, langsung berikan jawaban hangat dan ramah. Contoh: "Selamat sore, Emen! Aku baik, terima kasih sudah menyapa. Ada yang bisa aku bantu sore ini? 😇"
            """
            
            # 1. Observer - Melihat dan mendengar
            self.observer = AssistantAgent(
                name="Observer",
                model_client=self.model_client,
                system_message=observer_prompt
            )
            
            # 2. Analyst - Berpikir dan menganalisis
            self.analyst = AssistantAgent(
                name="Analyst",
                model_client=self.model_client,
                system_message=analyst_prompt
            )
            
            # 3. Critic - Mengkaji dan mengevaluasi
            self.critic = AssistantAgent(
                name="Critic",
                model_client=self.model_client,
                system_message=critic_prompt
            )
            
            # 4. Guardian - Mengingatkan dan mencatat
            self.guardian = AssistantAgent(
                name="Guardian",
                model_client=self.model_client,
                system_message=guardian_prompt
            )
            
            self.agents = [self.observer, self.analyst, self.critic, self.guardian]
            print(f"✅ Created {len(self.agents)} agents")
            
        except Exception as e:
            print(f"⚠️ Agent creation error: {e}")
            self.is_available = False
            
    def _create_team(self):
        """Bentuk tim dengan auto-termination"""
        if not self.agents:
            return
            
        try:
            # Terminate jika Guardian sudah memberikan rekomendasi
            termination = TextMentionTermination("✅ APPROVED")
            max_messages = MaxMessageTermination(max_messages=8)
            
            self.team = RoundRobinGroupChat(
                participants=self.agents,
                termination_condition=termination | max_messages,
            )
            print("✅ Team created")
        except Exception as e:
            print(f"⚠️ Team creation error: {e}")
            self.is_available = False
            
    async def process_question(self, question: str) -> str:
        """Proses pertanyaan dengan seluruh dewan"""
    
        # ============================================
        # DETEKSI PERTANYAAN SEDERHANA
        # ============================================
        simple_greetings = ['selamat pagi', 'selamat siang', 'selamat sore', 'selamat malam', 'apakabar', 'apa kabar', 'hai', 'halo', 'hello', 'hi']
    
        question_lower = question.lower()
        if any(greeting in question_lower for greeting in simple_greetings):
            # Langsung jawab tanpa AutoGen
            greetings = {
                'pagi': 'Selamat pagi, Emen! ☀️ Semoga harimu menyenangkan! Ada yang bisa aku bantu? 😇',
                'siang': 'Selamat siang, Emen! 🌤️ Semoga aktivitasmu lancar! Ada yang bisa aku bantu? 😇',
                'sore': 'Selamat sore, Emen! 🌅 Semoga soremu tenang! Ada yang bisa aku bantu? 😇',
                'malam': 'Selamat malam, Emen! 🌙 Istirahat yang nyaman ya! Ada yang bisa aku bantu? 😇'
            }
            for key, response in greetings.items():
                if key in question_lower:
                    return response
            return "Halo Emen! 👋 Ada yang bisa aku bantu hari ini? 😇"
    
        # ============================================
        # PROSES DENGAN AUTOGEN UNTUK PERTANYAAN KOMPLEKS
        # ============================================
        if not self.is_available or not self.team:
            if self.fallback_to_brain:
                return self.brain.ingat_kembali(question)
            return "⚠️ Sistem tidak tersedia."
        
        # Tambahkan konteks real-time dari screen & audio
        screen_context = ""
        audio_context = ""
        
        if self.screen_watcher:
            try:
                screen_context = self.screen_watcher.get_recent_context()
            except Exception as e:
                print(f"⚠️ Screen context error: {e}")
                
        if self.audio_watcher:
            try:
                audio_context = self.audio_watcher.get_latest_audio()
            except Exception as e:
                print(f"⚠️ Audio context error: {e}")
        
        # Context yang lebih terstruktur
        full_prompt = f"""
        📋 KONTEKS AKTIVITAS EMEN:
        
        🖥️ LAYAR (terakhir): 
        {screen_context if screen_context else 'Tidak ada data layar'}
        
        🎵 SUARA (terakhir):
        {audio_context if audio_context else 'Tidak ada data audio'}
        
        ❓ PERTANYAAN EMEN:
        {question}
        
        🔄 PROSES:
        1. Observer: Ringkasan aktivitas Emen
        2. Analyst: Analisis dan rekomendasi awal
        3. Critic: Evaluasi dan perbaikan
        4. Guardian: Rekomendasi final dan catatan
        
        Mohon berikan jawaban terbaik dengan proses di atas.
        """
        
        try:
            # Run the team
            result = await Console(self.team.run_stream(task=full_prompt))
            
            # Ekstrak jawaban dari Guardian
            if result and hasattr(result, 'messages'):
                for msg in reversed(result.messages):
                    if hasattr(msg, 'content') and '🛡️ GUARDIAN:' in msg.content:
                        return msg.content
                # Jika tidak ada Guardian, ambil pesan terakhir
                last_msg = result.messages[-1] if result.messages else None
                if last_msg and hasattr(last_msg, 'content'):
                    return last_msg.content
                    
            return str(result)
            
        except Exception as e:
            print(f"❌ Council error: {e}")
            if self.fallback_to_brain:
                return self.brain.ingat_kembali(question)
            return f"❌ Error: {e}"
            
    def start_continuous_monitoring(self):
        """Mulai monitoring kontinu di background"""
        if self.screen_watcher:
            try:
                self.screen_watcher.start()
                print("👁️ Screen Watcher started")
            except Exception as e:
                print(f"⚠️ Screen Watcher start error: {e}")
                
        if self.audio_watcher:
            try:
                self.audio_watcher.start()
                print("👂 Audio Watcher started")
            except Exception as e:
                print(f"⚠️ Audio Watcher start error: {e}")
                
        if self.is_available:
            threading.Thread(target=self._continuous_loop, daemon=True).start()
            print("🔄 Continuous monitoring active")
        
    def _continuous_loop(self):
        """Loop kontinu untuk deteksi trigger"""
        while True:
            try:
                if not self.screen_watcher:
                    time.sleep(60)
                    continue
                    
                recent = self.screen_watcher.get_recent_context(limit=3)
                keywords = ['error', 'bug', 'exception', 'failed', 'warning', 'critical']
                
                if any(kw in recent.lower() for kw in keywords):
                    asyncio.run(self._handle_automatic_alert(recent))
                    
                time.sleep(30)
                
            except Exception as e:
                print(f"❌ Continuous loop error: {e}")
                time.sleep(60)
                
    async def _handle_automatic_alert(self, context):
        """Tangani alert otomatis"""
        print("⚡ Automatic alert triggered!")
        result = await self.process_question(
            f"Ada aktivitas penting terdeteksi: {context[:200]}\n\n"
            f"Berikan analisis dan rekomendasi."
        )
        print(f"💬 Auto response: {result[:200] if result else 'No response'}")
        
    def stop(self):
        """Hentikan semua watcher"""
        if self.screen_watcher:
            try:
                self.screen_watcher.stop()
            except:
                pass
        if self.audio_watcher:
            try:
                self.audio_watcher.stop()
            except:
                pass
        print("🛑 Angelic Council stopped")