"""
Protocolo BLE para Sensores Xsens DOT (Movella DOT).

Define UUIDs, servicios, características y formato de datos
según especificaciones oficiales de Xsens/Movella.
"""

import struct
import numpy as np
from typing import Tuple
from enum import Enum


# ==================== UUIDs DE SERVICIOS Y CARACTERÍSTICAS ====================

# Base UUID de Xsens DOT
XSENS_DOT_BASE_UUID = "1517{:04x}-4947-11e9-8646-d663bd873d93"

# ===== Servicio de Información del Dispositivo (0x1000) =====
DEVICE_INFORMATION_SERVICE = XSENS_DOT_BASE_UUID.format(0x1000)
DEVICE_INFORMATION_CONTROL = XSENS_DOT_BASE_UUID.format(0x1001)
DEVICE_INFORMATION_REPORT = XSENS_DOT_BASE_UUID.format(0x1002)

# ===== Servicio de Batería (0x3000) =====
BATTERY_SERVICE = XSENS_DOT_BASE_UUID.format(0x3000)
BATTERY_CONTROL = XSENS_DOT_BASE_UUID.format(0x3001)
BATTERY_REPORT = XSENS_DOT_BASE_UUID.format(0x3002)

# ===== Servicio de Medición (0x2000) - PRINCIPAL =====
MEASUREMENT_SERVICE = XSENS_DOT_BASE_UUID.format(0x2000)
MEASUREMENT_CONTROL = XSENS_DOT_BASE_UUID.format(0x2001)  # Escritura
MEASUREMENT_MEDIUM_PAYLOAD = XSENS_DOT_BASE_UUID.format(0x2002)  # Notificación
MEASUREMENT_LONG_PAYLOAD = XSENS_DOT_BASE_UUID.format(0x2003)  # Notificación
MEASUREMENT_SHORT_PAYLOAD = XSENS_DOT_BASE_UUID.format(0x2004)  # Notificación

# ===== Servicio de Configuración (0x4000) =====
CONFIGURATION_SERVICE = XSENS_DOT_BASE_UUID.format(0x4000)
CONFIGURATION_CONTROL = XSENS_DOT_BASE_UUID.format(0x4001)
CONFIGURATION_REPORT = XSENS_DOT_BASE_UUID.format(0x4002)

# ===== Servicio de Mensajes (0x7000) =====
MESSAGE_SERVICE = XSENS_DOT_BASE_UUID.format(0x7000)
MESSAGE_CONTROL = XSENS_DOT_BASE_UUID.format(0x7001)
MESSAGE_NOTIFICATION = XSENS_DOT_BASE_UUID.format(0x7002)
MESSAGE_ACK_NOTIFICATION = XSENS_DOT_BASE_UUID.format(0x7003)


# ==================== MODOS DE SALIDA DE DATOS ====================

class OutputMode(Enum):
    """Modos de salida de datos del sensor."""
    COMPLETE_QUATERNION = 1  # Cuaternión + aceleración + velocidad angular libre
    COMPLETE_EULER = 2  # Ángulos de Euler + aceleración + velocidad angular libre
    EXTENDED_QUATERNION = 3  # Cuaternión + aceleración + velocidad angular + mag
    EXTENDED_EULER = 4  # Euler + aceleración + velocidad angular + mag
    RATE_QUANTITIES = 5  # Velocidad angular + aceleración
    RATE_QUANTITIES_WITH_MAG = 6  # Velocidad angular + aceleración + mag
    CUSTOM_MODE_1 = 7
    CUSTOM_MODE_2 = 8
    CUSTOM_MODE_3 = 9


# ==================== COMANDOS DE CONTROL ====================

class ControlCommand:
    """Comandos de control para el sensor."""

    # Comandos de medición
    START_MEASUREMENT = bytes([0x01, 0x01])
    STOP_MEASUREMENT = bytes([0x01, 0x00])

    # Comandos de configuración
    SET_OUTPUT_RATE = bytes([0x03])  # Seguido por byte de frecuencia
    SET_OUTPUT_MODE = bytes([0x02])  # Seguido por byte de modo

    # Comandos de batería
    GET_BATTERY_LEVEL = bytes([0x02, 0x01])

    # Comandos de información
    GET_DEVICE_INFO = bytes([0x01, 0x01])
    GET_FIRMWARE_VERSION = bytes([0x01, 0x02])


