import os
import platform
import threading
import time
import tempfile
from gtts import gTTS
from pygame import mixer

class AudioAlert:
    def __init__(self):
        self.beep_active = False
        self.beep_thread = None
        mixer.init()

    def _beep_loop(self):
        start_time = time.time()
        while self.beep_active:
            elapsed = int(time.time() - start_time)

            # Ajustes dinámicos pero más suaves
            freq = min(800 + elapsed * 20, 1200)             # Ligeramente más agudo con el tiempo
            duration = min(0.8 + elapsed * 0.1, 1.5)         # Empieza con beeps largos (~0.8s)
            interval = max(0.3 - elapsed * 0.02, 0.05)         # Tiempo entre beeps

            if platform.system() == "Windows":
                import winsound
                winsound.Beep(freq, int(duration * 1000))
            else:
                os.system(f'play -nq -t alsa synth {duration} sine {freq}')

            time.sleep(interval)


    def start_beep(self):
        if not self.beep_active:
            self.beep_active = True
            self.beep_thread = threading.Thread(target=self._beep_loop, daemon=True)
            self.beep_thread.start()

    def stop_beep(self):
        self.beep_active = False
        if self.beep_thread is not None:
            self.beep_thread.join()
            self.beep_thread = None

    def play_voice_alert(self, text):
        try:
            tts = gTTS(text=text, lang='es')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                filepath = fp.name
                tts.save(filepath)

            mixer.music.load(filepath)
            mixer.music.play()

            while mixer.music.get_busy():
                time.sleep(0.1)

            mixer.music.unload()
            os.remove(filepath)
        except Exception as e:
            print(f"Error reproduciendo mensaje de voz: {e}")
