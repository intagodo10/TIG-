"""
Componente de notificaciones toast.

Muestra alertas temporales en la esquina de la pantalla.
"""

import customtkinter as ctk
from typing import Literal
from config.ui_theme import COLORS, FONTS


class AlertToast(ctk.CTkFrame):
    """
    Notificación toast que aparece temporalmente.

    Se muestra en la esquina superior derecha y desaparece automáticamente.
    """

    def __init__(self, master, message: str,
                 alert_type: Literal["info", "success", "warning", "error"] = "info",
                 duration: int = 3000):
        """
        Inicializa el toast.

        Args:
            master: Widget padre
            message: Mensaje a mostrar
            alert_type: Tipo de alerta
            duration: Duración en milisegundos
        """
        super().__init__(master)

        self.message = message
        self.alert_type = alert_type
        self.duration = duration

        # Configurar apariencia según tipo
        colors = {
            "info": COLORS["info"],
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "error": COLORS["error"]
        }

        icons = {
            "info": "ℹ",
            "success": "✓",
            "warning": "⚠",
            "error": "✗"
        }

        self.color = colors.get(alert_type, COLORS["info"])
        self.icon = icons.get(alert_type, "ℹ")

        self.configure(
            fg_color=COLORS["bg_tertiary"],
            corner_radius=12,
            border_width=2,
            border_color=self.color
        )

        self._create_widgets()
        self._schedule_dismiss()

    def _create_widgets(self):
        """Crea los widgets internos."""
        # Frame contenedor
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(padx=15, pady=12, fill="both", expand=True)

        # Icono
        icon_label = ctk.CTkLabel(
            content_frame,
            text=self.icon,
            font=ctk.CTkFont(size=20),
            text_color=self.color,
            width=30
        )
        icon_label.pack(side="left", padx=(0, 10))

        # Mensaje
        message_label = ctk.CTkLabel(
            content_frame,
            text=self.message,
            font=ctk.CTkFont(size=FONTS["size_normal"]),
            text_color=COLORS["text_primary"],
            wraplength=300,
            justify="left"
        )
        message_label.pack(side="left", fill="both", expand=True)

        # Botón cerrar
        close_button = ctk.CTkButton(
            content_frame,
            text="✕",
            width=25,
            height=25,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_secondary"],
            command=self.dismiss
        )
        close_button.pack(side="right", padx=(10, 0))

    def _schedule_dismiss(self):
        """Programa el cierre automático."""
        if self.duration > 0:
            self.after(self.duration, self.dismiss)

    def dismiss(self):
        """Cierra y destruye el toast."""
        self.destroy()


class AlertManager:
    """
    Gestor de alertas toast.

    Controla la visualización y posicionamiento de múltiples alertas.
    """

    def __init__(self, master):
        """
        Inicializa el gestor de alertas.

        Args:
            master: Widget padre (ventana principal)
        """
        self.master = master
        self.active_toasts = []
        self.toast_spacing = 10
        self.start_y = 70  # Debajo del header

    def show_alert(self, message: str, alert_type: str = "info", duration: int = 3000):
        """
        Muestra una nueva alerta.

        Args:
            message: Mensaje a mostrar
            alert_type: Tipo de alerta
            duration: Duración en milisegundos
        """
        # Crear toast
        toast = AlertToast(self.master, message, alert_type, duration)

        # Posicionar en la esquina superior derecha
        self._position_toast(toast)

        # Agregar a lista activa
        self.active_toasts.append(toast)

        # Programar limpieza
        toast.bind("<Destroy>", lambda e: self._on_toast_destroyed(toast))

    def _position_toast(self, toast: AlertToast):
        """
        Posiciona el toast en la pantalla.

        Args:
            toast: Toast a posicionar
        """
        # Actualizar para obtener dimensiones
        toast.update_idletasks()

        # Dimensiones del toast
        toast_width = 350
        toast_height = toast.winfo_reqheight()

        # Dimensiones de la ventana
        window_width = self.master.winfo_width()

        # Calcular posición Y (apilar verticalmente)
        y_offset = self.start_y
        for existing_toast in self.active_toasts:
            if existing_toast.winfo_exists():
                y_offset += existing_toast.winfo_height() + self.toast_spacing

        # Posicionar
        x = window_width - toast_width - 20  # 20px de margen derecho
        toast.place(x=x, y=y_offset, width=toast_width)

    def _on_toast_destroyed(self, toast: AlertToast):
        """
        Maneja la destrucción de un toast.

        Args:
            toast: Toast destruido
        """
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)

        # Reposicionar toasts restantes
        self._reposition_all()

    def _reposition_all(self):
        """Reposiciona todos los toasts activos."""
        y_offset = self.start_y
        for toast in self.active_toasts:
            if toast.winfo_exists():
                toast.place_configure(y=y_offset)
                y_offset += toast.winfo_height() + self.toast_spacing

    def clear_all(self):
        """Cierra todas las alertas activas."""
        for toast in self.active_toasts[:]:  # Copiar lista para evitar problemas
            if toast.winfo_exists():
                toast.dismiss()
        self.active_toasts.clear()

    # Métodos de conveniencia
    def info(self, message: str, duration: int = 3000):
        """Muestra alerta de información."""
        self.show_alert(message, "info", duration)

    def success(self, message: str, duration: int = 3000):
        """Muestra alerta de éxito."""
        self.show_alert(message, "success", duration)

    def warning(self, message: str, duration: int = 5000):
        """Muestra alerta de advertencia."""
        self.show_alert(message, "warning", duration)

    def error(self, message: str, duration: int = 5000):
        """Muestra alerta de error."""
        self.show_alert(message, "error", duration)