# ==================== FRECUENCIAS DE MUESTREO ====================

class SampleRate(Enum):
    """Frecuencias de muestreo disponibles."""
    RATE_1_HZ = 1
    RATE_4_HZ = 4
    RATE_10_HZ = 10
    RATE_12_HZ = 12
    RATE_15_HZ = 15
    RATE_20_HZ = 20
    RATE_30_HZ = 30
    RATE_60_HZ = 60
    RATE_120_HZ = 120


# ==================== PARSEO DE DATOS ====================

def parse_complete_quaternion_payload(data: bytes) -> dict:
    """
    Parsea el payload del modo Complete Quaternion.

    Formato (20 bytes):
    - Timestamp (4 bytes, uint32, ms)
    - Quaternion W (4 bytes, float)
    - Quaternion X (4 bytes, float)
    - Quaternion Y (4 bytes, float)
    - Quaternion Z (4 bytes, float)

    Siguiente paquete (12 bytes):
    - Free Acceleration X, Y, Z (3 × 4 bytes, float, m/s²)
    - Angular Velocity X, Y, Z (3 × 4 bytes, float, rad/s)

    Args:
        data: Bytes del payload

    Returns:
        Diccionario con los datos parseados
    """
    if len(data) < 20:
        raise ValueError(f"Payload muy corto: {len(data)} bytes (esperado ≥20)")

    # Timestamp en milisegundos
    timestamp_ms = struct.unpack('<I', data[0:4])[0]
    timestamp_s = timestamp_ms / 1000.0

    # Cuaternión (w, x, y, z)
    quat_w = struct.unpack('<f', data[4:8])[0]
    quat_x = struct.unpack('<f', data[8:12])[0]
    quat_y = struct.unpack('<f', data[12:16])[0]
    quat_z = struct.unpack('<f', data[16:20])[0]

    result = {
        'timestamp': timestamp_s,
        'quaternion': np.array([quat_w, quat_x, quat_y, quat_z])
    }

    # Si hay datos adicionales (aceleración + velocidad angular)
    if len(data) >= 44:  # 20 + 12 + 12
        # Aceleración libre (sin gravedad)
        acc_x = struct.unpack('<f', data[20:24])[0]
        acc_y = struct.unpack('<f', data[24:28])[0]
        acc_z = struct.unpack('<f', data[28:32])[0]

        # Velocidad angular
        gyr_x = struct.unpack('<f', data[32:36])[0]
        gyr_y = struct.unpack('<f', data[36:40])[0]
        gyr_z = struct.unpack('<f', data[40:44])[0]

        result['acceleration'] = np.array([acc_x, acc_y, acc_z])
        result['angular_velocity'] = np.array([gyr_x, gyr_y, gyr_z])

    return result


def parse_rate_quantities_payload(data: bytes) -> dict:
    """
    Parsea el payload del modo Rate Quantities.

    Formato (28 bytes):
    - Timestamp (4 bytes, uint32, ms)
    - Angular Velocity X, Y, Z (3 × 4 bytes, float, rad/s)
    - Acceleration X, Y, Z (3 × 4 bytes, float, m/s²)

    Args:
        data: Bytes del payload

    Returns:
        Diccionario con los datos parseados
    """
    if len(data) < 28:
        raise ValueError(f"Payload muy corto: {len(data)} bytes (esperado 28)")

    # Timestamp
    timestamp_ms = struct.unpack('<I', data[0:4])[0]
    timestamp_s = timestamp_ms / 1000.0

    # Velocidad angular
    gyr_x = struct.unpack('<f', data[4:8])[0]
    gyr_y = struct.unpack('<f', data[8:12])[0]
    gyr_z = struct.unpack('<f', data[12:16])[0]

    # Aceleración
    acc_x = struct.unpack('<f', data[16:20])[0]
    acc_y = struct.unpack('<f', data[20:24])[0]
    acc_z = struct.unpack('<f', data[24:28])[0]

    return {
        'timestamp': timestamp_s,
        'angular_velocity': np.array([gyr_x, gyr_y, gyr_z]),
        'acceleration': np.array([acc_x, acc_y, acc_z])
    }


