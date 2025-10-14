"""
Diálogos de la aplicación.

Contiene ventanas modales y diálogos personalizados.
"""

from .sensor_assignment_dialog import SensorAssignmentDialog, show_sensor_assignment_dialog

__all__ = [
    'SensorAssignmentDialog',
    'show_sensor_assignment_dialog'
]
