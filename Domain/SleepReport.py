class SleepReport:
    def __init__(self):
        self.driver_data = {
            "nombre": "",
            "apellidos": "",
            "dni": "",
            "telefono": "",
            "tipo_vehiculo": "",
            "placa": ""
        }

        self.blink_count = 0
        self.yawn_count = 0
        self.nod_count = 0
        self.critical_events = []

    def agregar_parpadeo(self):
        self.blink_count += 1

    def agregar_bostezo(self):
        self.yawn_count += 1

    def agregar_cabeceo(self):
        self.nod_count += 1

    def registrar_evento_critico(self, descripcion_evento):
        if descripcion_evento not in self.critical_events:
            self.critical_events.append(descripcion_evento)

    def asignar_datos_conductor(self, nombre, apellidos, dni, telefono, tipo_vehiculo, placa):
        self.driver_data.update({
            "nombre": nombre,
            "apellidos": apellidos,
            "dni": dni,
            "telefono": telefono,
            "tipo_vehiculo": tipo_vehiculo,
            "placa": placa
        })
