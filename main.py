# main.py - FULLY FIXED WITH ALL METHODS INSIDE CLASS
import customtkinter as ctk
from tkinter import messagebox, ttk
import threading
import os
import sys
import json
import re
import random
import datetime
import asyncio
from datetime import datetime

# ============================================
# SETUP PATH & ENVIRONMENT
# ============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AGENT_DIR = os.path.join(BASE_DIR, 'agent')
CONFIG_DIR = os.path.join(BASE_DIR, 'config')

sys.path.insert(0, AGENT_DIR)
sys.path.insert(0, CONFIG_DIR)

# FFmpeg path
os.environ["PATH"] += os.pathsep + "C:\\ffmpeg\\bin"

print(f"📁 Base Dir: {BASE_DIR}")
print(f"📁 Agent Dir: {AGENT_DIR}")
print(f"📁 Config Dir: {CONFIG_DIR}")

# ============================================
# IMPORT SETTINGS
# ============================================
try:
    from settings_loader import settings
    print("✅ Settings loaded successfully")
except ImportError as e:
    print(f"❌ Gagal load settings: {e}")
    class DummySettings:
        def get(self, key, default=None):
            return default
    settings = DummySettings()

# ============================================
# COLOR PALETTE
# ============================================
COLORS = {
    "primary": "#6C63FF",
    "primary_light": "#8B83FF",
    "primary_dark": "#4A42D9",
    "secondary": "#FF6584",
    "accent": "#00D2FF",
    "accent_light": "#66E5FF",
    "success": "#00D26A",
    "warning": "#FFB800",
    "danger": "#FF4757",
    "bg_dark": "#0F0F1A",
    "bg_medium": "#1A1A2E",
    "bg_light": "#24243A",
    "surface": "#2D2D44",
    "surface_light": "#3A3A55",
    "text_primary": "#FFFFFF",
    "text_secondary": "#B8B8D0",
    "text_muted": "#8888AA",
}

# ============================================
# ATUR TEMA
# ============================================
try:
    theme = settings.get('gui.theme', 'dark')
    ctk.set_appearance_mode(theme)
    ctk.set_default_color_theme("blue")
    print(f"🎨 Theme: {theme}")
except Exception as e:
    print(f"⚠️ Theme setting error: {e}")
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

# ============================================
# IMPORT MODUL AIRAA
# ============================================
try:
    from airaa_brain import AiraaBrain
    print("✅ AiraaBrain loaded")
except ImportError as e:
    print(f"❌ AiraaBrain: {e}")

try:
    from airaa_proactive import AiraaProactive, sapa_emen_proaktif
    print("✅ AiraaProactive loaded")
except ImportError as e:
    print(f"❌ AiraaProactive: {e}")

try:
    from airaa_watcher import AiraaMultimodalWatcher, jalankan_pemantau
    print("✅ AiraaWatcher loaded")
except ImportError as e:
    print(f"❌ AiraaWatcher: {e}")

try:
    from airaa_logger import AiraaLogger
    print("✅ AiraaLogger loaded")
except ImportError as e:
    print(f"❌ AiraaLogger: {e}")

try:
    from airaa_reminder import AiraaReminder
    print("✅ AiraaReminder loaded")
except ImportError as e:
    print(f"❌ AiraaReminder: {e}")

try:
    from airaa_analytics import AiraaAnalytics
    print("✅ AiraaAnalytics loaded")
except ImportError as e:
    print(f"❌ AiraaAnalytics: {e}")

try:
    from airaa_voice import AiraaVoice
    print("✅ AiraaVoice loaded")
except ImportError as e:
    print(f"❌ AiraaVoice: {e}")

# ============================================
# IMPORT SCREEN & AUDIO WATCHER
# ============================================
try:
    from airaa_screen_watcher import AiraaScreenWatcher
    SCREEN_WATCHER_AVAILABLE = True
    print("✅ Screen Watcher loaded")
except ImportError:
    SCREEN_WATCHER_AVAILABLE = False
    print("⚠️ Screen Watcher not available")

try:
    from airaa_audio_watcher import AiraaAudioWatcher
    AUDIO_WATCHER_AVAILABLE = True
    print("✅ Audio Watcher loaded")
except ImportError:
    AUDIO_WATCHER_AVAILABLE = False
    print("⚠️ Audio Watcher not available")

# ============================================
# IMPORT ANGELIC COUNCIL (AUTOGEN)
# ============================================
try:
    from airaa_agent_council import AngelicCouncil
    COUNCIL_AVAILABLE = True
    print("✅ AngelicCouncil loaded")
except ImportError as e:
    COUNCIL_AVAILABLE = False
    print(f"⚠️ AngelicCouncil not available: {e}")

