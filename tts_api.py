import requests
import threading
import time
import logging

class TTSAPIThread:
    def __init__(self, text, lang, speed=1.0, pitch=1.0, progress_callback=None, finished_callback=None):
        self.text = text
        self.lang = lang
        self.speed = speed
        self.pitch = pitch
        self.progress_callback = progress_callback
        self.finished_callback = finished_callback
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        for attempt in range(3):
            try:
                url = f"https://google-tts-converter-sujan.vercel.app/v1/convert?text={self.text}&lang={self.lang}"
                if self.progress_callback:
                    self.progress_callback(10)
                response = requests.get(url, timeout=15)
                if self.progress_callback:
                    self.progress_callback(90)
                if response.status_code == 200:
                    data = response.content
                    if self.progress_callback:
                        self.progress_callback(100)
                    if self.finished_callback:
                        self.finished_callback(data, True)
                    return
                elif response.status_code == 429:  # Quota exceeded
                    if self.finished_callback:
                        self.finished_callback(b'', False)
                    return
                else:
                    if attempt == 2:
                        if self.finished_callback:
                            self.finished_callback(b'', False)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
                if attempt < 2:
                    time.sleep(1)  # Wait before retry
                    continue
                else:
                    if self.finished_callback:
                        self.finished_callback(b'', False)
            except Exception as e:
                logging.error(f"Unexpected TTS API Error: {e}")
                if self.finished_callback:
                    self.finished_callback(b'', False)
                return