import json
from datetime import datetime
import os

class ReportExporter:
    def __init__(self, output_folder="Reports"):
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)

    def export_to_json(self, report_object, filename_prefix="reporte_somnolencia"):
        data = {
            "conductor": report_object.driver_data,
            "reporte_somnolencia": {
                "parpadeos": report_object.blink_count,
                "bostezos": report_object.yawn_count,
                "cabeceos": report_object.nod_count,
                "eventos_criticos": list(report_object.critical_events),
                "videos": report_object.video_filenames  # Lista de nombres de videos
            },
            "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        filename = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.output_folder, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"-> Reporte exportado como: {filepath}")
        return filepath
