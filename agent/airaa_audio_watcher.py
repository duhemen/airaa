# airaa_audio_watcher.py - FIXED (No "self" error)
import wave
import time
import threading
import os
import subprocess
from datetime import datetime
import numpy as np

# Try to import whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
    model = whisper.load_model("base")
    print("✅ Whisper ready (Audio Watcher)")
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️ Whisper not available")
except Exception as e:
    WHISPER_AVAILABLE = False
    print(f"⚠️ Whisper error: {e}")

# Try to import pyaudio
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("⚠️ PyAudio not available")

from airaa_brain import AiraaBrain
from airaa_logger import AiraaLogger


class AiraaAudioWatcher:
    def __init__(self):
        self.brain = AiraaBrain()
        self.logger = AiraaLogger()
        self.is_running = False
        self.is_paused = False
        self.record_duration = 5
        self.audio_buffer = []
        self.last_transcript = ""
        self.last_transcript_time = 0
        
        # Cek ffmpeg
        self.ffmpeg_available = self._check_ffmpeg()
        if self.ffmpeg_available:
            print("🎵 FFmpeg available - WAV → MP3 compression enabled")
        else:
            print("⚠️ FFmpeg not found - using WAV format")
        
        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16 if PYAUDIO_AVAILABLE else 0
        self.CHANNELS = 1
        self.RATE = 16000
        
        print("👂 Audio Watcher initialized")
        
    def _check_ffmpeg(self):
        """Cek apakah ffmpeg tersedia"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            ffmpeg_paths = [
                "C:\\ffmpeg\\bin\\ffmpeg.exe",
                "C:\\ffmpeg\\ffmpeg.exe",
                "ffmpeg.exe"
            ]
            for path in ffmpeg_paths:
                if os.path.exists(path):
                    return True
            return False
            
    def _convert_wav_to_mp3(self, wav_file, mp3_file):
        """Konversi WAV ke MP3 dengan ffmpeg"""
        if not self.ffmpeg_available:
            return False
            
        try:
            cmd = [
                'ffmpeg', '-i', wav_file,
                '-acodec', 'mp3',
                '-ab', '64k',
                '-y',
                mp3_file
            ]
            
            if not subprocess.run(['ffmpeg', '-version'], capture_output=True).returncode == 0:
                ffmpeg_exe = "C:\\ffmpeg\\bin\\ffmpeg.exe"
                if os.path.exists(ffmpeg_exe):
                    cmd[0] = ffmpeg_exe
                    
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            return result.returncode == 0 and os.path.exists(mp3_file)
            
        except Exception as e:
            print(f"⚠️ FFmpeg conversion error: {e}")
            return False
            
    def start(self):
        if self.is_running:
            return
        if not PYAUDIO_AVAILABLE:
            return
        self.is_running = True
        self.is_paused = False
        thread = threading.Thread(target=self._watch_loop, daemon=True)
        thread.start()
        print("👂 Audio Watcher aktif!")
        
    def pause(self):
        self.is_paused = True
        print("⏸️ Audio Watcher dijeda")
        
    def resume(self):
        self.is_paused = False
        print("▶️ Audio Watcher dilanjutkan")
        
    def stop(self):
        self.is_running = False
        print("👂 Audio Watcher dihentikan")
        
    def _watch_loop(self):
        """Loop utama audio watcher"""
        if not PYAUDIO_AVAILABLE:
            return
            
        p = pyaudio.PyAudio()
        
        try:
            stream = p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            
            while self.is_running:
                if self.is_paused:
                    time.sleep(1)
                    continue
                    
                try:
                    # Rekam audio
                    frames = []
                    for _ in range(0, int(self.RATE / self.CHUNK * self.record_duration)):
                        data = stream.read(self.CHUNK, exception_on_overflow=False)
                        frames.append(data)
                    
                    # Simpan sebagai WAV
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    temp_wav = f"temp_audio_{timestamp}.wav"
                    
                    wf = wave.open(temp_wav, 'wb')
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(p.get_sample_size(self.FORMAT))
                    wf.setframerate(self.RATE)
                    wf.writeframes(b''.join(frames))
                    wf.close()
                    
                    # ============================================
                    # PROSES AUDIO - DENGAN ERROR HANDLING
                    # ============================================
                    if WHISPER_AVAILABLE and os.path.exists(temp_wav):
                        try:
                            # Cek ukuran file audio (minimal 1KB)
                            file_size = os.path.getsize(temp_wav)
                            if file_size < 1024:
                                print(f"🔇 Audio terlalu kecil ({file_size} bytes), skipping...")
                                try:
                                    os.remove(temp_wav)
                                except:
                                    pass
                                time.sleep(1)
                                continue
                            
                            audio_file = temp_wav
                            
                            # KONVERSI KE MP3 JIKA FFMPEG TERSEDIA
                            if self.ffmpeg_available:
                                temp_mp3 = temp_wav.replace('.wav', '.mp3')
                                if self._convert_wav_to_mp3(temp_wav, temp_mp3):
                                    audio_file = temp_mp3
                                    try:
                                        os.remove(temp_wav)
                                    except:
                                        pass
                            
                            # ============================================
                            # TRANSRIP DENGAN WHISPER
                            # ============================================
                            try:
                                result = model.transcribe(
                                    audio_file, 
                                    language='id',
                                    fp16=False,
                                    verbose=False
                                )
                                text = result['text'].strip()
                                
                                if len(text) > 10:
                                    # Panggil method dengan self
                                    self._process_audio_text(text)
                                    self.last_transcript = text
                                    self.last_transcript_time = time.time()
                                    print(f"🎙️ Transkrip: {text[:50]}...")
                                else:
                                    print(f"🔇 Tidak ada suara bermakna (text length: {len(text)})")
                                    
                            except RuntimeError as e:
                                error_msg = str(e)
                                if "key.size(1)" in error_msg:
                                    print("⚠️ Whisper tensor error (audio format issue), skipping...")
                                elif "out of memory" in error_msg.lower():
                                    print("⚠️ Whisper out of memory, skipping...")
                                else:
                                    print(f"⚠️ Whisper RuntimeError: {error_msg}")
                            except Exception as e:
                                print(f"⚠️ Whisper transcribe error: {e}")
                            
                            # Hapus file temp
                            try:
                                if os.path.exists(audio_file):
                                    os.remove(audio_file)
                            except:
                                pass
                                
                        except Exception as e:
                            print(f"⚠️ Audio processing error: {e}")
                            try:
                                if os.path.exists(temp_wav):
                                    os.remove(temp_wav)
                            except:
                                pass
                    
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ Audio recording error: {e}")
                    time.sleep(5)
                    
        except Exception as e:
            print(f"❌ Audio Watcher error: {e}")
        finally:
            try:
                stream.stop_stream()
                stream.close()
            except:
                pass
            p.terminate()
            
    def _process_audio_text(self, text):
        """Proses hasil transkrip audio"""
        if not text or len(text) < 10:
            return
            
        # Log
        self.logger.catat_interaksi("audio_capture", text[:200])
        
        # Simpan ke memori jika panjang
        if len(text) > 50:
            filename = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            self.brain.simpan_ilmu_baru(filename, text[:3000], {'source': 'audio'})
            print(f"👂 Audio content saved to memory")
            
    def get_latest_audio(self):
        """Dapatkan audio terakhir"""
        if self.last_transcript:
            return f"[{datetime.now().strftime('%H:%M:%S')}] {self.last_transcript[:200]}"
        return ""


if __name__ == "__main__":
    watcher = AiraaAudioWatcher()
    watcher.start()
    try:
        time.sleep(30)
    except KeyboardInterrupt:
        watcher.stop()