# ============================================
# MAIN GUI CLASS
# ============================================
class AiraaModernGUI:
    def __init__(self, root):
        self.root = root
        
        # Window settings
        width = settings.get('gui.window_width', 850)
        height = settings.get('gui.window_height', 700)
        min_width = settings.get('gui.min_width', 700)
        min_height = settings.get('gui.min_height', 600)
        
        self.root.title("😇 AIRAA - AI Recording Angel Agentic v2.0")
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(min_width, min_height)
        self.root.configure(fg_color=COLORS["bg_dark"])
        
        # ============================================
        # INISIALISASI KOMPONEN
        # ============================================
        self.brain = None
        self.logger = None
        self.reminder = None
        self.analytics = None
        self.voice = None
        self.proactive = None
        self.screen_watcher = None
        self.audio_watcher = None
        self.council = None
        
        # ============================================
        # STATUS FLAGS
        # ============================================
        self.focus_mode = False
        self.is_listening = False
        self.refresh_interval = settings.get('gui.auto_refresh_interval', 5)
        
        # ============================================
        # INISIALISASI BRAIN
        # ============================================
        try:
            self.brain = AiraaBrain()
            print("🧠 Brain initialized")
        except Exception as e:
            print(f"❌ Brain init error: {e}")
        
        # ============================================
        # INISIALISASI LOGGER
        # ============================================
        try:
            self.logger = AiraaLogger()
            print("📝 Logger initialized")
        except Exception as e:
            print(f"❌ Logger init error: {e}")
        
        # ============================================
        # INISIALISASI REMINDER
        # ============================================
        try:
            self.reminder = AiraaReminder()
            print("⏰ Reminder initialized")
        except Exception as e:
            print(f"❌ Reminder init error: {e}")
        
        # ============================================
        # INISIALISASI ANALYTICS
        # ============================================
        try:
            self.analytics = AiraaAnalytics()
            print("📊 Analytics initialized")
        except Exception as e:
            print(f"❌ Analytics init error: {e}")
        
        # ============================================
        # INISIALISASI VOICE
        # ============================================
        try:
            self.voice = AiraaVoice()
            print("🎤 Voice initialized")
        except Exception as e:
            print(f"❌ Voice init error: {e}")
            class DummyVoice:
                def __init__(self):
                    self.is_available = False
                    self.is_listening = False
                def mulai_mendengar(self, callback=None):
                    print("⏸️ Voice tidak tersedia")
                def berhenti_mendengar(self):
                    pass
                def text_to_speech(self, text):
                    print(f"🔊 {text}")
            self.voice = DummyVoice()
        
        # ============================================
        # INISIALISASI PROACTIVE
        # ============================================
        try:
            self.proactive = AiraaProactive()
            print("😇 Proactive initialized")
        except Exception as e:
            print(f"❌ Proactive init error: {e}")
        
        # ============================================
        # START SCREEN & AUDIO WATCHER
        # ============================================
        if SCREEN_WATCHER_AVAILABLE:
            try:
                self.screen_watcher = AiraaScreenWatcher()
                self.screen_watcher.start()
                print("👁️ Screen Watcher started")
            except Exception as e:
                print(f"⚠️ Screen Watcher error: {e}")
        
        if AUDIO_WATCHER_AVAILABLE:
            try:
                self.audio_watcher = AiraaAudioWatcher()
                self.audio_watcher.start()
                print("👂 Audio Watcher started")
            except Exception as e:
                print(f"⚠️ Audio Watcher error: {e}")
        
        # ============================================
        # INISIALISASI ANGELIC COUNCIL (AUTOGEN)
        # ============================================
        if COUNCIL_AVAILABLE:
            try:
                self.council = AngelicCouncil(
                    use_ollama=True,
                    use_gpu=True,
                    fallback_to_brain=True
                )
                self.council.start_continuous_monitoring()
                print("🧠 Angelic Council initialized with AutoGen + GPU!")
            except Exception as e:
                print(f"⚠️ Council init error: {e}")
                self.council = None
        else:
            print("⚠️ Angelic Council not available - using brain only")
        
        # ============================================
        # BUILD UI - FULL
        # ============================================
        self.buat_antarmuka()
        self.aktifkan_fitur_otomatis()
        self.muat_pengingat_aktif()
        
        # Logger startup
        if self.logger:
            try:
                self.logger.catat_interaksi("system_start", "AIRAA v2.0 dimulai (AutoGen + GPU)")
            except:
                pass
        
        print("😇 AIRAA siap beroperasi!")
    
    # ============================================
    # BUILD INTERFACE - FULL
    # ============================================
    def buat_antarmuka(self):
        """Build the main interface with enhanced design"""
        
        # HEADER
        self.header_frame = ctk.CTkFrame(
            self.root,
            height=80,
            fg_color=COLORS["primary"],
            corner_radius=0
        )
        self.header_frame.pack(fill="x", pady=(0, 10))
        self.header_frame.pack_propagate(False)
        
        header_content = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=25, pady=15)
        
        self.label_judul = ctk.CTkLabel(
            header_content,
            text="😇 AIRAA DASHBOARD",
            font=ctk.CTkFont(family="Helvetica", size=26, weight="bold"),
            text_color="white"
        )
        self.label_judul.pack(side="left")
        
        self.label_subtitle = ctk.CTkLabel(
            header_content,
            text="AI Recording Angel Agentic v2.0 | AutoGen + GPU",
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color=COLORS["text_secondary"]
        )
        self.label_subtitle.pack(side="left", padx=(15, 0))
        
        self.status_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        self.status_frame.pack(side="right")
        
        self.status_indicator = ctk.CTkLabel(
            self.status_frame,
            text="● ONLINE",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["success"]
        )
        self.status_indicator.pack(side="right", padx=10)
        
        # MAIN CONTAINER
        self.main_frame = ctk.CTkFrame(
            self.root,
            fg_color=COLORS["bg_dark"],
            corner_radius=15
        )
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # STATUS LABEL
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="📡 Status: Mengaktifkan Sistem...",
            font=ctk.CTkFont(size=13, slant="italic"),
            text_color=COLORS["text_secondary"]
        )
        self.status_label.pack(pady=(10, 5), anchor="w", padx=10)
        
        # TAB VIEW
        self.tabview = ctk.CTkTabview(
            self.main_frame,
            fg_color=COLORS["bg_medium"],
            segmented_button_fg_color=COLORS["surface"],
            segmented_button_selected_color=COLORS["primary"],
            segmented_button_selected_hover_color=COLORS["primary_light"],
            segmented_button_unselected_color=COLORS["surface"],
            segmented_button_unselected_hover_color=COLORS["surface_light"],
            text_color=COLORS["text_primary"],
            corner_radius=12,
            height=500
        )
        self.tabview.pack(fill="both", expand=True, pady=10)
        
        # Tabs
        self.tab_interaksi = self.tabview.add("💬 Interaksi")
        self.buat_tab_interaksi()
        
        self.tab_pengingat = self.tabview.add("⏰ Pengingat")
        self.buat_tab_pengingat()
        
        self.tab_jurnal = self.tabview.add("📖 Jurnal")
        self.buat_tab_jurnal()
        
        self.tab_analytics = self.tabview.add("📊 Analytics")
        self.buat_tab_analytics()
        
        self.tab_voice = self.tabview.add("🎤 Voice")
        self.buat_tab_voice()
        
        self.tab_sensor = self.tabview.add("📡 Sensor")
        self.buat_tab_sensor()
        
        # FOOTER
        self.footer_label = ctk.CTkLabel(
            self.main_frame,
            text="⚡ AIRAA v2.0 | © 2026 - Malaikat Digital untuk Emen | 🤖 AutoGen + 🎮 GPU",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"]
        )
        self.footer_label.pack(pady=8)
    
    # ============================================
    # TAB INTERAKSI
    # ============================================
    def buat_tab_interaksi(self):
        btn_frame = ctk.CTkFrame(self.tab_interaksi, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        
        self.btn_sapa = ctk.CTkButton(
            btn_frame,
            text="🌟 Panggil Bisikan Malaikat",
            command=self.sapa_dengan_log,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=12,
            height=50,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_light"],
            text_color="white"
        )
        self.btn_sapa.pack(side="left", padx=5, fill="x", expand=True)
        
        self.btn_analisis = ctk.CTkButton(
            btn_frame,
            text="📊 Analisis Aktivitas Hari Ini",
            command=self.tampilkan_analisis_harian,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=12,
            height=50,
            fg_color=COLORS["success"],
            hover_color="#00B85A",
            text_color="white"
        )
        self.btn_analisis.pack(side="left", padx=5, fill="x", expand=True)
        
        # Fokus Mode
        focus_frame = ctk.CTkFrame(self.tab_interaksi, fg_color="transparent")
        focus_frame.pack(fill="x", pady=5)
        
        self.btn_focus = ctk.CTkButton(
            focus_frame,
            text="🎯 Mode Fokus: OFF",
            command=self.toggle_focus_mode,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=10,
            height=35,
            fg_color=COLORS["surface"],
            hover_color=COLORS["surface_light"],
            text_color=COLORS["text_secondary"],
            border_width=1,
            border_color=COLORS["surface_light"]
        )
        self.btn_focus.pack(side="right", padx=5)
        
        self.focus_info = ctk.CTkLabel(
            focus_frame,
            text="⚡ Fitur real-time aktif",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["success"]
        )
        self.focus_info.pack(side="right", padx=10)
        
        # Tanya Jawab
        frame_tanya = ctk.CTkFrame(
            self.tab_interaksi,
            fg_color=COLORS["bg_medium"],
            corner_radius=12
        )
        frame_tanya.pack(fill="x", pady=15)
        
        lbl_tanya = ctk.CTkLabel(
            frame_tanya,
            text="🧠 Tanya Memori Jangka Panjang:",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        lbl_tanya.pack(anchor="w", pady=(10, 5), padx=15)
        
        input_frame = ctk.CTkFrame(frame_tanya, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.input_tanya = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ketik apa yang ingin diingat kembali oleh AIRAA...",
            font=ctk.CTkFont(size=13),
            height=45,
            corner_radius=10,
            fg_color=COLORS["surface"],
            text_color=COLORS["text_primary"],
            border_color=COLORS["surface_light"],
            border_width=1
        )
        self.input_tanya.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_tanya.bind("<Return>", lambda e: self.tanya_memori())
        
        self.btn_cari = ctk.CTkButton(
            input_frame,
            text="🔍 Tanya",
            command=self.tanya_memori,
            width=120,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_light"],
            text_color=COLORS["bg_dark"]
        )
        self.btn_cari.pack(side="right")
        
        # Hasil
        self.text_hasil = ctk.CTkTextbox(
            self.tab_interaksi,
            font=ctk.CTkFont(size=13),
            corner_radius=12,
            border_width=0,
            fg_color=COLORS["surface"],
            text_color=COLORS["text_primary"]
        )
        self.text_hasil.pack(pady=10, fill="both", expand=True)
        self.text_hasil.insert(
            "1.0",
            "😇 AIRAA: Tulis pertanyaan di atas untuk mengorek memori...\n\n"
            "💡 Tips: Tanyakan tentang dokumen yang sudah dipelajari, "
            "kode yang pernah dibuat, atau catatan penting lainnya."
        )
    
    # ============================================
    # TAB PENGINGAT
    # ============================================
    def buat_tab_pengingat(self):
        input_frame = ctk.CTkFrame(
            self.tab_pengingat,
            fg_color=COLORS["bg_medium"],
            corner_radius=12
        )
        input_frame.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(
            input_frame,
            text="📝 Pesan:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.entry_reminder_pesan = ctk.CTkEntry(
            input_frame,
            width=350,
            height=40,
            corner_radius=8,
            fg_color=COLORS["surface"],
            text_color=COLORS["text_primary"],
            border_color=COLORS["surface_light"],
            border_width=1,
            font=ctk.CTkFont(size=13)
        )
        self.entry_reminder_pesan.grid(row=0, column=1, padx=10, pady=10, sticky="w", columnspan=2)
        
        ctk.CTkLabel(
            input_frame,
            text="⏰ Waktu (HH:MM):",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.entry_reminder_waktu = ctk.CTkEntry(
            input_frame,
            width=120,
            height=40,
            placeholder_text="14:30",
            corner_radius=8,
            fg_color=COLORS["surface"],
            text_color=COLORS["text_primary"],
            border_color=COLORS["surface_light"],
            border_width=1,
            font=ctk.CTkFont(size=13)
        )
        self.entry_reminder_waktu.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        self.reminder_ulangi = ctk.CTkCheckBox(
            input_frame,
            text="🔄 Ulangi Harian",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_primary"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_light"]
        )
        self.reminder_ulangi.grid(row=1, column=2, padx=10, pady=5, sticky="w")
        
        btn_tambah = ctk.CTkButton(
            input_frame,
            text="➕ Tambah Pengingat",
            command=self.tambah_pengingat,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            corner_radius=10,
            fg_color=COLORS["warning"],
            hover_color="#E6A600",
            text_color=COLORS["bg_dark"]
        )
        btn_tambah.grid(row=2, column=0, columnspan=3, pady=15, padx=10)
        
        self.reminder_list_frame = ctk.CTkScrollableFrame(
            self.tab_pengingat,
            fg_color=COLORS["surface"],
            corner_radius=12,
            height=200
        )
        self.reminder_list_frame.pack(fill="both", expand=True, pady=10)
        self.refresh_reminder_list()
    
    # ============================================
    # TAB JURNAL
    # ============================================
    def buat_tab_jurnal(self):
        filter_frame = ctk.CTkFrame(self.tab_jurnal, fg_color="transparent")
        filter_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            filter_frame,
            text="Filter:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=10)
        
        self.filter_jenis = ctk.CTkComboBox(
            filter_frame,
            values=["Semua", "sapaan", "tanya_memori", "belajar_file", "reminder", "system_start", "screen_alert", "audio_capture"],
            width=180,
            height=35,
            corner_radius=8,
            fg_color=COLORS["surface"],
            text_color=COLORS["text_primary"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_light"]
        )
        self.filter_jenis.pack(side="left", padx=5)
        self.filter_jenis.set("Semua")
        
        btn_refresh = ctk.CTkButton(
            filter_frame,
            text="🔄 Refresh",
            command=self.refresh_jurnal,
            width=100,
            height=35,
            corner_radius=8,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_light"],
            text_color=COLORS["bg_dark"],
            font=ctk.CTkFont(size=12, weight="bold")
        )
        btn_refresh.pack(side="right", padx=10)
        
        self.jurnal_text = ctk.CTkTextbox(
            self.tab_jurnal,
            font=ctk.CTkFont(size=12),
            corner_radius=12,
            fg_color=COLORS["surface"],
            text_color=COLORS["text_primary"],
            border_width=0
        )
        self.jurnal_text.pack(fill="both", expand=True, pady=10)
        self.refresh_jurnal()
    
    # ============================================
    # TAB ANALYTICS
    # ============================================
    def buat_tab_analytics(self):
        stats_frame = ctk.CTkFrame(
            self.tab_analytics,
            fg_color=COLORS["bg_medium"],
            corner_radius=12
        )
        stats_frame.pack(fill="x", pady=10)
        
        self.statistik_label = ctk.CTkLabel(
            stats_frame,
            text="📊 Memuat statistik...",
            font=ctk.CTkFont(size=13),
            justify="left",
            text_color=COLORS["text_primary"]
        )
        self.statistik_label.pack(pady=15, padx=15)
        
        btn_refresh_stats = ctk.CTkButton(
            self.tab_analytics,
            text="🔄 Refresh Statistik",
            command=self.refresh_statistik,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            corner_radius=10,
            fg_color=COLORS["success"],
            hover_color="#00B85A",
            text_color=COLORS["bg_dark"]
        )
        btn_refresh_stats.pack(pady=10)
        self.refresh_statistik()
    
    # ============================================
    # TAB VOICE - FIXED
    # ============================================
    def buat_tab_voice(self):
        voice_frame = ctk.CTkFrame(
            self.tab_voice,
            fg_color=COLORS["bg_medium"],
            corner_radius=12
        )
        voice_frame.pack(fill="x", pady=20)
        
        self.voice_status = ctk.CTkLabel(
            voice_frame,
            text="🎙️ Voice Command: Nonaktif",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_muted"]
        )
        self.voice_status.pack(pady=20)
        
        # TOMBOL VOICE - BERUBAH SAAT AKTIF
        self.btn_mic = ctk.CTkButton(
            voice_frame,
            text="🎤 Mulai Mendengar",
            command=self.toggle_voice,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=55,
            corner_radius=12,
            fg_color=COLORS["success"],
            hover_color="#00B85A",
            text_color="white"
        )
        self.btn_mic.pack(pady=20)
        
        # Hasil transkrip
        self.voice_text = ctk.CTkTextbox(
            self.tab_voice,
            font=ctk.CTkFont(size=13),
            height=180,
            corner_radius=12,
            fg_color=COLORS["surface"],
            text_color=COLORS["text_primary"],
            border_width=0
        )
        self.voice_text.pack(fill="both", expand=True, pady=10)
        self.voice_text.insert(
            "1.0",
            "🎤 Klik 'Mulai Mendengar' untuk memberi perintah suara ke AIRAA...\n\n"
            "Contoh perintah:\n"
            "- 'AIRAA, ingatkan aku tentang meeting jam 3'\n"
            "- 'AIRAA, apa yang aku pelajari kemarin?'\n"
            "- 'AIRAA, buat pengingat untuk...'\n"
            "- 'berhenti' atau 'stop' untuk berhenti mendengar\n"
            "- 'tutup' atau 'keluar' untuk menutup voice"
        )
    
    # ============================================
    # TAB SENSOR
    # ============================================
    def buat_tab_sensor(self):
        # Status Fokus Mode
        focus_status_frame = ctk.CTkFrame(
            self.tab_sensor,
            fg_color=COLORS["bg_medium"],
            corner_radius=12
        )
        focus_status_frame.pack(fill="x", pady=10, padx=5)
        
        focus_status = "🎯 FOKUS" if self.focus_mode else "🟢 NORMAL"
        focus_color = COLORS["warning"] if self.focus_mode else COLORS["success"]
        
        ctk.CTkLabel(
            focus_status_frame,
            text=f"🎯 Mode Fokus: {focus_status}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=focus_color
        ).pack(anchor="w", padx=15, pady=5)
        
        if self.focus_mode:
            ctk.CTkLabel(
                focus_status_frame,
                text="⏸️ Sensor dijeda untuk performa maksimal",
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_muted"]
            ).pack(anchor="w", padx=15, pady=(0, 5))
        
        # Status Sensor
        sensor_frame = ctk.CTkFrame(
            self.tab_sensor,
            fg_color=COLORS["bg_medium"],
            corner_radius=12
        )
        sensor_frame.pack(fill="x", pady=10, padx=5)
        
        # Screen Watcher Status
        screen_status = "🟢 AKTIF" if self.screen_watcher else "🔴 TIDAK AKTIF"
        screen_color = COLORS["success"] if self.screen_watcher else COLORS["danger"]
        
        ctk.CTkLabel(
            sensor_frame,
            text=f"👁️ Screen Watcher: {screen_status}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=screen_color
        ).pack(anchor="w", padx=15, pady=5)
        
        # Audio Watcher Status
        audio_status = "🟢 AKTIF" if self.audio_watcher else "🔴 TIDAK AKTIF"
        audio_color = COLORS["success"] if self.audio_watcher else COLORS["danger"]
        
        ctk.CTkLabel(
            sensor_frame,
            text=f"👂 Audio Watcher: {audio_status}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=audio_color
        ).pack(anchor="w", padx=15, pady=5)
        
        # Council Status
        council_status = "🟢 AKTIF" if self.council else "🔴 TIDAK AKTIF"
        council_color = COLORS["success"] if self.council else COLORS["danger"]
        
        ctk.CTkLabel(
            sensor_frame,
            text=f"🧠 Angelic Council: {council_status}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=council_color
        ).pack(anchor="w", padx=15, pady=5)
        
        # Activity Log
        activity_label = ctk.CTkLabel(
            sensor_frame,
            text="📡 Aktivitas Terdeteksi:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        activity_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        self.sensor_activity = ctk.CTkTextbox(
            self.tab_sensor,
            font=ctk.CTkFont(size=12),
            height=150,
            corner_radius=12,
            fg_color=COLORS["surface"],
            text_color=COLORS["text_secondary"],
            border_width=0
        )
        self.sensor_activity.pack(fill="both", expand=True, padx=10, pady=10)
        self.sensor_activity.insert("1.0", "Menunggu aktivitas dari sensor...")
        
        btn_refresh_sensor = ctk.CTkButton(
            self.tab_sensor,
            text="🔄 Refresh Sensor",
            command=self.refresh_sensor_status,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            corner_radius=10,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_light"],
            text_color=COLORS["bg_dark"]
        )
        btn_refresh_sensor.pack(pady=10)
    
    # ============================================
    # FUNGSI UTAMA
    # ============================================
    
    def sapa_dengan_log(self):
        """Panggil sapaan proaktif dan catat ke log"""
        try:
            if self.logger:
                self.logger.catat_interaksi("sapaan", "Sapaan proaktif dipanggil oleh user")
            if 'sapa_emen_proaktif' in globals():
                sapa_emen_proaktif()
        except Exception as e:
            print(f"❌ Sapaan error: {e}")
            messagebox.showerror("Error", f"Gagal memanggil sapaan: {e}")
    
    def tampilkan_analisis_harian(self):
        """Tampilkan analisis aktivitas hari ini"""
        try:
            if self.analytics:
                analisis = self.analytics.get_analisis_harian()
                if analisis:
                    self.text_hasil.delete("1.0", "end")
                    self.text_hasil.insert("1.0", analisis)
                else:
                    messagebox.showinfo("Informasi", "Belum ada data aktivitas hari ini.")
            else:
                messagebox.showinfo("Informasi", "Modul Analytics tidak tersedia.")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
    
    # ============================================
    # TANYA MEMORI
    # ============================================
    def tanya_memori(self):
        pertanyaan = self.input_tanya.get().strip()
        if not pertanyaan:
            messagebox.showwarning("Peringatan", "Tulis pertanyaanmu dulu, Emen.")
            return
        
        self.text_hasil.delete("1.0", "end")
        
        if self.council:
            self.text_hasil.insert("1.0", "🧠 Dewan Malaikat sedang berunding...\n")
            self.root.update()
            
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                jawaban = loop.run_until_complete(
                    self.council.process_question(pertanyaan)
                )
                loop.close()
                
                self.text_hasil.delete("1.0", "end")
                self.text_hasil.insert("1.0", jawaban)
                return
                
            except Exception as e:
                print(f"❌ Council error: {e}")
                self.text_hasil.insert("end", f"\n\n⚠️ Council error: {e}\n\nFallback ke Brain...")
        
        if self.brain:
            self.text_hasil.insert("1.0", "🔍 AIRAA sedang mengingat...\n")
            self.root.update()
            memori = self.brain.ingat_kembali(pertanyaan)
            self.text_hasil.delete("1.0", "end")
            if memori:
                self.text_hasil.insert("1.0", f"😇 AIRAA (Brain):\n\n{memori}")
            else:
                self.text_hasil.insert("1.0", "😇 AIRAA: Maaf, aku belum menemukan catatan itu.")
        else:
            self.text_hasil.insert("1.0", "❌ Tidak ada modul AI yang tersedia.")
        
        self.input_tanya.delete(0, "end")
    
    # ============================================
    # FOKUS MODE
    # ============================================
    def toggle_focus_mode(self):
        """Toggle fokus mode"""
        self.focus_mode = not self.focus_mode
        
        if self.focus_mode:
            if self.screen_watcher:
                try:
                    self.screen_watcher.pause()
                except:
                    pass
            if self.audio_watcher:
                try:
                    self.audio_watcher.pause()
                except:
                    pass
            if self.council:
                try:
                    self.council.screen_watcher.pause()
                except:
                    pass
                try:
                    self.council.audio_watcher.pause()
                except:
                    pass
            if self.brain:
                try:
                    self.brain.set_focus_mode(True)
                except:
                    pass
            
            self.btn_focus.configure(
                text="🎯 Mode Fokus: ON",
                fg_color=COLORS["warning"],
                text_color=COLORS["bg_dark"]
            )
            self.focus_info.configure(
                text="⏸️ Sensor dijeda + Brain dioptimasi",
                text_color=COLORS["warning"]
            )
            self.status_label.configure(
                text="🎯 Mode Fokus AKTIF - Performa maksimal!",
                text_color=COLORS["warning"]
            )
            
        else:
            if self.screen_watcher:
                try:
                    self.screen_watcher.resume()
                except:
                    pass
            if self.audio_watcher:
                try:
                    self.audio_watcher.resume()
                except:
                    pass
            if self.council:
                try:
                    self.council.screen_watcher.resume()
                except:
                    pass
                try:
                    self.council.audio_watcher.resume()
                except:
                    pass
            if self.brain:
                try:
                    self.brain.set_focus_mode(False)
                except:
                    pass
            
            self.btn_focus.configure(
                text="🎯 Mode Fokus: OFF",
                fg_color=COLORS["surface"],
                text_color=COLORS["text_secondary"]
            )
            self.focus_info.configure(
                text="⚡ Fitur real-time aktif",
                text_color=COLORS["success"]
            )
            self.status_label.configure(
                text="📡 Status Pemantau: AKTIF & MENGAWASI",
                text_color=COLORS["success"]
            )
        
        self.refresh_sensor_status()
    
    # ============================================
    # VOICE - TOGGLE
    # ============================================
    def toggle_voice(self):
        """Toggle voice command on/off dengan tombol berubah dan status jelas"""
        if not self.voice:
            messagebox.showinfo("Informasi", "Modul Voice tidak tersedia.")
            return
        
        if not self.is_listening:
            # MULAI MENDENGAR
            self.is_listening = True
            
            self.voice_status.configure(
                text="🎙️ Mendengar... (Klik Stop untuk berhenti)",
                text_color=COLORS["success"]
            )
            self.btn_mic.configure(
                text="⏹️ Stop Mendengar",
                fg_color=COLORS["danger"],
                hover_color="#E63A4A",
                text_color="white"
            )
            self.voice.mulai_mendengar(callback=self.proses_voice_command)
            self.voice_text.insert("end", "\n🎤 Mendengar... (Katakan 'berhenti' untuk stop)\n")
            self.voice_text.see("end")
            
        else:
            # BERHENTI MENDENGAR
            self.is_listening = False
            
            self.voice_status.configure(
                text="🎙️ Voice Command: Nonaktif",
                text_color=COLORS["text_muted"]
            )
            self.btn_mic.configure(
                text="🎤 Mulai Mendengar",
                fg_color=COLORS["success"],
                hover_color="#00B85A",
                text_color="white"
            )
            self.voice.berhenti_mendengar()
            self.voice_text.insert("end", "\n⏹️ Berhenti mendengar. Klik 'Mulai Mendengar' untuk aktifkan kembali.\n")
            self.voice_text.see("end")
    
    # ============================================
    # VOICE - PROSES COMMAND
    # ============================================
    def proses_voice_command(self, teks):
        """Proses perintah suara dengan lebih cerdas"""
        self.voice_text.insert("end", f"\n🗣️ Kamu: {teks}\n")
        self.voice_text.see("end")
        
        teks_lower = teks.lower()
        
        # PERINTAH BERHENTI / STOP
        stop_commands = ['berhenti', 'stop', 'tutup', 'keluar', 'selesai', 'cukup', 'mati']
        if any(cmd in teks_lower for cmd in stop_commands):
            self.voice_text.insert("end", "🛑 Menghentikan voice command...\n")
            self.voice_text.see("end")
            if self.is_listening:
                self.root.after(100, self._stop_voice_from_command)
            return
        
        # PERINTAH PENGINGAT
        if "ingatkan" in teks_lower or "pengingat" in teks_lower:
            time_match = re.search(r'jam\s*(\d{1,2})(?:\s*:\s*(\d{2}))?', teks_lower)
            if time_match:
                jam = int(time_match.group(1))
                menit = int(time_match.group(2)) if time_match.group(2) else 0
                if 0 <= jam <= 23 and 0 <= menit <= 59:
                    self.entry_reminder_waktu.delete(0, "end")
                    self.entry_reminder_waktu.insert(0, f"{jam:02d}:{menit:02d}")
            
            self.voice_text.insert("end", "📝 Memproses pengingat...\n")
            self.entry_reminder_pesan.delete(0, "end")
            self.entry_reminder_pesan.insert(0, teks)
            self.voice_text.insert("end", "✅ Silakan atur waktu di tab Pengingat atau klik 'Tambah Pengingat'.\n")
            self.voice_text.see("end")
            return
        
        # PERINTAH TANYA MEMORI
        if "apa yang" in teks_lower or "ingat" in teks_lower or "jelaskan" in teks_lower:
            self.input_tanya.delete(0, "end")
            self.input_tanya.insert(0, teks)
            self.voice_text.insert("end", "🔍 Memproses pertanyaan...\n")
            self.voice_text.see("end")
            self.root.after(100, self.tanya_memori)
            return
        
        # PERINTAH SAPAAN / GREETING
        greetings = ['halo', 'hai', 'helo', 'selamat pagi', 'selamat siang', 
                    'selamat sore', 'selamat malam', 'apa kabar', 'apakabar']
        if any(g in teks_lower for g in greetings):
            now = datetime.now()
            hour = now.hour
            
            if hour < 12:
                waktu = "pagi ☀️"
            elif hour < 17:
                waktu = "siang 🌤️"
            elif hour < 20:
                waktu = "sore 🌅"
            else:
                waktu = "malam 🌙"
            
            responses = [
                f"Selamat {waktu}, Emen! Senang mendengar suaramu! 😇",
                f"Halo Emen! Selamat {waktu}! Ada yang bisa aku bantu? ✨",
                f"Wah, senangnya kamu menyapa! Selamat {waktu}, Emen! 💫",
                f"👋 Hai Emen! Semoga {waktu}mu menyenangkan! Ada yang bisa aku bantu?"
            ]
            response = random.choice(responses)
            
            self.voice_text.insert("end", f"😇 AIRAA: {response}\n")
            self.voice_text.see("end")
            return
        
        # PERINTAH TIDAK DIKENALI
        self.voice_text.insert(
            "end",
            "❓ Maaf, perintah tidak dikenali.\n"
            "💡 Coba: 'ingatkan...', 'apa yang...', 'halo', atau 'berhenti'\n"
        )
        self.voice_text.see("end")
    
    # ============================================
    # VOICE - STOP FROM COMMAND
    # ============================================
    def _stop_voice_from_command(self):
        """Hentikan voice dari perintah suara"""
        if self.is_listening:
            self.is_listening = False
            self.voice_status.configure(
                text="🎙️ Voice Command: Nonaktif",
                text_color=COLORS["text_muted"]
            )
            self.btn_mic.configure(
                text="🎤 Mulai Mendengar",
                fg_color=COLORS["success"],
                hover_color="#00B85A",
                text_color="white"
            )
            self.voice.berhenti_mendengar()
            self.voice_text.insert("end", "\n⏹️ Berhenti mendengar (dari perintah suara).\n")
            self.voice_text.see("end")
    
    # ============================================
    # TAMBAH PENGINGAT - NON-BLOCKING
    # ============================================
    def tambah_pengingat(self):
        if not self.reminder:
            messagebox.showwarning("Peringatan", "Modul Reminder tidak tersedia.")
            return
        
        pesan = self.entry_reminder_pesan.get().strip()
        waktu_str = self.entry_reminder_waktu.get().strip()
        
        if not pesan or not waktu_str:
            messagebox.showwarning("Peringatan", "Isi pesan dan waktu pengingat!")
            return
        
        try:
            jam, menit = map(int, waktu_str.split(':'))
            sekarang = datetime.now()
            waktu = datetime(sekarang.year, sekarang.month, sekarang.day, jam, menit)
            
            if waktu < sekarang:
                waktu = waktu.replace(day=waktu.day + 1)
            
            default_repeat = settings.get('reminder.default_repeat', False)
            ulangi = self.reminder_ulangi.get() == 1 or default_repeat
            
            def add_reminder_thread():
                try:
                    reminder = self.reminder.tambah_pengingat(
                        pesan=pesan,
                        waktu=waktu.isoformat(),
                        ulangi=ulangi
                    )
                    if reminder:
                        self.root.after(0, lambda: self._on_reminder_added(waktu))
                    else:
                        self.root.after(0, lambda: messagebox.showerror("Error", "Gagal menambah pengingat!"))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Error: {e}"))
            
            threading.Thread(target=add_reminder_thread, daemon=True).start()
            
            self.entry_reminder_pesan.delete(0, "end")
            self.entry_reminder_waktu.delete(0, "end")
            self.reminder_ulangi.deselect()
            
            messagebox.showinfo("Info", "⏳ Pengingat sedang diproses...")
            
        except ValueError:
            messagebox.showerror("Error", "Format waktu salah! Gunakan HH:MM (contoh: 14:30)")
    
    def _on_reminder_added(self, waktu):
        messagebox.showinfo("Sukses", f"✅ Pengingat ditambahkan!\n{waktu.strftime('%d %B %Y %H:%M')}")
        if self.logger:
            try:
                self.logger.catat_interaksi("reminder_add", "Pengingat ditambahkan")
            except:
                pass
        self.refresh_reminder_list()
    
    # ============================================
    # REFRESH REMINDER LIST
    # ============================================
    def refresh_reminder_list(self):
        for widget in self.reminder_list_frame.winfo_children():
            widget.destroy()
        
        if not self.reminder:
            label = ctk.CTkLabel(
                self.reminder_list_frame,
                text="Modul Reminder tidak tersedia",
                font=ctk.CTkFont(size=13, slant="italic"),
                text_color=COLORS["text_muted"]
            )
            label.pack(pady=20)
            return
        
        reminders = self.reminder.get_reminders_aktif()
        if not reminders:
            label = ctk.CTkLabel(
                self.reminder_list_frame,
                text="Tidak ada pengingat aktif",
                font=ctk.CTkFont(size=13, slant="italic"),
                text_color=COLORS["text_muted"]
            )
            label.pack(pady=20)
            return
        
        for r in reminders:
            frame = ctk.CTkFrame(
                self.reminder_list_frame,
                fg_color=COLORS["bg_medium"],
                corner_radius=8
            )
            frame.pack(fill="x", pady=3, padx=5)
            
            icon = "🔁" if r.get('ulangi', False) else "⏰"
            
            label = ctk.CTkLabel(
                frame,
                text=f"{icon} {r['pesan'][:40]}...",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_primary"]
            )
            label.pack(side="left", padx=10)
            
            waktu = datetime.fromisoformat(r['waktu'])
            label_waktu = ctk.CTkLabel(
                frame,
                text=waktu.strftime("%H:%M"),
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["warning"]
            )
            label_waktu.pack(side="right", padx=10)
            
            btn_hapus = ctk.CTkButton(
                frame,
                text="✕",
                width=30,
                height=30,
                corner_radius=15,
                fg_color=COLORS["danger"],
                hover_color="#E63A4A",
                text_color="white",
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda id=r['id']: self.hapus_pengingat(id)
            )
            btn_hapus.pack(side="right", padx=5)
    
    def hapus_pengingat(self, reminder_id):
        if not self.reminder:
            return
        if messagebox.askyesno("Konfirmasi", "Hapus pengingat ini?"):
            self.reminder.hapus_pengingat(reminder_id)
            self.refresh_reminder_list()
            if self.logger:
                try:
                    self.logger.catat_interaksi("reminder_delete", f"ID: {reminder_id}")
                except:
                    pass
    
    # ============================================
    # JURNAL
    # ============================================
    def refresh_jurnal(self):
        if not self.logger:
            self.jurnal_text.delete("1.0", "end")
            self.jurnal_text.insert("1.0", "Modul Logger tidak tersedia.")
            return
        
        filter_jenis = self.filter_jenis.get()
        if filter_jenis == "Semua":
            filter_jenis = None
        
        entries = self.logger.baca_log_terbaru(limit=50, jenis=filter_jenis)
        
        self.jurnal_text.delete("1.0", "end")
        if not entries:
            self.jurnal_text.insert("1.0", "Belum ada catatan interaksi.")
            return
        
        for entry in reversed(entries):
            waktu = datetime.fromisoformat(entry['waktu']).strftime("%H:%M:%S")
            jenis = entry['jenis']
            konten = entry['konten'][:60]
            
            emoji_map = {
                'sapaan': '💬',
                'tanya_memori': '❓',
                'tanya_memori_result': '📝',
                'belajar_file': '📚',
                'reminder_add': '⏰',
                'reminder_delete': '🗑️',
                'system_start': '🚀',
                'screen_alert': '👁️',
                'audio_capture': '👂'
            }
            emoji = emoji_map.get(jenis, '📌')
            
            line = f"{emoji} [{waktu}] {jenis.upper()}: {konten}\n"
            self.jurnal_text.insert("end", line)
    
    # ============================================
    # ANALYTICS
    # ============================================
    def refresh_statistik(self):
        if not self.analytics:
            self.statistik_label.configure(text="📊 Modul Analytics tidak tersedia.")
            return
        
        stats = self.analytics.get_statistik()
        if stats:
            text = f"""📊 STATISTIK AIRAA

📚 Total pengetahuan: {stats.get('total_memori', 0)} dokumen
💬 Total interaksi: {stats.get('total_interaksi', 0)} kali
🔄 Belajar hari ini: {stats.get('belajar_hari_ini', 0)} file
❓ Pertanyaan hari ini: {stats.get('pertanyaan_hari_ini', 0)} kali
⏰ Pengingat aktif: {stats.get('pengingat_aktif', 0)} 
🎯 Topik favorit: {stats.get('topik_favorit', 'Belum ada data')}

📈 Aktivitas 7 hari terakhir:
{stats.get('aktivitas_mingguan', 'Belum ada data')}"""
            self.statistik_label.configure(text=text)
        else:
            self.statistik_label.configure(text="📊 Belum ada data statistik. Mulai berinteraksi dengan AIRAA!")
    
    # ============================================
    # SENSOR
    # ============================================
    def refresh_sensor_status(self):
        self.sensor_activity.delete("1.0", "end")
        
        activity_text = "📡 AKTIVITAS SENSOR TERBARU\n"
        activity_text += "=" * 40 + "\n\n"
        
        if self.focus_mode:
            activity_text += "🎯 MODE FOKUS: ON (sensor dijeda)\n\n"
        else:
            activity_text += "🎯 MODE FOKUS: OFF (sensor aktif)\n\n"
        
        if self.screen_watcher:
            activity_text += "👁️ SCREEN WATCHER: AKTIF\n"
            context = self.screen_watcher.get_recent_context(limit=3)
            activity_text += f"   {context}\n\n"
        else:
            activity_text += "👁️ Screen Watcher: TIDAK AKTIF\n\n"
        
        if self.audio_watcher:
            activity_text += "👂 AUDIO WATCHER: AKTIF\n"
            audio = self.audio_watcher.get_latest_audio()
            activity_text += f"   {audio if audio else 'Belum ada transkrip'}\n\n"
        else:
            activity_text += "👂 Audio Watcher: TIDAK AKTIF\n\n"
        
        if self.council:
            activity_text += "🧠 ANGELIC COUNCIL: AKTIF (AutoGen + GPU)\n"
        else:
            activity_text += "🧠 Angelic Council: TIDAK AKTIF\n\n"
        
        self.sensor_activity.insert("1.0", activity_text)
    
    # ============================================
    # BACKGROUND SERVICES
    # ============================================
    def muat_pengingat_aktif(self):
        if self.reminder:
            try:
                self.reminder.start_reminder_checker(self.logger)
            except Exception as e:
                print(f"❌ Reminder start error: {e}")
    
    def aktifkan_fitur_otomatis(self):
        if 'jalankan_pemantau' in globals():
            self.watcher_thread = threading.Thread(target=self.mulai_watcher_bg, daemon=True)
            self.watcher_thread.start()
        else:
            self.status_label.configure(text="⚠️ Status Pemantau: TIDAK TERSEDIA", text_color=COLORS["warning"])
            self.status_indicator.configure(text="🟡 LIMITED", text_color=COLORS["warning"])
    
    def mulai_watcher_bg(self):
        try:
            self.status_label.configure(text="📡 Status Pemantau: AKTIF & MENGAWASI", text_color=COLORS["success"])
            self.status_indicator.configure(text="● ONLINE", text_color=COLORS["success"])
            if 'jalankan_pemantau' in globals():
                jalankan_pemantau()
        except Exception as e:
            self.status_label.configure(text=f"❌ Status Pemantau: ERROR - {str(e)}", text_color=COLORS["danger"])
            self.status_indicator.configure(text="● OFFLINE", text_color=COLORS["danger"])
            if self.logger:
                try:
                    self.logger.catat_interaksi("error", str(e))
                except:
                    pass


# ============================================
# RUN
# ============================================
if __name__ == "__main__":
    root = ctk.CTk()
    app = AiraaModernGUI(root)
    root.mainloop()