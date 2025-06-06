import os
os.environ["SDL_AUDIODRIVER"] = "alsa"
import platform
import threading
import time
from pygame import mixer

class AudioAlert:
    def __init__(self):
        self.beep_active = False
        self.voice_playing = False
        self.beep_thread = None
        self.voice_thread = None
        try:
            mixer.init()
        except Exception as e:
            print(f"[AudioAlert] ERROR al inicializar mixer: {e}")

        os.makedirs("audio_cache", exist_ok=True)

    def _beep_loop(self):
        start_time = time.time()
        while self.beep_active:
            elapsed = int(time.time() - start_time)
            freq = min(800 + elapsed * 20, 1200)
            duration = min(0.8 + elapsed * 0.1, 1.5)
            interval = max(0.3 - elapsed * 0.02, 0.05)

            if platform.system() == "Windows":
                import winsound
                winsound.Beep(freq, int(duration * 1000))
            else:
                os.system(f'play -nq -t alsa synth {duration} sine {freq}')
            time.sleep(interval)

    def _play_voice(self, event_key, duration_secs):
        try:
            self.voice_playing = True
            parts = []

            if event_key == "conductor_no_detectado":
                path = os.path.join("audio_cache", "conductor_no_detectado.mp3")
                parts = [path]
            else:
                path1 = os.path.join("audio_cache", f"parte1_{event_key}.mp3")
                path2 = os.path.join("audio_cache", "segundos", f"{duration_secs}.mp3")
                path3 = os.path.join("audio_cache", "parte3.mp3")
                parts = [path1, path2, path3]

            for part in parts:
                if not self.voice_playing:
                    break
                if not os.path.exists(part):
                    print(f"[AudioAlert] Archivo faltante: {part}")
                    continue
                mixer.music.load(part)
                mixer.music.play()
                while mixer.music.get_busy():
                    if not self.voice_playing:
                        mixer.music.stop()
                        break
                    time.sleep(0.1)
                mixer.music.unload()

            self.voice_playing = False

        except Exception as e:
            print(f"[AudioAlert] Error de voz: {e}")
            self.voice_playing = False

    # relacion 
    
    def start_alert(self):
        self.stop_voice()  # Prioridad al beep
        if not self.beep_active:
            self.beep_active = True
            self.beep_thread = threading.Thread(target=self._beep_loop, daemon=True)
            self.beep_thread.start()

    def stop_alert(self):
        self.beep_active = False
        if self.beep_thread:
            self.beep_thread.join()
            self.beep_thread = None

    def start_voice(self, event_key, duration_secs):
        self.stop_alert()  # Se detiene el beep
        self.stop_voice()  # Por si acaso hay voz en curso
        self.voice_thread = threading.Thread(
            target=self._play_voice, args=(event_key, duration_secs), daemon=True
        )
        self.voice_thread.start()

    def stop_voice(self):
        self.voice_playing = False
        if self.voice_thread and self.voice_thread.is_alive():
            self.voice_thread.join(timeout=0.5)
        self.voice_thread = None