def parse_short_payload(data: bytes) -> dict:
    """
    Parsea el payload corto (Short Payload).

    Usado para modos de baja latencia.

    Args:
        data: Bytes del payload

    Returns:
        Diccionario con los datos parseados
    """
    if len(data) < 4:
        raise ValueError(f"Payload muy corto: {len(data)} bytes")

    # Timestamp
    timestamp_ms = struct.unpack('<I', data[0:4])[0]
    timestamp_s = timestamp_ms / 1000.0

    result = {'timestamp': timestamp_s}

    # El resto depende del modo configurado
    # Por simplicidad, asumimos formato similar a rate quantities
    if len(data) >= 28:
        return parse_rate_quantities_payload(data)

    return result


def quaternion_to_euler(q: np.ndarray) -> np.ndarray:
    """
    Convierte cuaternión a ángulos de Euler (roll, pitch, yaw).

    Args:
        q: Cuaternión [w, x, y, z]

    Returns:
        Ángulos de Euler [roll, pitch, yaw] en radianes
    """
    w, x, y, z = q

    # Roll (rotación sobre X)
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = np.arctan2(sinr_cosp, cosr_cosp)

    # Pitch (rotación sobre Y)
    sinp = 2 * (w * y - z * x)
    if abs(sinp) >= 1:
        pitch = np.copysign(np.pi / 2, sinp)  # Usar 90° si fuera de rango
    else:
        pitch = np.arcsin(sinp)

    # Yaw (rotación sobre Z)
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = np.arctan2(siny_cosp, cosy_cosp)

    return np.array([roll, pitch, yaw])


def euler_to_quaternion(euler: np.ndarray) -> np.ndarray:
    """
    Convierte ángulos de Euler a cuaternión.

    Args:
        euler: Ángulos de Euler [roll, pitch, yaw] en radianes

    Returns:
        Cuaternión [w, x, y, z]
    """
    roll, pitch, yaw = euler

    cy = np.cos(yaw * 0.5)
    sy = np.sin(yaw * 0.5)
    cp = np.cos(pitch * 0.5)
    sp = np.sin(pitch * 0.5)
    cr = np.cos(roll * 0.5)
    sr = np.sin(roll * 0.5)

    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy

    return np.array([w, x, y, z])


# ==================== INFORMACIÓN DEL SENSOR ====================

SENSOR_INFO = {
    "name_prefix": "Xsens DOT",
    "manufacturer": "Movella (formerly Xsens)",
    "max_range_acc": 16,  # g
    "max_range_gyro": 2000,  # deg/s
    "resolution_acc": 0.000488,  # g/LSB (16-bit)
    "resolution_gyro": 0.061,  # deg/s/LSB (16-bit)
    "supported_rates": [1, 4, 10, 12, 15, 20, 30, 60, 120],  # Hz
    "battery_capacity": 150,  # mAh
    "typical_battery_life": "6-12 hours",  # Depende de la frecuencia
}


# ==================== FUNCIONES DE AYUDA ====================

def create_set_output_rate_command(rate_hz: int) -> bytes:
    """
    Crea comando para configurar frecuencia de muestreo.

    Args:
        rate_hz: Frecuencia deseada en Hz

    Returns:
        Bytes del comando
    """
    valid_rates = SENSOR_INFO["supported_rates"]
    if rate_hz not in valid_rates:
        raise ValueError(f"Frecuencia inválida: {rate_hz} Hz. Válidas: {valid_rates}")

    rate_code = {
        1: 0x00,
        4: 0x01,
        10: 0x02,
        12: 0x03,
        15: 0x04,
        20: 0x05,
        30: 0x06,
        60: 0x07,
        120: 0x08
    }[rate_hz]

    return ControlCommand.SET_OUTPUT_RATE + bytes([rate_code])


def create_set_output_mode_command(mode: OutputMode) -> bytes:
    """
    Crea comando para configurar modo de salida.

    Args:
        mode: Modo de salida deseado

    Returns:
        Bytes del comando
    """
    return ControlCommand.SET_OUTPUT_MODE + bytes([mode.value])


def is_xsens_dot_device(device_name: str) -> bool:
    """
    Verifica si un dispositivo BLE es un Xsens DOT.

    Args:
        device_name: Nombre del dispositivo

    Returns:
        True si es un Xsens DOT
    """
    if not device_name:
        return False

    keywords = ["Xsens DOT", "XSENS DOT", "xsens dot", "Movella DOT"]
    return any(keyword in device_name for keyword in keywords)
