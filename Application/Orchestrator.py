import time
import cv2
from Infrastructure.Input.CameraCV2 import CameraCV2
from Infrastructure.Input.FaceMeshAdapter import get_landmarks_from_frame
from Infrastructure.Output.DriverStatusPanel import create_status_panel
from Infrastructure.Output.ReportExporter import ReportExporter
from Domain.SomnolenceEvaluator import SomnolenceEvaluator
from Domain.FaceMetrics import calculate_ear, calculate_lip_openness, calculate_head_tilt_ratio
from Domain.SleepReport import SleepReport

def run_camera_view(camera_index=0):
    camera = CameraCV2(index=camera_index)

    if not camera.is_open():
        print("❌ No se pudo abrir la cámara")
        return
    else:
        print("✅ Cámara abierta correctamente")

    evaluator = SomnolenceEvaluator(
        ear_closing_threshold=0.23,
        ear_opening_threshold=0.26,
        lip_threshold=25
    )

    report = SleepReport()
    exporter = ReportExporter()

    blink_total = 0
    yawn_total = 0
    nod_total = 0
    eventos_globales = []

    while True:
        ret, frame = camera.read_frame()
        if not ret:
            print("❌ No se pudo leer el fotograma")
            break

        landmarks = get_landmarks_from_frame(frame)

        eye_state = "No detectado"
        lip_state = "No detectado"
        driver_state = "No detectado"
        ear_average = None
        lip_distance = None
        head_tilt_ratio = None
        head_position = "Cabeza: -"
        head_tilt_in_progress = False
        rostro_detectado = False

        if landmarks is not None:
            rostro_detectado = True

            for region in landmarks:
                for (x, y) in landmarks[region]:
                    cv2.circle(frame, (x, y), 2, (255, 255, 255), -1)

            prepared = {
                "left_eye": landmarks["left_eye"],
                "right_eye": landmarks["right_eye"],
                "lips": landmarks["lips"],
                "forehead_nose_chin": (
                    landmarks["forehead"][0],
                    landmarks["nose"][0],
                    landmarks["chin"][0]
                )
            }

            ear_izq = calculate_ear(prepared["left_eye"])
            ear_der = calculate_ear(prepared["right_eye"])
            ear_average = (ear_izq + ear_der) / 2

            if evaluator.eye_closed:
                eye_state = "Ojos abiertos" if ear_average > evaluator.ear_opening_threshold else "Ojos cerrados"
            else:
                eye_state = "Ojos cerrados" if ear_average < evaluator.ear_closing_threshold else "Ojos abiertos"

            lip_distance = calculate_lip_openness(prepared["lips"])
            lip_state = "Labios abiertos" if lip_distance > evaluator.lip_threshold else "Labios cerrados"

            forehead, nose, chin = prepared["forehead_nose_chin"]
            head_tilt_ratio = calculate_head_tilt_ratio(forehead, nose, chin)
            head_position = "Cabeza: Abajo" if head_tilt_ratio < evaluator.head_tilt_ratio_threshold else "Cabeza: Arriba"

            current_time = time.time()

            # === ESTADO EN TIEMPO REAL ===
            driver_state = "Alerta"

            if evaluator.eye_closed_time:
                duracion = current_time - evaluator.eye_closed_time
                if duracion >= 10:
                    driver_state = "Microsueño profundo"
                elif duracion >= 7:
                    driver_state = "Microsueño moderado"
                elif duracion >= 5:
                    driver_state = "Microsueño leve"
                elif duracion >= 3:
                    driver_state = "Parpadeo prolongado"

            if evaluator.yawn_in_progress and evaluator.yawn_start_time:
                duracion_bostezo = current_time - evaluator.yawn_start_time
                if duracion_bostezo >= evaluator.min_yawn_duration:
                    driver_state = "Bostezo"

            if evaluator.head_down_start_time:
                duracion_cabeceo = current_time - evaluator.head_down_start_time
                if duracion_cabeceo >= evaluator.head_tilt_min_duration:
                    head_tilt_in_progress = True
                    driver_state = "Cabeceo"

            eventos = evaluator.evaluate(prepared)

            for e in eventos:
                eventos_globales.append(e)

                if e.type.startswith("parpadeo") or e.type.startswith("microsueño"):
                    blink_total += 1
                    report.agregar_parpadeo()

                elif e.type == "bostezo":
                    yawn_total += 1
                    report.agregar_bostezo()

                elif e.type == "cabeceo":
                    nod_total += 1
                    report.agregar_cabeceo()

                if e.type in [
                    "parpadeo prolongado",
                    "microsueño leve",
                    "microsueño moderado",
                    "microsueño profundo",
                    "sueño profundo",
                    "parpadeos constantes",
                    "bostezos constantes",
                    "cabeceos constantes"
                ]:
                    report.registrar_evento_critico(f"{e.type} ({e.description})")

        else:
            driver_state = "No detectado"

        panel = create_status_panel(
            eventos_globales,
            blink_total,
            eye_state,
            driver_state,
            lip_state,
            ear_valor=ear_average,
            lip_valor=lip_distance,
            yawn_count=yawn_total,
            head_tilt_ratio=head_tilt_ratio,
            head_tilt_progress=head_tilt_in_progress,
            head_position=head_position,
            nod_count=nod_total
        )

        cv2.imshow("Vista de cámara", frame)
        cv2.imshow("Estado del conductor", panel)

        if cv2.waitKey(1) & 0xFF == ord('c') or cv2.getWindowProperty('Vista de cámara', cv2.WND_PROP_VISIBLE) < 1:
            break

    camera.release()
    cv2.destroyAllWindows()
    exporter.export_to_json(report)
