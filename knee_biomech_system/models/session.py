"""
Modelo de datos para sesiones de captura.

Define la estructura de una sesión de adquisición de datos,
incluyendo configuración, tiempos y resultados.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum
from pathlib import Path

import numpy as np


class SessionStatus(Enum):
    """Estado de la sesión."""
    CREATED = "creado"
    CONFIGURING = "configurando"
    CALIBRATING = "calibrando"
    READY = "listo"
    RECORDING = "grabando"
    PROCESSING = "procesando"
    COMPLETED = "completado"
    ERROR = "error"


class ExerciseType(Enum):
    """Tipo de ejercicio realizado."""
    SQUAT = "squat"
    CMJ = "cmj"
    SQUAT_JUMP = "squat_jump"


@dataclass
class Session:
    """
    Modelo de una sesión de captura de datos.

    Attributes:
        session_id: Identificador único de la sesión
        patient_id: ID del paciente asociado
        exercise_type: Tipo de ejercicio realizado
        status: Estado actual de la sesión
        created_at: Timestamp de creación
        started_at: Timestamp de inicio de grabación
        ended_at: Timestamp de finalización
        duration: Duración de la grabación en segundos
        repetitions: Número de repeticiones realizadas
        imu_data_path: Ruta a datos de IMU
        force_data_path: Ruta a datos de plataforma
        results_path: Ruta a resultados procesados
        notes: Notas sobre la sesión
        metadata: Metadatos adicionales
    """

    session_id: str
    patient_id: str
    exercise_type: ExerciseType
    status: SessionStatus = SessionStatus.CREATED
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration: float = 0.0
    repetitions: int = 1
    imu_data_path: Optional[Path] = None
    force_data_path: Optional[Path] = None
    results_path: Optional[Path] = None
    notes: str = ""
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        """Validación post-inicialización."""
        if isinstance(self.exercise_type, str):
            self.exercise_type = ExerciseType(self.exercise_type)
        if isinstance(self.status, str):
            self.status = SessionStatus(self.status)

    def start_recording(self):
        """Marca el inicio de la grabación."""
        self.started_at = datetime.now()
        self.status = SessionStatus.RECORDING

    def stop_recording(self):
        """Marca el fin de la grabación."""
        self.ended_at = datetime.now()
        if self.started_at:
            self.duration = (self.ended_at - self.started_at).total_seconds()
        self.status = SessionStatus.READY

    def start_processing(self):
        """Marca el inicio del procesamiento."""
        self.status = SessionStatus.PROCESSING

    def complete(self):
        """Marca la sesión como completada."""
        self.status = SessionStatus.COMPLETED

    def mark_error(self, error_message: str):
        """Marca la sesión con error."""
        self.status = SessionStatus.ERROR
        self.metadata['error'] = error_message
        self.metadata['error_time'] = datetime.now().isoformat()

    @property
    def is_completed(self) -> bool:
        """Verifica si la sesión está completada."""
        return self.status == SessionStatus.COMPLETED

    @property
    def is_recording(self) -> bool:
        """Verifica si está en grabación."""
        return self.status == SessionStatus.RECORDING

    @property
    def has_data(self) -> bool:
        """Verifica si tiene datos asociados."""
        return self.imu_data_path is not None and self.force_data_path is not None

    def to_dict(self) -> Dict:
        """Convierte la sesión a diccionario."""
        return {
            "session_id": self.session_id,
            "patient_id": self.patient_id,
            "exercise_type": self.exercise_type.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration": self.duration,
            "repetitions": self.repetitions,
            "imu_data_path": str(self.imu_data_path) if self.imu_data_path else None,
            "force_data_path": str(self.force_data_path) if self.force_data_path else None,
            "results_path": str(self.results_path) if self.results_path else None,
            "notes": self.notes,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Session':
        """Crea una sesión desde un diccionario."""
        # Convertir fechas
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('started_at') and isinstance(data['started_at'], str):
            data['started_at'] = datetime.fromisoformat(data['started_at'])
        if data.get('ended_at') and isinstance(data['ended_at'], str):
            data['ended_at'] = datetime.fromisoformat(data['ended_at'])

        # Convertir paths
        if data.get('imu_data_path'):
            data['imu_data_path'] = Path(data['imu_data_path'])
        if data.get('force_data_path'):
            data['force_data_path'] = Path(data['force_data_path'])
        if data.get('results_path'):
            data['results_path'] = Path(data['results_path'])

        return cls(**data)

    def __str__(self) -> str:
        """Representación en string."""
        return f"Session({self.session_id}: {self.exercise_type.value}, {self.status.value})"


@dataclass
class SessionData:
    """
    Contenedor para datos adquiridos en una sesión.

    Attributes:
        session_id: ID de la sesión asociada
        time_imu: Vector de tiempo para datos IMU (segundos)
        time_force: Vector de tiempo para datos de fuerza (segundos)
        imu_data: Datos de IMU [dict con keys por sensor]
        force_data: Datos de plataforma de fuerza
        is_synchronized: Indica si los datos están sincronizados
    """

    session_id: str
    time_imu: Optional[np.ndarray] = None
    time_force: Optional[np.ndarray] = None
    imu_data: Dict[str, Dict[str, np.ndarray]] = field(default_factory=dict)
    force_data: Optional[Dict[str, np.ndarray]] = None
    is_synchronized: bool = False

    def get_imu_location_data(self, location: str) -> Optional[Dict[str, np.ndarray]]:
        """
        Obtiene los datos de un sensor IMU específico.

        Args:
            location: Ubicación del sensor (pelvis, femur_right, etc.)

        Returns:
            Diccionario con datos del sensor o None
        """
        return self.imu_data.get(location)

    def add_imu_data(self, location: str, data: Dict[str, np.ndarray]):
        """
        Añade datos de un sensor IMU.

        Args:
            location: Ubicación del sensor
            data: Diccionario con datos (quaternion, acceleration, etc.)
        """
        self.imu_data[location] = data

    def add_force_data(self, data: Dict[str, np.ndarray]):
        """
        Añade datos de plataforma de fuerza.

        Args:
            data: Diccionario con canales (Fx, Fy, Fz, Mx, My, Mz)
        """
        self.force_data = data

    @property
    def num_samples_imu(self) -> int:
        """Retorna el número de muestras de datos IMU."""
        return len(self.time_imu) if self.time_imu is not None else 0

    @property
    def num_samples_force(self) -> int:
        """Retorna el número de muestras de datos de fuerza."""
        return len(self.time_force) if self.time_force is not None else 0

    @property
    def duration_imu(self) -> float:
        """Duración de datos IMU en segundos."""
        if self.time_imu is not None and len(self.time_imu) > 0:
            return self.time_imu[-1] - self.time_imu[0]
        return 0.0

    @property
    def duration_force(self) -> float:
        """Duración de datos de fuerza en segundos."""
        if self.time_force is not None and len(self.time_force) > 0:
            return self.time_force[-1] - self.time_force[0]
        return 0.0
