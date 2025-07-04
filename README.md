# DrowsinessDetection

Este proyecto implementa un sistema de detección de somnolencia utilizando visión computacional en tiempo real. Está desarrollado en Python y emplea Mediapipe, OpenCV y otros módulos personalizados para emitir alertas auditivas y generar reportes estructurados.

## Estructura del Proyecto

- `Application/`: Lógica principal de orquestación.
- `Domain/`: Entidades y reglas del dominio.
- `Infrastructure/`: Integraciones con hardware, red, y almacenamiento.
- `audio_cache/`: Audios utilizados para alertas.

## Características

- Detección de parpadeos, bostezos, cabeceos y microsueños.
- Grabación de video como evidencia de eventos críticos.
- Exportación de reportes en JSON.
- Integración con backend en Django y almacenamiento en AWS S3.

## Cómo ejecutar

```bash
python Main.py
