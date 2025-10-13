"""
Componente de tarjeta de métrica.

Muestra una métrica biomecánica con valor, unidad y estado visual.
"""

import customtkinter as ctk
from typing import Optional, Literal
from config.ui_theme import COLORS, FONTS


class MetricCard(ctk.CTkFrame):
    """
    Tarjeta para mostrar una métrica biomecánica.

    Muestra título, valor principal, unidad, y estado (normal/warning/error).
    """

    def __init__(self, master, title: str, value: str = "--",
                 unit: str = "", status: Literal["normal", "warning", "error"] = "normal",
                 **kwargs):
        """
        Inicializa la tarjeta de métrica.

        Args:
            master: Widget padre
            title: Título de la métrica
            value: Valor a mostrar
            unit: Unidad de medida
            status: Estado visual (normal, warning, error)
        """
        super().__init__(master, **kwargs)

        self.title_text = title
        self.value_text = value
        self.unit_text = unit
        self.status = status

        # Configurar el frame
        self.configure(
            fg_color=COLORS["bg_secondary"],
            corner_radius=12,
            border_width=2,
            border_color=self._get_status_color()
        )

        self._create_widgets()

    def _get_status_color(self) -> str:
        """Obtiene el color según el estado."""
        colors = {
            "normal": COLORS["accent_primary"],
            "warning": COLORS["warning"],
            "error": COLORS["error"]
        }
        return colors.get(self.status, COLORS["accent_primary"])

    def _create_widgets(self):
        """Crea los widgets internos."""
        # Padding interno
        self.grid_columnconfigure(0, weight=1)

        # Título
        self.title_label = ctk.CTkLabel(
            self,
            text=self.title_text,
            font=ctk.CTkFont(family=FONTS["family_primary"][0],
                           size=FONTS["size_small"],
                           weight=FONTS["weight_normal"]),
            text_color=COLORS["text_secondary"]
        )
        self.title_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        # Frame para valor y unidad
        value_frame = ctk.CTkFrame(self, fg_color="transparent")
        value_frame.grid(row=1, column=0, padx=15, pady=(0, 5), sticky="ew")

        # Valor principal
        self.value_label = ctk.CTkLabel(
            value_frame,
            text=self.value_text,
            font=ctk.CTkFont(family=FONTS["family_primary"][0],
                           size=FONTS["size_xxlarge"],
                           weight=FONTS["weight_bold"]),
            text_color=self._get_status_color()
        )
        self.value_label.pack(side="left")

        # Unidad
        if self.unit_text:
            self.unit_label = ctk.CTkLabel(
                value_frame,
                text=f" {self.unit_text}",
                font=ctk.CTkFont(family=FONTS["family_primary"][0],
                               size=FONTS["size_medium"]),
                text_color=COLORS["text_tertiary"]
            )
            self.unit_label.pack(side="left", padx=(5, 0))

        # Indicador de estado (emoji)
        status_icons = {
            "normal": "✓",
            "warning": "⚠",
            "error": "✗"
        }
        self.status_label = ctk.CTkLabel(
            self,
            text=status_icons.get(self.status, ""),
            font=ctk.CTkFont(size=FONTS["size_large"]),
            text_color=self._get_status_color()
        )
        self.status_label.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="w")

    def update_value(self, value: str, status: Optional[str] = None):
        """
        Actualiza el valor mostrado.

        Args:
            value: Nuevo valor
            status: Nuevo estado (opcional)
        """
        self.value_text = value
        self.value_label.configure(text=value)

        if status is not None:
            self.status = status
            color = self._get_status_color()
            self.configure(border_color=color)
            self.value_label.configure(text_color=color)
            self.status_label.configure(text_color=color)

            status_icons = {"normal": "✓", "warning": "⚠", "error": "✗"}
            self.status_label.configure(text=status_icons.get(status, ""))

    def update_all(self, title: Optional[str] = None, value: Optional[str] = None,
                   unit: Optional[str] = None, status: Optional[str] = None):
        """
        Actualiza todos los campos de la tarjeta.

        Args:
            title: Nuevo título (opcional)
            value: Nuevo valor (opcional)
            unit: Nueva unidad (opcional)
            status: Nuevo estado (opcional)
        """
        if title is not None:
            self.title_text = title
            self.title_label.configure(text=title)

        if value is not None:
            self.value_text = value
            self.value_label.configure(text=value)

        if unit is not None:
            self.unit_text = unit
            if hasattr(self, 'unit_label'):
                self.unit_label.configure(text=f" {unit}")

        if status is not None:
            self.update_value(self.value_text, status)
