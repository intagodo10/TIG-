"""
Configuración general del Sistema de Análisis Biomecánico de Rodilla.

Este módulo contiene todos los parámetros configurables del sistema,
incluyendo frecuencias de muestreo, ubicaciones de sensores, umbrales
de alertas, y configuraciones de procesamiento de señales.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple

# ==================== RUTAS DEL PROYECTO ====================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
RESULTS_DIR = DATA_DIR / "results"
MODELS_DIR = DATA_DIR / "models"
ASSETS_DIR = BASE_DIR / "assets"
LOGS_DIR = BASE_DIR / "logs"

# Crear directorios si no existen
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, RESULTS_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ==================== CONFIGURACIÓN DE SENSORES ====================

# Sensores IMU (Xsens DOT)
IMU_CONFIG = {
    "num_sensors": 7,
    "sampling_rate": 60,  # Hz
    "locations": [
        "pelvis",
        "femur_right",
        "femur_left",
        "tibia_right",
        "tibia_left",
        "foot_right",
        "foot_left"
    ],
    "orientation_format": "quaternion",  # quaternion, euler
    "output_data": ["quaternion", "acceleration", "angular_velocity"],
    "bluetooth_timeout": 10,  # segundos
    "connection_retry": 3,
    "calibration_duration": 5,  # segundos
    "signal_quality_threshold": 70  # porcentaje (0-100)
}

# Plataforma de Fuerza (Valkyria)
FORCE_PLATFORM_CONFIG = {
    "sampling_rate": 1000,  # Hz
    "dimensions": (0.60, 0.40),  # metros (ancho, largo)
    "output_channels": ["Fx", "Fy", "Fz", "Mx", "My", "Mz"],
    "excel_import": True,
    "excel_columns": {
        "time": "Time (s)",
        "fx": "Fx (N)",
        "fy": "Fy (N)",
        "fz": "Fz (N)",
        "mx": "Mx (Nm)",
        "my": "My (Nm)",
        "mz": "Mz (Nm)"
    },
    "calibration_required": True,
    "zero_threshold": 5.0  # Newtons
}

# ==================== SINCRONIZACIÓN ====================

SYNC_CONFIG = {
    "target_frequency": 100,  # Hz - frecuencia común para sincronización
    "interpolation_method": "cubic",  # linear, cubic, quadratic
    "alignment_method": "cross_correlation",
    "max_time_offset": 0.5,  # segundos - máximo desfase permitido
    "sync_error_threshold": 0.01,  # segundos (10 ms)
    "use_movement_onset": True,
    "onset_threshold": 10.0  # N para fuerza vertical
}

# ==================== PROCESAMIENTO DE SEÑALES ====================

SIGNAL_PROCESSING = {
    "filter_type": "butterworth",
    "filter_order": 4,
    "cutoff_frequencies": {
        "imu_acc": 20,  # Hz
        "imu_gyro": 15,  # Hz
        "force": 50  # Hz
    },
    "filter_direction": "forward-backward",  # filtfilt
    "remove_gravity": True,
    "gravity_value": 9.81,  # m/s²
    "detect_events": True,
    "event_detection_method": "threshold"
}

# ==================== OPENSIM ====================

OPENSIM_CONFIG = {
    "model_file": "gait2392_simbody.osim",
    "model_path": MODELS_DIR / "gait2392_simbody.osim",
    "use_scaled_model": True,
    "scaling_method": "anthropometric",
    "ik_accuracy": 1e-5,
    "ik_constraint_weight": 20.0,
    "id_lowpass_cutoff": 6,  # Hz
    "coordinate_names": {
        "knee_flex_r": "knee_angle_r",
        "knee_flex_l": "knee_angle_l",
        "knee_add_r": "knee_adduction_r",
        "knee_add_l": "knee_adduction_l",
        "knee_rot_r": "knee_rotation_r",
        "knee_rot_l": "knee_rotation_l"
    }
}

# ==================== EJERCICIOS DE REHABILITACIÓN ====================

EXERCISES = {
    "squat": {
        "name": "Sentadilla",
        "duration_range": (10, 60),  # segundos
        "repetitions_range": (5, 20),
        "expected_rom": (60, 100),  # grados
        "expected_grf": (0.8, 1.5),  # × peso corporal
        "expected_moment": (1.5, 2.5),  # Nm/kg
        "instructions": "Realizar sentadilla controlada manteniendo la espalda recta"
    },
    "cmj": {
        "name": "Countermovement Jump",
        "duration_range": (2, 5),  # segundos por salto
        "repetitions_range": (3, 10),
        "expected_rom": (80, 120),  # grados
        "expected_grf_takeoff": (2.0, 3.5),  # × peso corporal
        "expected_grf_landing": (2.5, 5.0),  # × peso corporal
        "expected_jump_height": (0.20, 0.45),  # metros
        "instructions": "Saltar con contra-movimiento, despegar con ambos pies"
    },
    "squat_jump": {
        "name": "Squat Jump",
        "duration_range": (2, 5),  # segundos por salto
        "repetitions_range": (3, 10),
        "expected_rom": (90, 110),  # grados
        "expected_grf_takeoff": (2.5, 4.0),  # × peso corporal
        "expected_grf_landing": (3.0, 6.0),  # × peso corporal
        "expected_jump_height": (0.15, 0.40),  # metros
        "instructions": "Desde posición de sentadilla, saltar sin contra-movimiento"
    }
}

# ==================== MÉTRICAS Y VALIDACIÓN ====================

METRICS_CONFIG = {
    "kinematic_metrics": [
        "rom_flexion",
        "max_flexion",
        "min_flexion",
        "peak_angular_velocity",
        "peak_angular_acceleration"
    ],
    "dynamic_metrics": [
        "peak_flexion_moment",
        "peak_extension_moment",
        "peak_abduction_moment",
        "peak_power",
        "work"
    ],
    "force_metrics": [
        "peak_vertical_grf",
        "peak_ap_grf",
        "peak_ml_grf",
        "loading_rate",
        "impulse",
        "contact_time",
        "flight_time"
    ],
    "symmetry_metrics": [
        "rom_symmetry",
        "moment_symmetry",
        "grf_symmetry"
    ],
    "normalize_by_mass": True,
    "normalize_by_height": False
}

VALIDATION_THRESHOLDS = {
    "rmse_kinematics_excellent": 5.0,  # grados
    "rmse_kinematics_acceptable": 10.0,  # grados
    "rmse_dynamics_excellent": 0.10,  # 10%
    "rmse_dynamics_acceptable": 0.20,  # 20%
    "icc_poor": 0.50,
    "icc_moderate": 0.75,
    "icc_good": 0.90
}

# ==================== SISTEMA DE ALERTAS ====================

ALERT_THRESHOLDS = {
    "rom_min": 60,  # grados
    "rom_max": 130,  # grados
    "moment_max": 2.5,  # Nm/kg
    "max_knee_moment": 3.5,  # Nm/kg
    "grf_squat_max": 3.0,  # × peso corporal
    "grf_landing_max": 6.0,  # × peso corporal
    "loading_rate_max": 100,  # BW/s (body weights por segundo)
    "max_loading_rate": 75,  # BW/s
    "max_angular_velocity": 500,  # deg/s
    "asymmetry_max": 15,  # porcentaje
    "moderate_asymmetry": 10,  # %
    "severe_asymmetry": 20,  # %
    "signal_quality_min": 60  # porcentaje
}

ALERT_LEVELS = {
    "info": {"color": "#4a9eff", "icon": "ℹ"},
    "warning": {"color": "#ffd93d", "icon": "⚠"},
    "critical": {"color": "#ff6b6b", "icon": "⛔"}
}

# ==================== VALORES DE REFERENCIA (Literatura) ====================

REFERENCE_VALUES = {
    # Rangos normales de movimiento articular
    "knee_flexion_rom": (0, 135),  # grados (Norkin & White, 2016)
    "hip_flexion_rom": (0, 120),  # grados
    "ankle_dorsiflexion_rom": (-20, 30),  # grados

    # Ejercicios específicos
    "squat": {
        "rom_knee": {"mean": 75, "std": 10, "range": (60, 90), "unit": "°"},
        "moment_peak": {"mean": 2.0, "std": 0.5, "range": (1.5, 2.5), "unit": "Nm/kg"},
        "grf_peak": {"mean": 1.2, "std": 0.3, "range": (0.8, 1.5), "unit": "BW"}
    },
    "cmj": {
        "jump_height": {"mean": 0.32, "std": 0.08, "range": (0.20, 0.45), "unit": "m"},
        "grf_takeoff": {"mean": 2.8, "std": 0.5, "range": (2.0, 3.5), "unit": "BW"},
        "grf_landing": {"mean": 3.8, "std": 0.8, "range": (2.5, 5.0), "unit": "BW"},
        "contact_time": {"mean": 450, "std": 100, "range": (300, 600), "unit": "ms"}
    },
    "squat_jump": {
        "jump_height": {"mean": 0.28, "std": 0.08, "range": (0.15, 0.40), "unit": "m"},
        "grf_takeoff": {"mean": 3.2, "std": 0.6, "range": (2.5, 4.0), "unit": "BW"},
        "grf_landing": {"mean": 4.5, "std": 1.0, "range": (3.0, 6.0), "unit": "BW"}
    }
}

# ==================== CONFIGURACIÓN DE BASE DE DATOS ====================

DATABASE_CONFIG = {
    "type": "sqlite",
    "name": "knee_biomech.db",
    "path": BASE_DIR / "knee_biomech.db",
    "echo": False,  # SQL logging
    "backup_enabled": True,
    "backup_frequency": "daily"
}

# ==================== CONFIGURACIÓN DE LOGGING ====================

LOGGING_CONFIG = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "file_enabled": True,
    "file_name": "system.log",
    "file_path": LOGS_DIR / "system.log",
    "max_file_size": 10 * 1024 * 1024,  # 10 MB
    "backup_count": 5
}

# ==================== CONFIGURACIÓN DE REPORTES ====================

REPORT_CONFIG = {
    "formats": ["pdf", "excel", "csv"],
    "default_format": "pdf",
    "include_logo": True,
    "logo_path": ASSETS_DIR / "images" / "logo_uan.png",
    "template_path": BASE_DIR / "templates",
    "output_path": RESULTS_DIR,
    "auto_timestamp": True,
    "include_graphs": True,
    "graph_dpi": 300,
    "page_size": "letter",  # letter, A4
    "margins": (2.5, 2.5, 2.5, 2.5)  # cm (top, right, bottom, left)
}

# ==================== CONFIGURACIÓN DE INTERFAZ ====================

UI_CONFIG = {
    "window_title": "Sistema de Análisis Biomecánico de Rodilla - UAN",
    "window_size": (1400, 900),
    "min_window_size": (1200, 700),
    "fullscreen": False,
    "resizable": True,
    "fps_refresh": 30,  # Hz para gráficos en tiempo real
    "plot_buffer_size": 1000,  # puntos máximos en gráficos en tiempo real
    "auto_save": True,
    "auto_save_interval": 300,  # segundos (5 minutos)
    "language": "es",  # español
    "date_format": "%d/%m/%Y",
    "time_format": "%H:%M:%S"
}

# ==================== CONSTANTES FÍSICAS ====================

PHYSICAL_CONSTANTS = {
    "gravity": 9.81,  # m/s²
    "air_density": 1.225,  # kg/m³
    "body_segments": {
        "pelvis": {"mass_ratio": 0.142, "length_ratio": None},
        "thigh": {"mass_ratio": 0.100, "length_ratio": 0.245},
        "shank": {"mass_ratio": 0.0465, "length_ratio": 0.246},
        "foot": {"mass_ratio": 0.0145, "length_ratio": 0.152}
    }
}

# ==================== FUNCIONES AUXILIARES ====================

def get_exercise_config(exercise_type: str) -> Dict:
    """
    Obtiene la configuración de un ejercicio específico.

    Args:
        exercise_type: Tipo de ejercicio ('squat', 'cmj', 'squat_jump')

    Returns:
        Diccionario con configuración del ejercicio
    """
    return EXERCISES.get(exercise_type, {})


def get_reference_values(exercise_type: str) -> Dict:
    """
    Obtiene los valores de referencia de literatura para un ejercicio.

    Args:
        exercise_type: Tipo de ejercicio

    Returns:
        Diccionario con valores de referencia
    """
    return REFERENCE_VALUES.get(exercise_type, {})


def validate_config() -> bool:
    """
    Valida que todas las configuraciones sean consistentes.

    Returns:
        True si la configuración es válida
    """
    # Verificar que archivos necesarios existen
    required_dirs = [RAW_DATA_DIR, PROCESSED_DATA_DIR, RESULTS_DIR, MODELS_DIR]
    for directory in required_dirs:
        if not directory.exists():
            print(f"Advertencia: Directorio no existe: {directory}")

    return True


# Validar configuración al importar
validate_config()
