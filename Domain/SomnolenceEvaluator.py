from Domain.FaceMetrics import calculate_ear, calculate_lip_openness, calculate_head_tilt_ratio
from Domain.Events import create_event
import time

class SomnolenceEvaluator:
    def __init__(self, ear_closing_threshold, ear_opening_threshold,
                 lip_threshold, min_yawn_duration,
                 head_tilt_ratio_threshold, head_tilt_min_duration):
        self.ear_closing_threshold = ear_closing_threshold
        self.ear_opening_threshold = ear_opening_threshold
        self.lip_threshold = lip_threshold
        self.min_yawn_duration = min_yawn_duration
        self.head_tilt_ratio_threshold = head_tilt_ratio_threshold
        self.head_tilt_min_duration = head_tilt_min_duration

        self.eye_closed = False
        self.eye_closed_time = None

        self.yawn_in_progress = False
        self.yawn_start_time = None

        self.head_down_in_progress = False
        self.head_down_start_time = None

        self.last_head_down_duration = 0

    def evaluate(self, landmarks):
        events = []
        current_time = time.time()

        # === PARPADEO / MICROSUEÑOS ===
        ear = (calculate_ear(landmarks["left_eye"]) + calculate_ear(landmarks["right_eye"])) / 2

        if not self.eye_closed:
            if ear < self.ear_closing_threshold:
                self.eye_closed = True
                self.eye_closed_time = current_time
        else:
            if ear > self.ear_opening_threshold:
                eye_duration = current_time - self.eye_closed_time if self.eye_closed_time else 0
                self.eye_closed = False

                if 10 <= eye_duration < 15 and self.last_head_down_duration >= 5:
                    detalle = f"Microsueño profundo + Cabeceo prolongado - {eye_duration:.1f}s + {self.last_head_down_duration:.1f}s"
                    events.append(create_event("sueño profundo", detalle))
                else:
                    if eye_duration < 3:
                        detalle = f"Ojos cerrados < 3s - {eye_duration:.1f} segundos"
                        events.append(create_event("parpadeo", detalle))
                    if 3 <= eye_duration < 5:
                        detalle = f"Ojos cerrados 3 a 5 segundos - {eye_duration:.1f} segundos"
                        events.append(create_event("parpadeo prolongado", detalle))
                    elif 5 <= eye_duration < 7:
                        detalle = f"Ojos cerrados 5 a 7segundos - {eye_duration:.1f} segundos"
                        events.append(create_event("microsueño leve", detalle))
                    elif 7 <= eye_duration < 10:
                        detalle = f"Ojos cerrados 7 a 10 segundos - {eye_duration:.1f} segundos"
                        events.append(create_event("microsueño moderado", detalle))
                    elif 10 <= eye_duration < 15:
                        detalle = f"Ojos cerrados 10 a 15 segundos - {eye_duration:.1f} segundos"
                        events.append(create_event("microsueño profundo", detalle))

                self.eye_closed_time = None

        # === BOSTEZO ===
        lip_distance = calculate_lip_openness(landmarks["lips"])
        if lip_distance > self.lip_threshold:
            if not self.yawn_in_progress:
                self.yawn_in_progress = True
                self.yawn_start_time = current_time
        else:
            if self.yawn_in_progress and self.yawn_start_time is not None:
                yawn_duration = current_time - self.yawn_start_time
                if yawn_duration >= self.min_yawn_duration:
                    detalle = f"Apertura de labios >= {self.min_yawn_duration}s - {yawn_duration:.1f} segundos"
                    events.append(create_event("bostezo", detalle))
            self.yawn_in_progress = False
            self.yawn_start_time = None

        # === CABECEO ===
        forehead, nose, chin = landmarks["forehead_nose_chin"]
        tilt_ratio = calculate_head_tilt_ratio(forehead, nose, chin)

        if tilt_ratio < self.head_tilt_ratio_threshold:
            if not self.head_down_in_progress:
                self.head_down_in_progress = True
                self.head_down_start_time = current_time
        else:
            if self.head_down_in_progress:
                head_down_duration = current_time - self.head_down_start_time if self.head_down_start_time else 0
                self.last_head_down_duration = head_down_duration
                if head_down_duration >= self.head_tilt_min_duration:
                    detalle = f"Inclinación cabeza > {self.head_tilt_ratio_threshold:.1f} durante {head_down_duration:.1f}s"
                    events.append(create_event("cabeceo", detalle))
                self.head_down_in_progress = False
                self.head_down_start_time = None

        return events

    def is_head_tilt_active(self):
        return self.head_down_in_progress
