import os
import time
from threading import Thread

def cleanup_old_files(directory: str, max_age_hours: int = 1):
    """Remove files older than max_age_hours from directory"""
    try:
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > max_age_seconds:
                    try:
                        os.remove(filepath)
                        print(f"Cleaned up old file: {filename}")
                    except Exception as e:
                        print(f"Error removing file {filename}: {e}")
    except Exception as e:
        print(f"Error during cleanup: {e}")

def start_background_cleanup(directory: str, interval_hours: int = 1):
    """Start background thread for periodic cleanup"""
    def cleanup_worker():
        while True:
            cleanup_old_files(directory)
            time.sleep(interval_hours * 3600)
    
    cleanup_thread = Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()
    return cleanup_thread
