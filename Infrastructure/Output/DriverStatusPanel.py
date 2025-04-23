from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_status_panel(eventos, blink_count, eye_state, driver_state, lip_state,
                        ear_valor=None, lip_valor=None, yawn_count=0,
                        head_tilt_ratio=None,
                        head_tilt_progress=False, head_position="Cabeza: -", nod_count=0):
    width, height = 600, 400
    panel = np.ones((height, width, 3), dtype=np.uint8) * 30

    image = Image.fromarray(panel)
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("Merriweather_120pt-Regular.ttf", 30)
    except IOError:
        font = ImageFont.load_default()

    draw.text((20, 150), eye_state, fill=(110, 100, 228), font=font)
    draw.text((20, 120), f'Parpadeos: {blink_count}', fill=(110, 100, 228), font=font)
    draw.text((100, 120), f'Bostezos: {yawn_count}', fill=(228, 153, 110), font=font)
    draw.text((20, 90), f'Conductor: {driver_state}', fill=(255, 255, 255), font=font)
    draw.text((100, 150), lip_state, fill=(228, 153, 110), font=font)

    if ear_valor is not None:
        draw.text((20, 180), f'EAR: {ear_valor:.3f}', fill=(110, 100, 228), font=font)

    if lip_valor is not None:
        draw.text((100, 180), f'Labios: {lip_valor:.2f}', fill=(228, 153, 110), font=font)

    if head_tilt_ratio is not None:
        draw.text((200, 180), f'Inclinación cabeza: {head_tilt_ratio:.2f}', fill=(110, 228, 128), font=font)

    draw.text((200, 210), f'Cabeceo en progreso: {"sí" if head_tilt_progress else "no"}', fill=(110, 228, 128), font=font)
    draw.text((200, 150), head_position, fill=(110, 228, 128), font=font)
    draw.text((200, 120), f'Cabeceos: {nod_count}', fill=(110, 228, 128), font=font)

    return np.array(image)
