import cv2

class CameraCV2:
    def __init__(self, index=0):
        self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # ← importante
        print(f"Intentando abrir cámara {index} con CAP_DSHOW...")

    def is_open(self):
        return self.cap.isOpened()

    def read_frame(self):
        return self.cap.read()

    def release(self):
        self.cap.release()
