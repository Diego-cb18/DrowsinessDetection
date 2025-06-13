import requests
import certifi

class ReportSender:
    def __init__(self, backend_url):
        self.backend_url = backend_url

    def send_report(self, json_path):
        with open(json_path, 'rb') as json_file:
            files = {
                'json': ('reporte.json', json_file, 'application/json'),
            }

            try:
                response = requests.post(
                    self.backend_url,
                    files=files,
                    timeout=10,
                    verify=certifi.where()
                )
                print("--> Reporte enviado al backend")
                print("Código:", response.status_code)
                print("Respuesta:", response.json())
                return response
            except requests.exceptions.SSLError as ssl_err:
                print("[ERROR SSL] No se confía en el certificado:", ssl_err)
                return None
            except requests.exceptions.ConnectTimeout:
                print("[ERROR] Tiempo de conexión agotado (timeout)")
                return None
            except Exception as e:
                print("-->  Error al enviar el reporte:", str(e))
                return None
