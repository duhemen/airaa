import json
import os
from pathlib import Path

class SettingsValidator:
    @staticmethod
    def validate(settings):
        """Validasi settings dan return list of errors"""
        errors = []
        warnings = []
        
        # Cek path required
        required_paths = ['base_dir', 'knowledge_dir', 'db_dir', 'logs_dir']
        paths = settings.get('paths', {})
        for path_key in required_paths:
            path = paths.get(path_key)
            if not path:
                errors.append(f"Path '{path_key}' tidak diset")
            elif not os.path.exists(path):
                warnings.append(f"Path '{path_key}' tidak ditemukan: {path} (akan dibuat otomatis)")
                
        # Cek Ollama
        ollama = settings.get('ollama', {})
        if ollama.get('enabled', True):
            base_url = ollama.get('base_url')
            if not base_url:
                errors.append("Ollama base_url tidak diset")
            elif not base_url.startswith('http'):
                warnings.append(f"Ollama base_url tidak valid: {base_url}")
                
        # Cek model
        required_models = ['chat_model', 'embedding_model']
        for model in required_models:
            if not ollama.get(model):
                errors.append(f"Model '{model}' tidak diset")
                
        # Cek watcher
        watcher = settings.get('watcher', {})
        watch_path = watcher.get('watch_path')
        if watch_path and not os.path.exists(watch_path):
            warnings.append(f"Watch path tidak ditemukan: {watch_path}")
            
        # Cek GUI
        gui = settings.get('gui', {})
        if gui.get('window_width', 0) < 200:
            warnings.append("Window width terlalu kecil (< 200)")
        if gui.get('window_height', 0) < 200:
            warnings.append("Window height terlalu kecil (< 200)")
            
        return errors, warnings
        
    @staticmethod
    def repair(settings):
        """Perbaiki settings yang rusak dengan default values"""
        # Pastikan paths ada
        if 'paths' not in settings:
            settings['paths'] = {}
            
        default_paths = {
            'base_dir': 'C:\\airaa',
            'knowledge_dir': 'C:\\airaa\\knowledge',
            'db_dir': 'C:\\airaa\\db',
            'logs_dir': 'C:\\airaa\\logs',
            'audio_cache': 'C:\\airaa\\audio',
            'config_dir': 'C:\\airaa\\config'
        }
        
        for key, value in default_paths.items():
            if key not in settings['paths'] or not settings['paths'][key]:
                settings['paths'][key] = value
                
        # Pastikan ollama ada
        if 'ollama' not in settings:
            settings['ollama'] = {}
            
        default_ollama = {
            'enabled': True,
            'base_url': 'http://localhost:11434',
            'embedding_model': 'nomic-embed-text',
            'chat_model': 'qwen2.5:7b-instruct',
            'vision_model': 'llava:7b',
            'timeout': 60,
            'retry_attempts': 3,
            'retry_delay': 2
        }
        
        for key, value in default_ollama.items():
            if key not in settings['ollama']:
                settings['ollama'][key] = value
                
        # Pastikan gui ada
        if 'gui' not in settings:
            settings['gui'] = {}
            
        default_gui = {
            'theme': 'System',
            'color_theme': 'blue',
            'window_width': 700,
            'window_height': 650,
            'min_width': 600,
            'min_height': 500,
            'font_family': 'Helvetica',
            'font_size': 13,
            'auto_refresh_interval': 5,
            'show_notifications': True
        }
        
        for key, value in default_gui.items():
            if key not in settings['gui']:
                settings['gui'][key] = value
                
        return settings
        
    @staticmethod
    def create_default_settings():
        """Buat settings default lengkap"""
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
                "audit_python_files": True
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
                "tts_enabled": False
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
        return default_settings

if __name__ == "__main__":
    # Test validator
    test_settings = {
        "paths": {
            "base_dir": "C:\\airaa"
        }
    }
    errors, warnings = SettingsValidator.validate(test_settings)
    print("Errors:", errors)
    print("Warnings:", warnings)
    
    repaired = SettingsValidator.repair(test_settings)
    print("Repaired:", repaired.keys())