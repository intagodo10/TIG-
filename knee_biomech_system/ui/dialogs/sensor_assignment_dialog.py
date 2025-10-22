"""
Diálogo para asignar sensores BLE a ubicaciones anatómicas.

Permite escanear, visualizar y asignar sensores Xsens DOT a ubicaciones del cuerpo.
"""

import customtkinter as ctk
import asyncio
import threading 
from typing import Dict, List, Optional
from tkinter import messagebox

from config.ui_theme import COLORS, FONTS
from utils.logger import get_logger

logger = get_logger(__name__)


class SensorAssignmentDialog(ctk.CTkToplevel):
    """
    Diálogo para escanear y asignar sensores a ubicaciones anatómicas.

    Workflow:
    1. Escanear sensores BLE disponibles
    2. Mostrar lista de sensores encontrados
    3. Usuario asigna cada sensor a una ubicación anatómica
    4. Devolver diccionario de asignaciones
    """

    def __init__(self, parent, required_locations: List[str], **kwargs):
        """
        Inicializa el diálogo.

        Args:
            parent: Widget padre
            required_locations: Lista de ubicaciones anatómicas requeridas
                              (ej: ['pelvis', 'femur_right', 'tibia_right'])
        """
        super().__init__(parent, **kwargs)

        self.required_locations = required_locations
        self.scanned_sensors: List[Dict] = []  # Lista de sensores encontrados
        self.assignments: Dict[str, str] = {}  # {location: sensor_address}
        self.result = None  # Resultado final del diálogo

        # Configurar ventana
        self.title("Asignación de Sensores")
        self.geometry("800x600")
        self.configure(fg_color=COLORS["bg_primary"])

        # Centrar ventana
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"+{x}+{y}")

        # Modal
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets del diálogo."""
        # Grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ===== HEADER =====
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text="🔍 Escanear y Asignar Sensores",
            font=ctk.CTkFont(size=FONTS["size_xxlarge"], weight=FONTS["weight_bold"]),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Escanea los sensores y asígnalos a las ubicaciones anatómicas correspondientes",
            font=ctk.CTkFont(size=FONTS["size_normal"]),
            text_color=COLORS["text_secondary"]
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # ===== CONTENT AREA (2 columnas) =====
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # ----- Columna Izquierda: Sensores Escaneados -----
        left_panel = ctk.CTkFrame(content_frame, fg_color=COLORS["bg_secondary"], corner_radius=12)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Título sección
        ctk.CTkLabel(
            left_panel,
            text="Sensores Encontrados",
            font=ctk.CTkFont(size=FONTS["size_medium"], weight=FONTS["weight_bold"]),
            text_color=COLORS["accent_primary"]
        ).pack(padx=15, pady=(15, 10), anchor="w")

        # Botón de escaneo
        self.scan_button = ctk.CTkButton(
            left_panel,
            text="🔍 Escanear Sensores (10s)",
            command=self._start_scan,
            height=40,
            font=ctk.CTkFont(size=FONTS["size_normal"], weight=FONTS["weight_bold"]),
            fg_color=COLORS["accent_secondary"],
            hover_color="#3a8aef"
        )
        self.scan_button.pack(padx=15, pady=(0, 10), fill="x")

        # Status label
        self.scan_status_label = ctk.CTkLabel(
            left_panel,
            text="Presiona 'Escanear' para buscar sensores",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_secondary"]
        )
        self.scan_status_label.pack(padx=15, pady=(0, 10))

        # Lista de sensores (scrollable)
        self.sensor_list_frame = ctk.CTkScrollableFrame(
            left_panel,
            fg_color=COLORS["bg_primary"],
            corner_radius=8
        )
        self.sensor_list_frame.pack(padx=15, pady=(0, 15), fill="both", expand=True)

        # ----- Columna Derecha: Asignaciones -----
        right_panel = ctk.CTkFrame(content_frame, fg_color=COLORS["bg_secondary"], corner_radius=12)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Título sección
        ctk.CTkLabel(
            right_panel,
            text="Asignaciones",
            font=ctk.CTkFont(size=FONTS["size_medium"], weight=FONTS["weight_bold"]),
            text_color=COLORS["accent_primary"]
        ).pack(padx=15, pady=(15, 10), anchor="w")

        # Info de ubicaciones requeridas
        ctk.CTkLabel(
            right_panel,
            text=f"Se requieren {len(self.required_locations)} sensores",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_secondary"]
        ).pack(padx=15, pady=(0, 10))

        # Lista de asignaciones
        self.assignment_frame = ctk.CTkScrollableFrame(
            right_panel,
            fg_color=COLORS["bg_primary"],
            corner_radius=8
        )
        self.assignment_frame.pack(padx=15, pady=(0, 15), fill="both", expand=True)

        # Crear widgets para cada ubicación requerida
        self.location_combos: Dict[str, ctk.CTkComboBox] = {}
        self._create_assignment_widgets()

        # ===== FOOTER =====
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))

        # Botones
        button_container = ctk.CTkFrame(footer_frame, fg_color="transparent")
        button_container.pack(side="right")

        cancel_button = ctk.CTkButton(
            button_container,
            text="Cancelar",
            command=self._cancel,
            width=120,
            height=40,
            fg_color=COLORS["bg_secondary"],
            hover_color=COLORS["bg_tertiary"],
            text_color=COLORS["text_primary"]
        )
        cancel_button.pack(side="left", padx=(0, 10))

        self.confirm_button = ctk.CTkButton(
            button_container,
            text="Confirmar Asignaciones",
            command=self._confirm,
            width=200,
            height=40,
            font=ctk.CTkFont(size=FONTS["size_normal"], weight=FONTS["weight_bold"]),
            fg_color=COLORS["success"],
            hover_color="#5abf6f",
            state="disabled"
        )
        self.confirm_button.pack(side="left")

    def _create_assignment_widgets(self):
        """Crea widgets de asignación para cada ubicación."""
        location_names = {
            'pelvis': 'Pelvis',
            'femur_left': 'Fémur Izquierdo',
            'femur_right': 'Fémur Derecho',
            'tibia_left': 'Tibia Izquierda',
            'tibia_right': 'Tibia Derecha',
            'foot_left': 'Pie Izquierdo',
            'foot_right': 'Pie Derecho'
        }

        for location in self.required_locations:
            # Frame para cada ubicación
            loc_frame = ctk.CTkFrame(self.assignment_frame, fg_color="transparent")
            loc_frame.pack(fill="x", pady=5)

            # Label de ubicación
            display_name = location_names.get(location, location)
            ctk.CTkLabel(
                loc_frame,
                text=display_name,
                font=ctk.CTkFont(size=FONTS["size_normal"]),
                text_color=COLORS["text_primary"],
                width=150,
                anchor="w"
            ).pack(side="left", padx=(0, 10))

            # ComboBox para seleccionar sensor
            combo = ctk.CTkComboBox(
                loc_frame,
                values=["No asignado"],
                state="readonly",
                width=250
            )
            combo.set("No asignado")
            combo.pack(side="left", fill="x", expand=True)

            self.location_combos[location] = combo

    def _start_scan(self):
        """Inicia el escaneo de sensores BLE."""
        logger.info("Iniciando escaneo de sensores...")

        # Deshabilitar botón durante escaneo
        self.scan_button.configure(state="disabled", text="⏳ Escaneando...")
        self.scan_status_label.configure(
            text="Escaneando... Asegúrate de que los sensores estén encendidos",
            text_color=COLORS["warning"]
        )

        # ✅ Ejecutar escaneo en un hilo de trabajo (no bloquear GUI)
        t = threading.Thread(target=self._scan_worker, daemon=True)
        t.start()

    def _scan_worker(self):
        """
        Hilo de trabajo: prepara el hilo en modo compatible con Bleak
        y ejecuta la corrutina de escaneo.
        """
        try:
            # 👇 Muy importante en Windows:
            # Si algún paquete puso el hilo en STA, lo “desinicializamos”
            # para que Bleak pueda usar MTA internamente.
            try:
                from bleak.backends.winrt.util import uninitialize_sta
                uninitialize_sta()
            except Exception:
                # Si no aplica/ya está OK, seguimos
                pass

            # Ejecutar la corrutina real en este hilo
            asyncio.run(self._scan_async())

        except Exception as e:
            logger.error(f"Error en _scan_worker: {e}", exc_info=True)
            # Volver al hilo de la GUI para mostrar error y reactivar botón
            self.after(0, lambda: self._scan_error(str(e)))


    async def _scan_async(self):
        """Escanea sensores de forma asíncrona."""
        try:
            # Importar aquí para evitar errores si bleak no está instalado
            from core.data_acquisition.imu_handler import IMUHandler

            handler = IMUHandler()
            sensors = await handler.scan_sensors(duration=10.0)

            self.scanned_sensors = sensors

            # Actualizar UI en el hilo principal
            self.after(0, self._update_sensor_list)

        except ImportError as e:
            logger.error(f"Error importando IMUHandler: {e}")
            self.after(0, lambda: self._scan_error("Librería 'bleak' no instalada"))
        except Exception as e:
            logger.error(f"Error durante escaneo: {e}", exc_info=True)
            self.after(0, lambda: self._scan_error(str(e)))

    def _update_sensor_list(self):
        """Actualiza la lista de sensores encontrados."""
        # Limpiar lista anterior
        for widget in self.sensor_list_frame.winfo_children():
            widget.destroy()

        if not self.scanned_sensors:
            # No se encontraron sensores
            self.scan_status_label.configure(
                text="⚠️ No se encontraron sensores Xsens DOT",
                text_color=COLORS["warning"]
            )

            ctk.CTkLabel(
                self.sensor_list_frame,
                text="No se encontraron sensores.\n\nVerifica que:\n• Los sensores estén encendidos (LED azul)\n• Bluetooth esté activado",
                font=ctk.CTkFont(size=FONTS["size_small"]),
                text_color=COLORS["text_secondary"],
                justify="left"
            ).pack(padx=10, pady=20)
        else:
            # Mostrar sensores encontrados
            self.scan_status_label.configure(
                text=f"✓ Se encontraron {len(self.scanned_sensors)} sensores",
                text_color=COLORS["success"]
            )

            for sensor in self.scanned_sensors:
                sensor_card = self._create_sensor_card(sensor)
                sensor_card.pack(fill="x", padx=5, pady=3)

            # Actualizar opciones de los ComboBox
            sensor_options = ["No asignado"] + [
                f"{s['name']} ({s['address'][-8:]})" for s in self.scanned_sensors
            ]

            for combo in self.location_combos.values():
                combo.configure(values=sensor_options)

        # Rehabilitar botón
        self.scan_button.configure(state="normal", text="🔄 Reescanear")

    def _create_sensor_card(self, sensor: Dict) -> ctk.CTkFrame:
        """
        Crea una tarjeta visual para un sensor.

        Args:
            sensor: Diccionario con info del sensor

        Returns:
            Frame con la tarjeta del sensor
        """
        card = ctk.CTkFrame(self.sensor_list_frame, fg_color=COLORS["bg_secondary"], corner_radius=8)

        # Nombre del sensor
        name_label = ctk.CTkLabel(
            card,
            text=sensor['name'],
            font=ctk.CTkFont(size=FONTS["size_normal"], weight=FONTS["weight_bold"]),
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        name_label.pack(anchor="w", padx=10, pady=(8, 2))

        # Dirección MAC (últimos 8 caracteres)
        address_label = ctk.CTkLabel(
            card,
            text=f"Dirección: ...{sensor['address'][-8:]}",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        address_label.pack(anchor="w", padx=10, pady=(0, 2))

        # RSSI (señal)
        rssi = sensor.get('rssi', 0)
        rssi_color = COLORS["success"] if rssi > -70 else COLORS["warning"] if rssi > -85 else COLORS["error"]

        rssi_label = ctk.CTkLabel(
            card,
            text=f"Señal: {rssi} dBm",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=rssi_color,
            anchor="w"
        )
        rssi_label.pack(anchor="w", padx=10, pady=(0, 8))

        return card

    def _scan_error(self, error_message: str):
        """Maneja errores durante el escaneo."""
        self.scan_status_label.configure(
            text=f"✗ Error: {error_message}",
            text_color=COLORS["error"]
        )
        self.scan_button.configure(state="normal", text="🔍 Reintentar Escaneo")

        messagebox.showerror(
            "Error de Escaneo",
            f"No se pudo escanear los sensores:\n\n{error_message}\n\nVerifica que Bluetooth esté activado."
        )

    def _confirm(self):
        """Confirma las asignaciones y cierra el diálogo."""
        # Construir diccionario de asignaciones
        assignments = {}

        for location, combo in self.location_combos.items():
            selected = combo.get()

            if selected == "No asignado":
                # Ubicación sin asignar
                messagebox.showwarning(
                    "Asignación Incompleta",
                    f"La ubicación '{location}' no tiene un sensor asignado.\n\nAsigna un sensor a todas las ubicaciones."
                )
                return

            # Extraer dirección del sensor del texto seleccionado
            # Formato: "Xsens DOT (XX:XX:XX:XX)"
            for sensor in self.scanned_sensors:
                if sensor['address'][-8:] in selected:
                    assignments[location] = sensor['address']
                    break

        # Verificar que no haya duplicados
        if len(set(assignments.values())) != len(assignments):
            messagebox.showwarning(
                "Sensores Duplicados",
                "No puedes asignar el mismo sensor a múltiples ubicaciones."
            )
            return

        # Todo correcto
        self.result = assignments
        logger.info(f"Asignaciones confirmadas: {assignments}")
        self.destroy()

    def _cancel(self):
        """Cancela el diálogo sin guardar."""
        self.result = None
        self.destroy()

    def get_assignments(self) -> Optional[Dict[str, str]]:
        """
        Obtiene las asignaciones realizadas.

        Returns:
            Diccionario {ubicación: dirección_mac} o None si se canceló
        """
        return self.result


def show_sensor_assignment_dialog(parent, required_locations: List[str]) -> Optional[Dict[str, str]]:
    """
    Muestra el diálogo de asignación de sensores.

    Args:
        parent: Widget padre
        required_locations: Lista de ubicaciones anatómicas requeridas

    Returns:
        Diccionario de asignaciones o None si se canceló
    """
    dialog = SensorAssignmentDialog(parent, required_locations)
    parent.wait_window(dialog)
    return dialog.get_assignments()
