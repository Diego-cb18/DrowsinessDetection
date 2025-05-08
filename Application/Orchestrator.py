import time
import cv2
from Infrastructure.Input.CameraCV2 import CameraCV2
from Infrastructure.Input.FaceMeshAdapter import get_landmarks_from_frame
from Infrastructure.Output.DriverStatusPanel import create_status_panel
from Infrastructure.Output.ReportExporter import ReportExporter
from Infrastructure.Output.VideoExporter import VideoExporter
from Domain.SomnolenceEvaluator import SomnolenceEvaluator
from Domain.FaceMetrics import calculate_ear, calculate_lip_openness, calculate_head_tilt_ratio
from Domain.SleepReport import SleepReport

def run_camera_view(camera_index=0):
    camera = CameraCV2(index=camera_index)

    if not camera.is_open():
        print("No se pudo abrir la cámara")
        return
    else:
        print("Cámara abierta correctamente")

    evaluator = SomnolenceEvaluator(
        ear_closing_threshold=0.23,
        ear_opening_threshold=0.26,
        lip_threshold=25,
        min_yawn_duration=4,
        head_tilt_ratio_threshold=0.75,
        head_tilt_min_duration=3
    )

    report = SleepReport()
    exporter = ReportExporter()
    video_exporter = VideoExporter()

    blink_total = 0
    yawn_total = 0
    nod_total = 0
    eventos_globales = []

    recording = False
    recording_start_time = None
    alert_started_time = None
    alert_seconds = 0
    waiting_for_alert = False
    last_recording_ended_time = None

    while True:
        ret, frame = camera.read_frame()
        if not ret:
            print("-> No se pudo leer el fotograma")
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
        yawn_in_progress = False
        rostro_detectado = False

        current_time = time.time()

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

            if evaluator.yawn_start_time:
                duracion_bostezo = current_time - evaluator.yawn_start_time
                if duracion_bostezo >= evaluator.min_yawn_duration:
                    yawn_in_progress = True
                    driver_state = "Bostezo"

            if evaluator.head_down_start_time:
                duracion_cabeceo = current_time - evaluator.head_down_start_time
                if duracion_cabeceo >= evaluator.head_tilt_min_duration:
                    head_tilt_in_progress = True
                    driver_state = "Cabeceo"

            if driver_state in [
                "Parpadeo prolongado",
                "Microsueño leve",
                "Microsueño moderado",
                "Microsueño profundo",
                "Sueño profundo"
            ]:
                alert_started_time = None
                alert_seconds = 0

                if not recording and not waiting_for_alert:
                    nombre_video = video_exporter.start_recording()
                    report.registrar_video(nombre_video)
                    recording = True
                    recording_start_time = current_time
                elif recording:
                    video_seconds = int(current_time - recording_start_time)
                    if video_seconds >= 60:
                        video_exporter.stop_recording()
                        recording = False
                        last_recording_ended_time = current_time
                        waiting_for_alert = True
            elif recording:
                if driver_state == "Alerta":
                    if alert_started_time is None:
                        alert_started_time = current_time
                    else:
                        alert_seconds = int(current_time - alert_started_time)
                        if alert_seconds >= 7:
                            video_exporter.stop_recording()
                            recording = False
                            last_recording_ended_time = current_time
                            waiting_for_alert = True
                else:
                    alert_started_time = None
                    alert_seconds = 0
            elif waiting_for_alert:
                if driver_state == "Alerta":
                    waiting_for_alert = False
                    alert_started_time = None
                    alert_seconds = 0

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

        video_seconds = int(time.time() - recording_start_time) if recording and recording_start_time else 0

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
            nod_count=nod_total,
            yawn_in_progress=yawn_in_progress,
            video_seconds=video_seconds,
            alert_seconds=alert_seconds
        )

        if video_exporter.is_recording():
            frame_resized = cv2.resize(frame, (480, 480))
            panel_resized = cv2.resize(panel, (480, 480))
            combined_frame = cv2.hconcat([frame_resized, panel_resized])
            video_exporter.write_frame(combined_frame)

        cv2.imshow("Vista de cámara", frame)
        cv2.imshow("Estado del conductor", panel)

        if cv2.waitKey(1) & 0xFF == ord('c') or cv2.getWindowProperty('Vista de cámara', cv2.WND_PROP_VISIBLE) < 1:
            break

    if video_exporter.is_recording():
        video_exporter.stop_recording()

    camera.release()
    cv2.destroyAllWindows()
    exporter.export_to_json(report)
