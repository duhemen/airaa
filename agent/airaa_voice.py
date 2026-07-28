import speech_recognition as sr
import threading
import queue
import time
import os

# Import settings
try:
    from settings_loader import settings
except ImportError:
    class DummySettings:
        def get(self, key, default=None):
            return default
    settings = DummySettings()

class AiraaVoice:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.callback = None
        self.thread = None
        self.microphone = None
        self.is_available = False
        
        # Settings
        self.language = settings.get('voice.language', 'id-ID')
        self.listening_timeout = settings.get('voice.listening_timeout', 5)
        self.phrase_time_limit = settings.get('voice.phrase_time_limit', 10)
        self.auto_calibrate = settings.get('voice.auto_calibrate', True)
        self.tts_enabled = settings.get('voice.tts_enabled', False)
        
        # Coba inisialisasi microphone
        try:
            import pyaudio
            self.microphone = sr.Microphone()
            if self.auto_calibrate:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    print("🎤 Microphone dikalibrasi")
            self.is_available = True
            print("🎤 Voice module siap")
        except ImportError:
            print("⚠️ PyAudio tidak tersedia - Voice command dinonaktifkan")
            print("💡 Install dengan: pip install pyaudio")
        except Exception as e:
            print(f"⚠️ Voice module error: {e}")
            print("💡 Voice command akan dinonaktifkan")
                
        # TTS engine
        self.tts_engine = None
        if self.tts_enabled and self.is_available:
            try:
                import pyttsx3
                self.tts_engine = pyttsx3.init()
                voice_id = settings.get('voice.tts_voice', None)
                if voice_id:
                    self.tts_engine.setProperty('voice', voice_id)
                print("🎤 TTS engine initialized")
            except ImportError:
                print("⚠️ pyttsx3 tidak tersedia, TTS disabled")
                self.tts_enabled = False
            except Exception as e:
                print(f"❌ TTS init error: {e}")
                self.tts_enabled = False
            
    def mulai_mendengar(self, callback=None):
        """Mulai listening di background"""
        if not self.is_available:
            print("⏸️ Voice command tidak tersedia (PyAudio tidak terinstall)")
            return
            
        if self.is_listening:
            return
            
        if not settings.get('voice.enabled', True):
            print("⏸️ Voice command disabled in settings")
            return
            
        self.is_listening = True
        self.callback = callback
        
        def listen_loop():
            with self.microphone as source:
                if self.auto_calibrate:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                while self.is_listening:
                    try:
                        print("🎤 Mendengar...")
                        audio = self.recognizer.listen(source, timeout=self.listening_timeout, 
                                                      phrase_time_limit=self.phrase_time_limit)
                        
                        # Proses di thread terpisah
                        threading.Thread(target=self.proses_audio, args=(audio,), daemon=True).start()
                        
                    except sr.WaitTimeoutError:
                        continue
                    except Exception as e:
                        print(f"❌ Error listening: {e}")
                        time.sleep(1)
                        
        self.thread = threading.Thread(target=listen_loop, daemon=True)
        self.thread.start()
        print("🎤 Voice command aktif!")
        
    def proses_audio(self, audio):
        """Proses audio yang ditangkap"""
        if not self.is_available:
            return
            
        try:
            text = self.recognizer.recognize_google(audio, language=self.language)
            print(f"🗣️ Dikenali: {text}")
            
            if self.callback:
                self.callback(text)
                
        except sr.UnknownValueError:
            print("🔇 Tidak bisa mengenali ucapan")
        except sr.RequestError as e:
            print(f"❌ Error koneksi ke Google Speech: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
            
    def berhenti_mendengar(self):
        """Berhenti mendengar"""
        self.is_listening = False
        if self.thread:
            self.thread.join(timeout=2)
        print("🎤 Voice command dinonaktifkan")
        
    def text_to_speech(self, text):
        """Text to speech"""
        if not self.tts_enabled or not self.tts_engine:
            print(f"🔊 (TTS tidak tersedia) {text}")
            return
            
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"❌ TTS Error: {e}")

if __name__ == "__main__":
    voice = AiraaVoice()
    
    def test_callback(text):
        print(f"Command: {text}")
        
    voice.mulai_mendengar(test_callback)
    input("Press Enter to stop...\n")
    voice.berhenti_mendengar()