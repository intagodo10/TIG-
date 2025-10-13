"""
Sistema de logging para el Sistema de Análisis Biomecánico.

Proporciona funcionalidades de registro de eventos, errores y debug
con rotación de archivos y niveles configurables.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional

from config.settings import LOGGING_CONFIG


class BiomechLogger:
    """
    Logger personalizado para el sistema biomecánico.

    Proporciona logging a archivo y consola con formato personalizado,
    rotación automática de archivos y filtrado por niveles.
    """

    def __init__(self, name: str = "BiomechSystem"):
        """
        Inicializa el logger.

        Args:
            name: Nombre del logger
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOGGING_CONFIG["level"]))

        # Evitar duplicación de handlers
        if self.logger.handlers:
            return

        # Formato de log
        formatter = logging.Formatter(
            LOGGING_CONFIG["format"],
            datefmt=LOGGING_CONFIG["date_format"]
        )

        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Handler para archivo (si está habilitado)
        if LOGGING_CONFIG["file_enabled"]:
            file_handler = RotatingFileHandler(
                LOGGING_CONFIG["file_path"],
                maxBytes=LOGGING_CONFIG["max_file_size"],
                backupCount=LOGGING_CONFIG["backup_count"],
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str, **kwargs):
        """Log de debug."""
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log de información."""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log de advertencia."""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log de error."""
        self.logger.error(message, exc_info=exc_info, **kwargs)

    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """Log crítico."""
        self.logger.critical(message, exc_info=exc_info, **kwargs)

    def exception(self, message: str, **kwargs):
        """Log de excepción con traceback."""
        self.logger.exception(message, **kwargs)


# Logger global del sistema
system_logger = BiomechLogger("BiomechSystem")


def get_logger(name: str) -> BiomechLogger:
    """
    Obtiene un logger específico para un módulo.

    Args:
        name: Nombre del módulo

    Returns:
        Instancia de BiomechLogger
    """
    return BiomechLogger(name)


# Funciones de conveniencia
def log_info(message: str):
    """Log de información usando el logger global."""
    system_logger.info(message)


def log_warning(message: str):
    """Log de advertencia usando el logger global."""
    system_logger.warning(message)


def log_error(message: str, exc_info: bool = False):
    """Log de error usando el logger global."""
    system_logger.error(message, exc_info=exc_info)


def log_debug(message: str):
    """Log de debug usando el logger global."""
    system_logger.debug(message)


def log_session_start(patient_id: str, exercise_type: str):
    """Registra el inicio de una sesión de captura."""
    system_logger.info(
        f"Iniciando sesión - Paciente: {patient_id}, Ejercicio: {exercise_type}"
    )


def log_session_end(patient_id: str, duration: float, success: bool):
    """Registra el fin de una sesión de captura."""
    status = "exitosa" if success else "fallida"
    system_logger.info(
        f"Sesión finalizada ({status}) - Paciente: {patient_id}, "
        f"Duración: {duration:.2f}s"
    )


def log_sensor_event(sensor_location: str, event: str, details: str = ""):
    """Registra eventos de sensores."""
    message = f"Sensor {sensor_location}: {event}"
    if details:
        message += f" - {details}"
    system_logger.info(message)


def log_analysis_step(step_name: str, status: str, duration: Optional[float] = None):
    """Registra pasos del análisis."""
    message = f"Análisis - {step_name}: {status}"
    if duration:
        message += f" (duración: {duration:.2f}s)"
    system_logger.info(message)
