import json
import os
from pathlib import Path

class AiraaSettings:
    """Manajer konfigurasi AIRAA"""
    
    _instance = None
    _settings = None
    _settings_path = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AiraaSettings, cls).__new__(cls)
            cls._instance._settings_path = os.path.join("C:\\airaa\\config", "settings.json")
            cls._instance._load_settings()
        return cls._instance
    
    def _load_settings(self):
        """Load settings dari file JSON"""
        settings_path = self._settings_path
        
        # Default settings jika file tidak ada
        default_settings = {
            "version": "2.0.0",
            "app_name": "AIRAA - AI Recording Angel Agentic",
            "paths": {
                "base_dir": "C:\\airaa",
                "knowledge_dir": "C:\\airaa\\knowledge",
                "db_dir": "C:\\airaa\\db",
                "logs_dir": "C:\\airaa\\logs",
                "audio_cache": "C:\\airaa\\audio",
                "config_dir": "C:\\airaa\\config"
            },
            "ollama": {
                "enabled": True,
                "base_url": "http://localhost:11434",
                "embedding_model": "nomic-embed-text",
                "chat_model": "qwen2.5:7b-instruct",
                "vision_model": "llava:7b",
                "timeout": 60,
                "retry_attempts": 3,
                "retry_delay": 2
            },
            "memory": {
                "vector_db": "chromadb",
                "max_document_length": 3000,
                "default_results": 3,
                "cache_enabled": True,
                "cache_ttl": 3600,
                "auto_learn_from_knowledge": True,
                "knowledge_extensions": [".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".md", ".py", ".jpg", ".png", ".mp3", ".mp4"]
            },
            "watcher": {
                "enabled": True,
                "watch_path": "C:\\airaa",
                "recursive": True,
                "debounce_seconds": 5,
                "scan_interval": 2,
                "exclude_patterns": ["~$*", "*.tmp", "*.log", "*.cache"],
                "process_knownledge_files": True,
                "audit_python_files": True,
                "supported_extensions": {
                    "documents": [".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".md"],
                    "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
                    "media": [".mp3", ".mp4", ".wav", ".avi", ".mov"],
                    "code": [".py", ".js", ".html", ".css", ".json", ".yaml", ".yml"]
                }
            },
            "proactive": {
                "enabled": True,
                "auto_sapaan": True,
                "sapaan_interval_minutes": 60,
                "active_hours_start": 6,
                "active_hours_end": 22,
                "variations": True,
                "fallback_sapaan": "Selamat pagi/siang/malam, Emen! Aku di sini siap mencatat setiap langkah kebaikanmu hari ini.",
                "notification_timeout": 12,
                "max_daily_sapaan": 10
            },
            "reminder": {
                "enabled": True,
                "check_interval_seconds": 30,
                "notification_timeout": 15,
                "max_reminders": 50,
                "default_repeat": False,
                "sound_enabled": True,
                "sound_file": "C:\\airaa\\audio\\reminder.wav"
            },
            "voice": {
                "enabled": True,
                "listening_timeout": 5,
                "phrase_time_limit": 10,
                "language": "id-ID",
                "ambient_noise_adjustment": 1.0,
                "auto_calibrate": True,
                "tts_enabled": False,
                "tts_voice": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ID-ID_HANYA_11.0"
            },
            "analytics": {
                "enabled": True,
                "track_interactions": True,
                "track_file_changes": True,
                "analytics_retention_days": 30,
                "generate_daily_report": True,
                "report_time": "23:59"
            },
            "logger": {
                "enabled": True,
                "log_level": "INFO",
                "max_entries_per_file": 1000,
                "log_formats": ["json", "text"],
                "auto_archive": True,
                "archive_after_days": 7,
                "include_metadata": True
            },
            "gui": {
                "theme": "System",
                "color_theme": "blue",
                "window_width": 700,
                "window_height": 650,
                "min_width": 600,
                "min_height": 500,
                "font_family": "Helvetica",
                "font_size": 13,
                "auto_refresh_interval": 5,
                "show_notifications": True
            },
            "llm": {
                "temperature": 0.7,
                "max_tokens": 500,
                "top_p": 0.9,
                "top_k": 40,
                "repeat_penalty": 1.1,
                "context_window": 2048,
                "system_prompt": "Kamu adalah AIRAA (Artificial Intelligence Recording Angel Agentic), malaikat penjaga digital yang bijak, hangat, dan selalu siap membantu Emen dalam segala hal."
            },
            "features": {
                "rag_enabled": True,
                "multimodal_learning": True,
                "code_audit": True,
                "web_learning": True,
                "proactive_suggestions": True,
                "voice_commands": True,
                "daily_summary": True,
                "auto_backup": False,
                "backup_interval_days": 7
            },
            "security": {
                "allowed_paths": ["C:\\airaa", "C:\\Users"],
                "blocked_paths": ["C:\\Windows", "C:\\Program Files"],
                "max_file_size_mb": 100,
                "scan_external_media": False,
                "require_confirmation_for_delete": True
            }
        }
        
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge dengan default
                    self._settings = self._merge_dict(default_settings, loaded)
                    print("✅ Settings loaded successfully")
            else:
                self._settings = default_settings
                # Buat default settings
                os.makedirs(os.path.dirname(settings_path), exist_ok=True)
                with open(settings_path, 'w', encoding='utf-8') as f:
                    json.dump(default_settings, f, indent=2, ensure_ascii=False)
                print("📝 Default settings created")
        except Exception as e:
            print(f"❌ Error loading settings: {e}")
            self._settings = default_settings
            
        # Validasi settings
        from settings_validator import SettingsValidator
        errors = SettingsValidator.validate(self._settings)
        if errors:
            print("⚠️ Settings validation warnings:")
            for error in errors:
                print(f"   - {error}")
            # Repair jika diperlukan
            self._settings = SettingsValidator.repair(self._settings)
            
    def _merge_dict(self, default, custom):
        """Merge dua dictionary secara rekursif"""
        result = default.copy()
        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dict(result[key], value)
            else:
                result[key] = value
        return result
        
    def get(self, key_path, default=None):
        """Dapatkan nilai dari settings dengan path (contoh: 'ollama.chat_model')"""
        keys = key_path.split('.')
        value = self._settings
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key_path, value):
        """Set nilai di settings (tidak permanen)"""
        keys = key_path.split('.')
        target = self._settings
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value
        
    def save(self):
        """Simpan settings ke file"""
        try:
            with open(self._settings_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error saving settings: {e}")
            return False
            
    def reload(self):
        """Reload settings dari file"""
        self._load_settings()
        
    @property
    def all_settings(self):
        return self._settings

# Singleton instance
settings = AiraaSettings()

if __name__ == "__main__":
    # Test
    s = AiraaSettings()
    print(f"Ollama URL: {s.get('ollama.base_url')}")
    print(f"Chat Model: {s.get('ollama.chat_model')}")
    print(f"All settings: {s.all_settings}")