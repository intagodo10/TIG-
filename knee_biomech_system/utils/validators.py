"""
Validadores de datos y entrada del sistema.

Proporciona funciones de validación para asegurar
la integridad de los datos del sistema.
"""

import re
from typing import Optional, Tuple
import numpy as np

from utils.logger import get_logger

logger = get_logger(__name__)


def validate_patient_id(patient_id: str) -> Tuple[bool, Optional[str]]:
    """
    Valida el formato del ID de paciente.

    Args:
        patient_id: ID del paciente

    Returns:
        Tuple (es_valido, mensaje_error)
    """
    if not patient_id or not isinstance(patient_id, str):
        return False, "El ID de paciente no puede estar vacío"

    if len(patient_id) < 3:
        return False, "El ID debe tener al menos 3 caracteres"

    if len(patient_id) > 20:
        return False, "El ID no puede exceder 20 caracteres"

    # Solo alfanuméricos, guiones y guiones bajos
    if not re.match(r'^[A-Za-z0-9_-]+$', patient_id):
        return False, "El ID solo puede contener letras, números, guiones y guiones bajos"

    return True, None


def validate_patient_data(name: str, age: int, mass: float, height: float) -> Tuple[bool, Optional[str]]:
    """
    Valida datos antropométricos del paciente.

    Args:
        name: Nombre del paciente
        age: Edad en años
        mass: Masa corporal en kg
        height: Altura en metros

    Returns:
        Tuple (es_valido, mensaje_error)
    """
    # Validar nombre
    if not name or not isinstance(name, str):
        return False, "El nombre no puede estar vacío"

    if len(name) < 2:
        return False, "El nombre debe tener al menos 2 caracteres"

    # Validar edad
    if not isinstance(age, int) or age < 0 or age > 150:
        return False, "La edad debe estar entre 0 y 150 años"

    # Validar masa
    if not isinstance(mass, (int, float)) or mass <= 0 or mass > 500:
        return False, "La masa debe estar entre 0 y 500 kg"

    # Validar altura
    if not isinstance(height, (int, float)) or height <= 0 or height > 3.0:
        return False, "La altura debe estar entre 0 y 3.0 metros"

    return True, None


def validate_imu_data(quaternion: np.ndarray, acceleration: np.ndarray,
                     angular_velocity: np.ndarray) -> Tuple[bool, Optional[str]]:
    """
    Valida datos de sensor IMU.

    Args:
        quaternion: Array [w, x, y, z]
        acceleration: Array [x, y, z]
        angular_velocity: Array [x, y, z]

    Returns:
        Tuple (es_valido, mensaje_error)
    """
    # Validar cuaternión
    if quaternion.shape != (4,):
        return False, "El cuaternión debe tener 4 componentes"

    # Verificar normalización (debe ser ~ 1.0)
    quat_norm = np.linalg.norm(quaternion)
    if not (0.9 < quat_norm < 1.1):
        return False, f"Cuaternión no normalizado (norma = {quat_norm:.3f})"

    # Validar aceleración
    if acceleration.shape != (3,):
        return False, "La aceleración debe tener 3 componentes"

    # Verificar rangos razonables (±200 m/s² = ~20g)
    if np.any(np.abs(acceleration) > 200):
        return False, "Aceleración fuera de rango razonable (>200 m/s²)"

    # Validar velocidad angular
    if angular_velocity.shape != (3,):
        return False, "La velocidad angular debe tener 3 componentes"

    # Verificar rangos razonables (±35 rad/s = ~2000 °/s)
    if np.any(np.abs(angular_velocity) > 35):
        return False, "Velocidad angular fuera de rango razonable (>35 rad/s)"

    return True, None


