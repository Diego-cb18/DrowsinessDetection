import cv2
import platform

class CameraCV2:
    def __init__(self, index=0):
        self.index = index
        self.cap = self._initialize_camera(index)

    def _initialize_camera(self, index):
        system = platform.system()
        if system == "Windows":
            print(f"Intentando abrir cámara {index} con CAP_DSHOW (Windows)...")
            return cv2.VideoCapture(index, cv2.CAP_DSHOW)
        else:
            print(f"Intentando abrir cámara {index} sin CAP_DSHOW ({system})...")
            return cv2.VideoCapture(index)

    def is_open(self):
        return self.cap.isOpened()

    def read_frame(self):
        return self.cap.read()

    def release(self):
        self.cap.release()
