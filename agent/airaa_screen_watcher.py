# airaa_screen_watcher.py - FIXED VERSION
import time
import os
import threading
import base64
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
import io

# Try to import OCR
try:
    from paddleocr import PaddleOCR
    OCR_AVAILABLE = True
    # Hapus parameter show_log yang tidak dikenali
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    print("✅ PaddleOCR ready (Screen Watcher)")
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️ PaddleOCR not available (install: pip install paddlepaddle paddleocr)")
except Exception as e:
    OCR_AVAILABLE = False
    print(f"⚠️ PaddleOCR error: {e}")

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False
    print("⚠️ mss not available (install: pip install mss)")

try:
    import pygetwindow as gw
    GW_AVAILABLE = True
except ImportError:
    GW_AVAILABLE = False
    print("⚠️ pygetwindow not available (install: pip install pygetwindow)")

from airaa_brain import AiraaBrain
from airaa_logger import AiraaLogger


class AiraaScreenWatcher:
    def __init__(self):
        self.brain = AiraaBrain()
        self.logger = AiraaLogger()
        self.is_running = False
        self.is_paused = False
        self.capture_interval = 10  # detik
        self.last_captures = []
        
        # Window tracking
        self.current_window = None
        self.window_history = []
        
        # Cache untuk OCR
        self.last_text = ""
        self.last_capture_time = 0
        
        print("👁️ Screen Watcher initialized")
        
    def start(self):
        if self.is_running:
            return
        if not MSS_AVAILABLE:
            return
        self.is_running = True
        self.is_paused = False
        thread = threading.Thread(target=self._watch_loop, daemon=True)
        thread.start()
        print("👁️ Screen Watcher aktif!")
        
    def pause(self):
        """Pause screen watcher"""
        self.is_paused = True
        print("⏸️ Screen Watcher dijeda")
        
    def resume(self):
        """Resume screen watcher"""
        self.is_paused = False
        print("▶️ Screen Watcher dilanjutkan")
        
    def stop(self):
        self.is_running = False
        print("👁️ Screen Watcher dihentikan")
        
    def _watch_loop(self):
        """Loop utama screen watcher"""
        if not MSS_AVAILABLE:
            return
            
        with mss.mss() as sct:
            try:
                monitor = sct.monitors[1]  # Monitor utama
            except:
                monitor = sct.monitors[0]  # Fallback ke monitor pertama
            
            while self.is_running:
                if self.is_paused:
                    time.sleep(1)
                    continue
                    
                try:
                    # 1. Capture screenshot
                    screenshot = sct.grab(monitor)
                    img = np.array(screenshot)
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
                    
                    # 2. Ekstrak teks dengan OCR
                    extracted_text = self._extract_text(img_rgb)
                    
                    # 3. Proses jika ada teks
                    if extracted_text and len(extracted_text) > 20:
                        self._process_screen_content(extracted_text)
                        self.last_text = extracted_text
                        self.last_capture_time = time.time()
                    
                    # 4. Deteksi window aktif
                    self._detect_active_window()
                    
                    # 5. Simpan untuk konteks
                    timestamp = datetime.now().isoformat()
                    self.last_captures.append({
                        'timestamp': timestamp,
                        'text': (extracted_text[:500] if extracted_text else '')[:500],
                        'window': self.current_window or 'Unknown'
                    })
                    
                    # Keep last 10 captures
                    if len(self.last_captures) > 10:
                        self.last_captures.pop(0)
                    
                    # 6. Sleep
                    time.sleep(self.capture_interval)
                    
                except Exception as e:
                    print(f"❌ Screen Watcher error: {e}")
                    time.sleep(5)
                    
    def _extract_text(self, img):
        """Ekstrak teks dari gambar dengan OCR"""
        if not OCR_AVAILABLE:
            return ""
            
        try:
            # Resize untuk performa
            h, w = img.shape[:2]
            if w > 1920:
                scale = 1920 / w
                new_w = 1920
                new_h = int(h * scale)
                img = cv2.resize(img, (new_w, new_h))
                
            result = ocr.ocr(img, cls=True)
            
            if result and result[0]:
                texts = []
                for line in result[0]:
                    if line and len(line) > 1:
                        # line[1][0] adalah teks
                        texts.append(line[1][0])
                return ' '.join(texts)
        except Exception as e:
            # Error handling tanpa akses variabel yang tidak terdefinisi
            pass
        return ''
        
    def _process_screen_content(self, text):
        """Proses konten dari layar"""
        if not text or len(text) < 20:
            return
            
        # Cek apakah ada kata kunci menarik
        keywords = ['error', 'bug', 'exception', 'failed', 'success', 
                   'selesai', 'done', 'warning', 'critical', 'alert']
        
        text_lower = text.lower()
        found_keywords = [kw for kw in keywords if kw in text_lower]
        
        if found_keywords:
            self.logger.catat_interaksi("screen_alert", text[:200], {
                'type': 'keyword_detected',
                'keywords': found_keywords,
                'window': self.current_window
            })
            
            # Simpan ke memori jika panjang
            if len(text) > 100:
                filename = f"screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                self.brain.simpan_ilmu_baru(filename, text[:3000], {'source': 'screen'})
                print(f"👁️ Screen content saved to memory (keywords: {found_keywords})")
                
    def _detect_active_window(self):
        """Deteksi window aktif"""
        if not GW_AVAILABLE:
            return
            
        try:
            active = gw.getActiveWindow()
            if active:
                new_window = active.title
                if new_window and new_window != self.current_window:
                    self.current_window = new_window
                    self.window_history.append(self.current_window)
                    self.logger.catat_interaksi("window_change", self.current_window)
                    if len(self.window_history) > 20:
                        self.window_history.pop(0)
        except:
            pass
            
    def get_recent_context(self, limit=3):
        """Dapatkan konteks aktivitas terbaru"""
        context = []
        for capture in self.last_captures[-limit:]:
            if capture.get('text'):
                context.append(
                    f"[{capture['timestamp']}] {capture['window']}: {capture['text'][:100]}"
                )
        return '\n'.join(context) if context else "Tidak ada aktivitas terdeteksi"