import os
import time
import shutil
import threading
import json
from Infrastructure.Utils.NetworkUtils import is_connected
from Infrastructure.Output.VideoUploader import VideoUploader
from Infrastructure.Output.ReportSender import ReportSender
from Infrastructure.Output.ReportExporter import ReportExporter

class PendingResender:
    def __init__(self, check_interval=10):
        self.check_interval = check_interval
        self.running = False
        self.thread = threading.Thread(target=self._loop, daemon=True)

    def start(self):
        print("[RESENDER] Servicio de reenvío automático iniciado...")
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def _loop(self):
        while self.running:
            if not self._hay_pendientes():
                time.sleep(self.check_interval)
                continue

            print("[RESENDER] Hay archivos pendientes. Verificando conexión...")
            if is_connected():
                print("[RESENDER] Conexión detectada. Reintentando envío...")
                self._reenviar_pendientes()
            else:
                print("[RESENDER] Sin conexión. Esperando...")
            time.sleep(self.check_interval)

    def _hay_pendientes(self):
        return bool(os.listdir("PendingVideos")) and bool(os.listdir("PendingReports"))

    def _reenviar_pendientes(self):
        video_uploader = VideoUploader()
        report_sender = ReportSender("https://vigiadrowsyapp.duckdns.org/reports/upload/")
        exporter = ReportExporter()

        for report_file in os.listdir("PendingReports"):
            report_path = os.path.join("PendingReports", report_file)

            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                    video_filenames = report_data.get("reporte_somnolencia", {}).get("videos", [])
                    if not video_filenames:
                        print(f"[RESENDER][ERROR] El reporte {report_file} no contiene nombres de video.")
                        continue
            except Exception as e:
                print(f"[RESENDER][ERROR] No se pudo leer {report_file}: {e}")
                continue

            print(f"[RESENDER] Procesando y subiendo videos: {video_filenames}")

            try:
                video_urls = video_uploader.process_and_upload_all(video_filenames, folder="PendingVideos")
                if "reporte_somnolencia" in report_data:
                    report_data["reporte_somnolencia"]["url_videos"] = video_urls
                else:
                    print(f"[RESENDER][ERROR] Estructura inválida en {report_file}: falta 'reporte_somnolencia'")
                    continue

                # Guardar nuevo JSON actualizado en carpeta Reports/
                updated_json_path = os.path.join("Reports", report_file)
                with open(updated_json_path, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=4, ensure_ascii=False)

                # Enviar al backend
                response = report_sender.send_report(updated_json_path)

                if response and response.status_code == 201:
                    print(f"[RESENDER] Reporte reenviado correctamente: {report_file}")

                    # Mover videos
                    for video_name in video_filenames:
                        try:
                            shutil.move(
                                os.path.join("PendingVideos", video_name),
                                os.path.join("Videos", video_name)
                            )
                        except Exception as ve:
                            print(f"[RESENDER][ERROR] No se pudo mover el video {video_name}: {ve}")

                    # Borrar JSON de pendientes
                    os.remove(report_path)
                else:
                    print(f"[RESENDER][ERROR] Fallo al reenviar {report_file}. Código: {response.status_code if response else 'Sin respuesta'}")

            except Exception as e:
                print(f"[RESENDER][ERROR] Fallo al procesar {report_file}: {e}")
