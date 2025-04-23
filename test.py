import cv2

camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("❌ No se pudo abrir la cámara")
    exit()
else:
    print("✅ Cámara detectada correctamente")

while True:
    ret, frame = camera.read()

    if not ret or frame is None:
        print("⚠️ No se pudo leer el fotograma o está vacío")
        break

    cv2.imshow('Vista de camara', frame)

    if cv2.waitKey(1) & 0xFF == ord('c') or cv2.getWindowProperty('Vista de camara', cv2.WND_PROP_VISIBLE) < 1:
        break

camera.release()
cv2.destroyAllWindows()
