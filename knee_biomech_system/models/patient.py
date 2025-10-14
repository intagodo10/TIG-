"""
Modelo de datos para pacientes.

Define la estructura de información de pacientes y métodos
para gestión en base de datos.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict
from enum import Enum


class Sex(Enum):
    """Sexo biológico del paciente."""
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"


class AffectedLimb(Enum):
    """Extremidad afectada del paciente."""
    RIGHT = "derecha"
    LEFT = "izquierda"
    BOTH = "ambas"
    NONE = "ninguna"


@dataclass
class Patient:
    """
    Modelo de datos de un paciente.

    Attributes:
        patient_id: Identificador único del paciente
        name: Nombre completo del paciente
        age: Edad en años
        mass: Masa corporal en kg
        height: Altura en metros
        sex: Sexo biológico
        affected_limb: Extremidad afectada
        diagnosis: Diagnóstico médico
        notes: Notas adicionales
        created_at: Fecha de creación del registro
        updated_at: Fecha de última actualización
    """

    patient_id: str
    name: str
    age: int
    mass: float  # kg
    height: float  # metros
    sex: Sex
    affected_limb: AffectedLimb
    diagnosis: str = ""
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validación post-inicialización."""
        # Convertir strings a enums si es necesario
        if isinstance(self.sex, str):
            self.sex = Sex(self.sex)
        if isinstance(self.affected_limb, str):
            self.affected_limb = AffectedLimb(self.affected_limb)

        # Validaciones básicas
        if self.age < 0 or self.age > 150:
            raise ValueError(f"Edad inválida: {self.age}")
        if self.mass <= 0 or self.mass > 500:
            raise ValueError(f"Masa inválida: {self.mass}")
        if self.height <= 0 or self.height > 3.0:
            raise ValueError(f"Altura inválida: {self.height}")

    @property
    def bmi(self) -> float:
        """
        Calcula el Índice de Masa Corporal (BMI).

        Returns:
            BMI en kg/m²
        """
        return self.mass / (self.height ** 2)

    @property
    def body_weight_newtons(self) -> float:
        """
        Calcula el peso corporal en Newtons.

        Returns:
            Peso en N
        """
        return self.mass * 9.81

    @property
    def body_weight(self) -> float:
        """
        Alias para body_weight_newtons.

        Returns:
            Peso en N
        """
        return self.body_weight_newtons

    def to_dict(self) -> Dict:
        """
        Convierte el paciente a diccionario.

        Returns:
            Diccionario con datos del paciente
        """
        return {
            "patient_id": self.patient_id,
            "name": self.name,
            "age": self.age,
            "mass": self.mass,
            "height": self.height,
            "sex": self.sex.value,
            "affected_limb": self.affected_limb.value,
            "diagnosis": self.diagnosis,
            "notes": self.notes,
            "bmi": self.bmi,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Patient':
        """
        Crea un paciente desde un diccionario.

        Args:
            data: Diccionario con datos del paciente

        Returns:
            Instancia de Patient
        """
        # Convertir fechas si son strings
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])

        # Remover campos calculados
        data.pop('bmi', None)

        return cls(**data)

    def update(self, **kwargs):
        """
        Actualiza atributos del paciente.

        Args:
            **kwargs: Atributos a actualizar
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()

    def __str__(self) -> str:
        """Representación en string del paciente."""
        return f"Patient({self.patient_id}: {self.name}, {self.age} años, {self.mass} kg)"

    def __repr__(self) -> str:
        """Representación técnica del paciente."""
        return self.__str__()
