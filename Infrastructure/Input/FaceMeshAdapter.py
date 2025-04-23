import cv2
import mediapipe as mp

# Inicializar solo una vez
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

def get_landmarks_from_frame(frame):
    """
    Procesa un frame y devuelve puntos clave del rostro si se detecta.
    """
    height, width, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)

    if not results.multi_face_landmarks:
        return None

    landmarks = results.multi_face_landmarks[0].landmark

    indices = {
        "right_eye": [33, 160, 158, 133, 153, 144],
        "left_eye": [362, 385, 387, 263, 373, 380],
        "lips": [13, 14],
        "forehead": [10],
        "nose": [1],
        "chin": [152]
    }

    points = {}
    for region, ids in indices.items():
        points[region] = [(int(landmarks[i].x * width), int(landmarks[i].y * height)) for i in ids]

    return points