def validate_force_data(fx: float, fy: float, fz: float,
                       mx: float, my: float, mz: float) -> Tuple[bool, Optional[str]]:
    """
    Valida datos de plataforma de fuerza.

    Args:
        fx, fy, fz: Fuerzas en N
        mx, my, mz: Momentos en Nm

    Returns:
        Tuple (es_valido, mensaje_error)
    """
    # Verificar tipos
    values = [fx, fy, fz, mx, my, mz]
    if not all(isinstance(v, (int, float)) for v in values):
        return False, "Todos los valores deben ser numéricos"

    # Verificar rangos de fuerza (±10000 N = ±1000 kg)
    if any(abs(f) > 10000 for f in [fx, fy, fz]):
        return False, "Fuerza fuera de rango razonable (>10000 N)"

    # Verificar rangos de momento (±1000 Nm)
    if any(abs(m) > 1000 for m in [mx, my, mz]):
        return False, "Momento fuera de rango razonable (>1000 Nm)"

    return True, None


def validate_time_series(time: np.ndarray, data: np.ndarray,
                        expected_rate: float = None) -> Tuple[bool, Optional[str]]:
    """
    Valida una serie temporal.

    Args:
        time: Vector de tiempo
        data: Vector de datos
        expected_rate: Frecuencia esperada en Hz (opcional)

    Returns:
        Tuple (es_valido, mensaje_error)
    """
    # Verificar longitudes
    if len(time) != len(data):
        return False, "Los vectores de tiempo y datos deben tener la misma longitud"

    if len(time) < 2:
        return False, "Se requieren al menos 2 puntos de datos"

    # Verificar monotonía del tiempo
    if not np.all(np.diff(time) > 0):
        return False, "El vector de tiempo debe ser estrictamente creciente"

    # Verificar frecuencia si se especifica
    if expected_rate is not None:
        actual_rate = len(time) / (time[-1] - time[0])
        rate_error = abs(actual_rate - expected_rate) / expected_rate

        if rate_error > 0.1:  # 10% de tolerancia
            return False, f"Frecuencia incorrecta: esperada {expected_rate} Hz, actual {actual_rate:.1f} Hz"

    # Verificar que no haya NaN o Inf
    if np.any(np.isnan(data)) or np.any(np.isinf(data)):
        return False, "Los datos contienen valores NaN o Infinito"

    return True, None


def validate_sync_quality(time_offset: float, max_offset: float = 0.01) -> Tuple[bool, Optional[str]]:
    """
    Valida la calidad de sincronización.

    Args:
        time_offset: Offset temporal calculado (segundos)
        max_offset: Offset máximo permitido (segundos)

    Returns:
        Tuple (es_valido, mensaje_error)
    """
    if abs(time_offset) > max_offset:
        return False, f"Offset de sincronización muy grande: {time_offset*1000:.1f} ms (máx: {max_offset*1000:.1f} ms)"

    return True, None


def validate_metrics(metrics: dict) -> Tuple[bool, Optional[str]]:
    """
    Valida que las métricas calculadas sean razonables.

    Args:
        metrics: Diccionario de métricas

    Returns:
        Tuple (es_valido, mensaje_error)
    """
    # Verificar ROM
    if 'rom_flexion' in metrics:
        rom = metrics['rom_flexion']
        if not (0 < rom < 180):
            return False, f"ROM de flexión fuera de rango fisiológico: {rom:.1f}°"

    # Verificar momentos (normalizados por masa)
    if 'peak_flexion_moment' in metrics:
        moment = abs(metrics['peak_flexion_moment'])
        if moment > 10.0:  # 10 Nm/kg es extremadamente alto
            return False, f"Momento de flexión excesivo: {moment:.2f} Nm/kg"

    # Verificar GRF (normalizada)
    if 'peak_vertical_grf_normalized' in metrics:
        grf = metrics['peak_vertical_grf_normalized']
        if not (0.1 < grf < 10.0):  # Entre 0.1 y 10 veces peso corporal
            return False, f"GRF fuera de rango razonable: {grf:.2f} × PC"

    return True, None


