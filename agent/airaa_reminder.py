# airaa_reminder.py - FIXED (No Crash)
import json
import datetime
import threading
import time
import os
from plyer import notification

# Import settings
try:
    from settings_loader import settings
except ImportError:
    class DummySettings:
        def get(self, key, default=None):
            return default
    settings = DummySettings()


class AiraaReminder:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(settings.get('paths.db_dir', "C:\\airaa\\db"), "reminders.json")
            
        self.db_path = db_path
        self.reminders = []
        self.lock = threading.RLock()  # <-- GANTI: RLock untuk reentrant lock
        self.is_running = False
        self.check_interval = settings.get('reminder.check_interval_seconds', 30)
        self.notification_timeout = settings.get('reminder.notification_timeout', 15)
        self.max_reminders = settings.get('reminder.max_reminders', 50)
        self.default_repeat = settings.get('reminder.default_repeat', False)
        self._stop_event = threading.Event()  # <-- TAMBAHKAN: Untuk stop graceful
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.load_reminders()
        
    def load_reminders(self):
        """Load reminders from file"""
        with self.lock:
            try:
                if os.path.exists(self.db_path):
                    with open(self.db_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.reminders = data if isinstance(data, list) else []
                else:
                    self.reminders = []
            except Exception as e:
                print(f"⚠️ Load reminders error: {e}")
                self.reminders = []
            
    def save_reminders(self):
        """Save reminders to file"""
        with self.lock:
            try:
                # Backup dulu
                if os.path.exists(self.db_path):
                    backup_path = self.db_path + ".backup"
                    try:
                        os.replace(self.db_path, backup_path)
                    except:
                        pass
                
                with open(self.db_path, 'w', encoding='utf-8') as f:
                    json.dump(self.reminders, f, indent=2, ensure_ascii=False)
                return True
            except Exception as e:
                print(f"❌ Gagal save reminders: {e}")
                return False
                
    def tambah_pengingat(self, pesan, waktu, ulangi=None):
        """Tambah pengingat baru"""
        if ulangi is None:
            ulangi = self.default_repeat
            
        # Cek limit
        aktif = self.get_reminders_aktif()
        if len(aktif) >= self.max_reminders:
            print(f"⚠️ Max reminders reached ({self.max_reminders})")
            return None
            
        reminder = {
            "id": int(time.time() * 1000),
            "pesan": pesan,
            "waktu": waktu,
            "ulangi": ulangi,
            "aktif": True,
            "created": datetime.datetime.now().isoformat()
        }
        
        with self.lock:
            self.reminders.append(reminder)
            self.save_reminders()
            
        print(f"✅ Pengingat ditambahkan: {pesan[:30]}...")
        return reminder
        
    def hapus_pengingat(self, reminder_id):
        """Hapus pengingat"""
        with self.lock:
            before = len(self.reminders)
            self.reminders = [r for r in self.reminders if r.get('id') != reminder_id]
            if len(self.reminders) < before:
                self.save_reminders()
                print(f"🗑️ Pengingat {reminder_id} dihapus")
            
    def get_reminders_aktif(self):
        """Dapatkan daftar pengingat aktif"""
        with self.lock:
            return [r for r in self.reminders if r.get('aktif', True)]
            
    def get_all_reminders(self):
        """Dapatkan semua pengingat"""
        with self.lock:
            return self.reminders.copy()
            
    def start_reminder_checker(self, logger=None):
        """Start reminder checker thread"""
        if self.is_running:
            return
            
        if not settings.get('reminder.enabled', True):
            print("⏸️ Reminder system disabled in settings")
            return
            
        self.is_running = True
        self._stop_event.clear()
        
        def check_reminders():
            print(f"⏰ Sistem pengingat aktif! (check setiap {self.check_interval}s)")
            while not self._stop_event.is_set():
                try:
                    now = datetime.datetime.now()
                    reminders_to_remove = []
                    
                    with self.lock:
                        for r in self.reminders:
                            if not r.get('aktif', True):
                                continue
                                
                            try:
                                waktu_reminder = datetime.datetime.fromisoformat(r['waktu'])
                                
                                if now >= waktu_reminder:
                                    # Kirim notifikasi
                                    try:
                                        notification.notify(
                                            title="⏰ AIRAA Mengingatkan",
                                            message=r['pesan'],
                                            app_name="AIRAA Core",
                                            timeout=self.notification_timeout
                                        )
                                        print(f"🔔 Reminder triggered: {r['pesan'][:30]}...")
                                    except Exception as e:
                                        print(f"⚠️ Notification error: {e}")
                                    
                                    # Log jika ada logger
                                    if logger:
                                        try:
                                            logger.catat_interaksi("reminder_trigger", r['pesan'], {
                                                "id": r['id']
                                            })
                                        except:
                                            pass
                                    
                                    # Handle repeat
                                    if r.get('ulangi', False):
                                        next_time = waktu_reminder + datetime.timedelta(days=1)
                                        r['waktu'] = next_time.isoformat()
                                        print(f"🔄 Pengingat diulang: {r['pesan'][:30]}...")
                                    else:
                                        r['aktif'] = False
                                        reminders_to_remove.append(r['id'])
                                        
                                    # Save setelah perubahan
                                    self.save_reminders()
                                    
                            except Exception as e:
                                print(f"⚠️ Error processing reminder {r.get('id', 'unknown')}: {e}")
                                
                        # Cleanup reminder yang sudah tidak aktif
                        if reminders_to_remove:
                            self.reminders = [r for r in self.reminders if r.get('aktif', True) or r.get('ulangi', False)]
                            self.save_reminders()
                                
                except Exception as e:
                    print(f"❌ Reminder checker error: {e}")
                    
                time.sleep(self.check_interval)
            
            print("⏰ Sistem pengingat dihentikan")
        
        self._thread = threading.Thread(target=check_reminders, daemon=True)
        self._thread.start()
        return True
        
    def stop_reminder_checker(self):
        """Stop reminder checker"""
        self.is_running = False
        self._stop_event.set()
        if hasattr(self, '_thread') and self._thread:
            self._thread.join(timeout=2)
        print("⏰ Sistem pengingat dihentikan")


if __name__ == "__main__":
    reminder = AiraaReminder()
    reminder.start_reminder_checker()
    
    # Test tambah pengingat
    now = datetime.datetime.now() + datetime.timedelta(seconds=10)
    reminder.tambah_pengingat(
        pesan="Test reminder 10 detik",
        waktu=now.isoformat()
    )
    
    try:
        time.sleep(20)
    except KeyboardInterrupt:
        reminder.stop_reminder_checker()