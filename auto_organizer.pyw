import os
import sys
import time
from pathlib import Path
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

# 1. PAKSA PATH KE USER PROFILE (Penting untuk Windows Startup)
USER_HOME = Path(os.environ["USERPROFILE"])
TRACKED_DIR = USER_HOME / "Downloads"
LOG_FILE = USER_HOME / "auto_organizer.log"

# Fungsi untuk mencetak log ke file karena tidak ada terminal
def write_log(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

DESTINATIONS = {
    "Dokumen": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".csv"],
    "Gambar": [".jpg", ".jpeg", ".png", ".gif", ".svg"],
    "Audio": [".mp3", ".wav", ".flac"],
    "Video": [".mp4", ".mkv", ".avi"],
    "Arsip": [".zip", ".rar", ".7z", ".tar"]
}

class FileHandler(FileSystemEventHandler):
    def process_file(self, event_path):
        file_path = Path(event_path)

        if not file_path.exists() or file_path.is_dir():
            return
        if file_path.suffix.lower() in [".tmp", ".crdownload", ".part", ".download"]:
            return

        file_ext = file_path.suffix.lower()

        for category, extensions in DESTINATIONS.items():
            if file_ext in extensions:
                target_folder = TRACKED_DIR / category
                target_folder.mkdir(exist_ok=True)
                new_path = target_folder / file_path.name

                time.sleep(2)
                max_retries = 8
                for attempt in range(max_retries):
                    try:
                        file_path.rename(new_path)
                        write_log(f"BERHASIL: {file_path.name} -> {category}/")
                        return
                    except PermissionError:
                        time.sleep(2)
                    except Exception as e:
                        write_log(f"ERROR {file_path.name}: {e}")
                        return

    def on_created(self, event):
        self.process_file(event.src_path)

    def on_modified(self, event):
        self.process_file(event.src_path)

    def on_moved(self, event):
        self.process_file(event.dest_path)

if __name__ == "__main__":
    write_log("=== Service Auto Organizer Dimulai ===")
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(TRACKED_DIR), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()