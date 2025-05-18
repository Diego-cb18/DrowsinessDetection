import numpy as np
import math

# Calcula el Eye Aspect Ratio (EAR)
def calculate_ear(eye_points):
    p2_p6 = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
    p3_p5 = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
    p1_p4 = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
    ear = (p2_p6 + p3_p5) / (2.0 * p1_p4)
    return ear

# Calcula la distancia vertical entre labios (seguro para listas cortas)
def calculate_lip_openness(lip_points):
    if len(lip_points) >= 2:
        top = np.array(lip_points[0])     # punto superior
        bottom = np.array(lip_points[1])  # punto inferior
        return np.linalg.norm(top - bottom)
    else:
        return 0  # valor neutro si no hay suficientes puntos

# Relación entre inclinación nariz-mentón y frente-nariz
def calculate_head_tilt_ratio(forehead, nose, chin):
    dist_forehead_nose = math.dist(forehead, nose)
    dist_nose_chin = math.dist(nose, chin)
    if dist_forehead_nose == 0:
        return 1  # evita división por cero
    return dist_nose_chin / dist_forehead_nose