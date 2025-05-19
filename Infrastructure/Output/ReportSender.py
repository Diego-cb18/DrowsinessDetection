import requests

class ReportSender:
    def __init__(self, backend_url):
        self.backend_url = backend_url

    def send_report(self, json_path):
        with open(json_path, 'rb') as json_file:
            files = {
                'json': ('reporte.json', json_file, 'application/json'),
            }

            try:
                response = requests.post(self.backend_url, files=files)
                print("--> Reporte enviado al backend")
                print("Código:", response.status_code)
                print("Respuesta:", response.json())
            except Exception as e:
                print("-->  Error al enviar el reporte:", str(e))
