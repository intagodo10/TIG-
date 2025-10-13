"""
Componente de estado de sensores.

Muestra el estado de conexión de los sensores IMU.
"""

import customtkinter as ctk
from typing import Literal
from config.ui_theme import COLORS, FONTS


class SensorStatusIndicator(ctk.CTkFrame):
    """
    Indicador de estado de un sensor individual.

    Muestra nombre del sensor y LED de estado (conectado/desconectado/error).
    """

    def __init__(self, master, sensor_name: str,
                 status: Literal["connected", "connecting", "disconnected", "error"] = "disconnected",
                 **kwargs):
        """
        Inicializa el indicador de sensor.

        Args:
            master: Widget padre
            sensor_name: Nombre del sensor
            status: Estado del sensor
        """
        super().__init__(master, **kwargs)

        self.sensor_name = sensor_name
        self.status = status

        self.configure(
            fg_color=COLORS["bg_tertiary"],
            corner_radius=8
        )

        self._create_widgets()

    def _get_status_info(self):
        """Obtiene color y texto según el estado."""
        status_info = {
            "connected": {
                "color": COLORS["sensor_connected"],
                "text": "Conectado",
                "icon": "●"
            },
            "connecting": {
                "color": COLORS["sensor_connecting"],
                "text": "Conectando...",
                "icon": "◐"
            },
            "disconnected": {
                "color": COLORS["sensor_disconnected"],
                "text": "Desconectado",
                "icon": "○"
            },
            "error": {
                "color": COLORS["sensor_error"],
                "text": "Error",
                "icon": "✗"
            }
        }
        return status_info.get(self.status, status_info["disconnected"])

    def _create_widgets(self):
        """Crea los widgets internos."""
        info = self._get_status_info()

        # LED indicador
        self.led_label = ctk.CTkLabel(
            self,
            text=info["icon"],
            font=ctk.CTkFont(size=20),
            text_color=info["color"],
            width=30
        )
        self.led_label.pack(side="left", padx=(10, 5), pady=10)

        # Frame de texto
        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=10)

        # Nombre del sensor
        self.name_label = ctk.CTkLabel(
            text_frame,
            text=self.sensor_name,
            font=ctk.CTkFont(size=FONTS["size_normal"], weight=FONTS["weight_bold"]),
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        self.name_label.pack(anchor="w")

        # Estado
        self.status_label = ctk.CTkLabel(
            text_frame,
            text=info["text"],
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        self.status_label.pack(anchor="w")

    def update_status(self, status: str):
        """
        Actualiza el estado del sensor.

        Args:
            status: Nuevo estado
        """
        self.status = status
        info = self._get_status_info()

        self.led_label.configure(text=info["icon"], text_color=info["color"])
        self.status_label.configure(text=info["text"])


class SensorPanel(ctk.CTkScrollableFrame):
    """
    Panel que muestra el estado de todos los sensores.
    """

    def __init__(self, master, sensor_locations: list, **kwargs):
        """
        Inicializa el panel de sensores.

        Args:
            master: Widget padre
            sensor_locations: Lista de nombres de ubicaciones de sensores
        """
        super().__init__(master, **kwargs)

        self.sensor_locations = sensor_locations
        self.sensors = {}

        self.configure(
            fg_color=COLORS["bg_secondary"],
            corner_radius=12
        )

        self._create_widgets()

    def _create_widgets(self):
        """Crea los indicadores para todos los sensores."""
        # Título
        title_label = ctk.CTkLabel(
            self,
            text="Estado de Sensores IMU",
            font=ctk.CTkFont(size=FONTS["size_large"], weight=FONTS["weight_bold"]),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(padx=15, pady=(15, 10), anchor="w")

        # Crear indicador para cada sensor
        for location in self.sensor_locations:
            # Formatear nombre
            display_name = location.replace("_", " ").title()

            sensor = SensorStatusIndicator(
                self,
                sensor_name=display_name,
                status="disconnected"
            )
            sensor.pack(padx=10, pady=5, fill="x")

            self.sensors[location] = sensor

    def update_sensor_status(self, location: str, status: str):
        """
        Actualiza el estado de un sensor específico.

        Args:
            location: Ubicación del sensor
            status: Nuevo estado
        """
        if location in self.sensors:
            self.sensors[location].update_status(status)

    def update_all_sensors(self, status: str):
        """
        Actualiza el estado de todos los sensores.

        Args:
            status: Nuevo estado para todos
        """
        for sensor in self.sensors.values():
            sensor.update_status(status)

    def get_sensor_statuses(self) -> dict:
        """
        Obtiene el estado de todos los sensores.

        Returns:
            Diccionario {location: status}
        """
        return {loc: sensor.status for loc, sensor in self.sensors.items()}