def validate_file_path(filepath: str, must_exist: bool = True,
                      allowed_extensions: list = None) -> Tuple[bool, Optional[str]]:
    """
    Valida una ruta de archivo.

    Args:
        filepath: Ruta al archivo
        must_exist: Si True, el archivo debe existir
        allowed_extensions: Lista de extensiones permitidas (ej: ['.xlsx', '.csv'])

    Returns:
        Tuple (es_valido, mensaje_error)
    """
    from pathlib import Path

    if not filepath:
        return False, "La ruta de archivo no puede estar vacía"

    path = Path(filepath)

    # Verificar existencia
    if must_exist and not path.exists():
        return False, f"El archivo no existe: {filepath}"

    # Verificar extensión
    if allowed_extensions is not None:
        if path.suffix.lower() not in allowed_extensions:
            return False, f"Extensión no permitida. Use: {', '.join(allowed_extensions)}"

    # Verificar que no sea directorio
    if path.exists() and path.is_dir():
        return False, "La ruta es un directorio, no un archivo"

    return True, None


def validate_exercise_config(exercise_type: str, duration: float,
                            repetitions: int) -> Tuple[bool, Optional[str]]:
    """
    Valida configuración de ejercicio.

    Args:
        exercise_type: Tipo de ejercicio
        duration: Duración en segundos
        repetitions: Número de repeticiones

    Returns:
        Tuple (es_valido, mensaje_error)
    """
    from config.settings import EXERCISES

    # Verificar tipo de ejercicio
    if exercise_type not in EXERCISES:
        return False, f"Tipo de ejercicio inválido: {exercise_type}"

    config = EXERCISES[exercise_type]

    # Verificar duración
    min_dur, max_dur = config['duration_range']
    if not (min_dur <= duration <= max_dur):
        return False, f"Duración debe estar entre {min_dur} y {max_dur} segundos"

    # Verificar repeticiones
    min_rep, max_rep = config['repetitions_range']
    if not (min_rep <= repetitions <= max_rep):
        return False, f"Repeticiones deben estar entre {min_rep} y {max_rep}"

    return True, None


def check_signal_quality(data: np.ndarray, threshold: float = 0.6) -> Tuple[float, bool]:
    """
    Evalúa la calidad de una señal.

    Args:
        data: Vector de datos
        threshold: Umbral de calidad (0-1)

    Returns:
        Tuple (calidad, es_aceptable)
    """
    # Calcular métricas de calidad
    nan_ratio = np.sum(np.isnan(data)) / len(data)
    zero_ratio = np.sum(data == 0) / len(data)

    # Calcular varianza (señal con poca variación = baja calidad)
    variance = np.nanvar(data)
    variance_score = min(variance / 100, 1.0)  # Normalizar

    # Score de calidad combinado
    quality = (1 - nan_ratio) * (1 - zero_ratio * 0.5) * variance_score

    is_acceptable = quality >= threshold

    return quality, is_acceptable


# Función principal de validación
def validate_all(patient_id: str, patient_data: dict, imu_data: dict,
                force_data: dict) -> Tuple[bool, list]:
    """
    Valida todos los aspectos de una sesión.

    Args:
        patient_id: ID del paciente
        patient_data: Datos del paciente
        imu_data: Datos de IMU
        force_data: Datos de fuerza

    Returns:
        Tuple (es_valido, lista_de_errores)
    """
    errors = []

    # Validar ID
    valid, error = validate_patient_id(patient_id)
    if not valid:
        errors.append(f"ID de paciente: {error}")

    # Validar datos del paciente
    if patient_data:
        valid, error = validate_patient_data(
            patient_data.get('name', ''),
            patient_data.get('age', 0),
            patient_data.get('mass', 0),
            patient_data.get('height', 0)
        )
        if not valid:
            errors.append(f"Datos del paciente: {error}")

    # Más validaciones según sea necesario...

    is_valid = len(errors) == 0

    if is_valid:
        logger.info("✓ Validación completa exitosa")
    else:
        logger.warning(f"⚠ Validación falló con {len(errors)} errores")
        for error in errors:
            logger.warning(f"  - {error}")

    return is_valid, errors
