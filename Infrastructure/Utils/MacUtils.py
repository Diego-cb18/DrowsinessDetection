import uuid

def get_mac_address():
    mac_num = hex(uuid.getnode()).replace('0x', '').zfill(12).upper()
    mac = ':'.join(mac_num[i:i+2] for i in range(0, 12, 2))
    return mac
