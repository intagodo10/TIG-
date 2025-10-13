"""
Vista de captura de datos.

Permite capturar datos de sensores y plataforma de fuerza.
"""

import customtkinter as ctk
from typing import Optional, Callable
from tkinter import filedialog

from config.ui_theme import COLORS, FONTS
from config.settings import IMU_CONFIG, EXERCISES
from ui.components import SensorPanel, PlotWidget
from core.data_acquisition.force_platform import ForcePlatformHandler
from utils.logger import get_logger

logger = get_logger(__name__)


class CaptureView(ctk.CTkFrame):
    """
    Vista de captura de datos en tiempo real.

    Permite conectar sensores, configurar ejercicios y capturar datos.
    """

    def __init__(self, master, **kwargs):
        """
        Inicializa la vista de captura.

        Args:
            master: Widget padre
        """
        super().__init__(master, **kwargs)

        self.force_handler = ForcePlatformHandler()
        self.is_recording = False

        self.configure(fg_color=COLORS["bg_primary"])

        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets de la vista."""
        # Layout de 2 columnas
        self.grid_columnconfigure(0, weight=2)  # Panel derecho (gráficos)
        self.grid_columnconfigure(1, weight=1)  # Panel izquierdo (controles)
        self.grid_rowconfigure(0, weight=1)

        # ===== PANEL DERECHO: Gráficos =====
        right_panel = ctk.CTkFrame(self, fg_color="transparent")
        right_panel.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)

        # Configurar grid
        right_panel.grid_rowconfigure(0, weight=0)  # Título (tamaño fijo)
        right_panel.grid_rowconfigure(1, weight=1)  # Gráfico 1
        right_panel.grid_rowconfigure(2, weight=1)  # Gráfico 2
        right_panel.grid_columnconfigure(0, weight=1)

        # Título
        title_label = ctk.CTkLabel(
            right_panel,
            text="Captura de Datos en Tiempo Real",
            font=ctk.CTkFont(size=FONTS["size_xxlarge"], weight=FONTS["weight_bold"]),
            text_color=COLORS["text_primary"]
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Gráfico de fuerzas
        self.force_plot = PlotWidget(right_panel, title="Fuerza de Reacción al Suelo (GRF)")
        self.force_plot.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        # Gráfico de ángulo (placeholder)
        self.angle_plot = PlotWidget(right_panel, title="Ángulo de Rodilla")
        self.angle_plot.grid(row=2, column=0, sticky="nsew")

        # ===== PANEL IZQUIERDO: Controles =====
        left_panel = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_secondary"],
            corner_radius=12
        )
        left_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)

        # Sección: Configuración de Ejercicio
        exercise_frame = self._create_section(left_panel, "Configuración de Ejercicio")

        # Tipo de ejercicio
        ctk.CTkLabel(exercise_frame, text="Tipo de Ejercicio:",
                    font=ctk.CTkFont(size=FONTS["size_normal"]),
                    text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 5))

        self.exercise_combo = ctk.CTkComboBox(
            exercise_frame,
            values=[EXERCISES[key]["name"] for key in EXERCISES.keys()],
            state="readonly"
        )
        self.exercise_combo.set(EXERCISES["squat"]["name"])
        self.exercise_combo.pack(fill="x", pady=(0, 15))

        # Duración
        ctk.CTkLabel(exercise_frame, text="Duración (segundos):",
                    font=ctk.CTkFont(size=FONTS["size_normal"]),
                    text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 5))

        self.duration_entry = ctk.CTkEntry(exercise_frame, placeholder_text="10")
        self.duration_entry.insert(0, "10")
        self.duration_entry.pack(fill="x", pady=(0, 15))

        # Repeticiones
        ctk.CTkLabel(exercise_frame, text="Repeticiones:",
                    font=ctk.CTkFont(size=FONTS["size_normal"]),
                    text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 5))

        self.reps_entry = ctk.CTkEntry(exercise_frame, placeholder_text="5")
        self.reps_entry.insert(0, "5")
        self.reps_entry.pack(fill="x", pady=(0, 10))

        # Sección: Plataforma de Fuerza
        platform_frame = self._create_section(left_panel, "Plataforma de Fuerza")

        self.import_button = ctk.CTkButton(
            platform_frame,
            text="📥 Importar Datos de Valkyria",
            command=self._import_force_data,
            height=36,
            fg_color=COLORS["accent_secondary"],
            hover_color="#3a8aef"
        )
        self.import_button.pack(fill="x", pady=(0, 10))

        self.platform_status_label = ctk.CTkLabel(
            platform_frame,
            text="Estado: Sin datos",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_secondary"]
        )
        self.platform_status_label.pack(anchor="w")

        # Sección: Sensores IMU
        sensor_section = self._create_section(left_panel, "Sensores IMU")

        self.sensor_panel = SensorPanel(
            sensor_section,
            sensor_locations=IMU_CONFIG["locations"],
            height=300
        )
        self.sensor_panel.pack(fill="both", expand=True, pady=(0, 10))

        connect_button = ctk.CTkButton(
            sensor_section,
            text="🔌 Conectar Sensores",
            command=self._connect_sensors,
            height=36,
            fg_color=COLORS["accent_secondary"],
            hover_color="#3a8aef"
        )
        connect_button.pack(fill="x")

        # Sección: Control de Grabación
        record_frame = self._create_section(left_panel, "Control de Grabación")

        self.record_button = ctk.CTkButton(
            record_frame,
            text="▶ Iniciar Grabación",
            command=self._toggle_recording,
            height=50,
            font=ctk.CTkFont(size=FONTS["size_large"], weight=FONTS["weight_bold"]),
            fg_color=COLORS["success"],
            hover_color="#5abf6f"
        )
        self.record_button.pack(fill="x", pady=(0, 10))

        self.timer_label = ctk.CTkLabel(
            record_frame,
            text="00:00",
            font=ctk.CTkFont(size=FONTS["size_xxlarge"], weight=FONTS["weight_bold"]),
            text_color=COLORS["text_primary"]
        )
        self.timer_label.pack(pady=10)

        self.status_label = ctk.CTkLabel(
            record_frame,
            text="Listo para grabar",
            font=ctk.CTkFont(size=FONTS["size_normal"]),
            text_color=COLORS["text_secondary"]
        )
        self.status_label.pack()

    def _create_section(self, parent, title: str) -> ctk.CTkFrame:
        """
        Crea una sección con título.

        Args:
            parent: Widget padre
            title: Título de la sección

        Returns:
            Frame de la sección
        """
        # Título
        title_label = ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(size=FONTS["size_medium"], weight=FONTS["weight_bold"]),
            text_color=COLORS["accent_primary"]
        )
        title_label.pack(padx=15, pady=(20, 10), anchor="w")

        # Frame contenedor
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=False, padx=15, pady=(0, 10))

        return frame

    def _import_force_data(self):
        """Importa datos de la plataforma de fuerza."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de Valkyria",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )

        if not file_path:
            return

        logger.info(f"Importando datos de: {file_path}")
        self.platform_status_label.configure(text="Estado: Importando...")

        if self.force_handler.import_from_excel(file_path):
            # Calibrar
            if self.force_handler.calibrate_zero():
                stats = self.force_handler.get_summary_stats()

                self.platform_status_label.configure(
                    text=f"✓ Datos importados ({stats['duration']:.1f}s, {stats['num_samples']} muestras)"
                )

                # Graficar datos
                self._plot_force_data()

                logger.info("Datos de fuerza importados y graficados correctamente")
            else:
                self.platform_status_label.configure(text="✗ Error en calibración")
                logger.error("Error calibrando datos de fuerza")
        else:
            self.platform_status_label.configure(text="✗ Error en importación")
            logger.error("Error importando datos de fuerza")

    def _plot_force_data(self):
        """Grafica los datos de fuerza importados."""
        if self.force_handler.data is None:
            return

        data = self.force_handler.get_data_dict()

        # Limpiar gráfico
        self.force_plot.clear()

        # Graficar Fz (fuerza vertical)
        self.force_plot.plot_line(
            data['time'],
            data['fz'],
            label='Fz (vertical)',
            color=COLORS["plot_line_1"],
            linewidth=2
        )

        # Configurar gráfico
        self.force_plot.set_labels(
            xlabel='Tiempo (s)',
            ylabel='Fuerza (N)',
            title='Fuerza Vertical (Fz)'
        )
        self.force_plot.add_grid()
        self.force_plot.add_legend()
        self.force_plot.refresh()

        logger.debug("Gráfico de fuerzas actualizado")

    def _connect_sensors(self):
        """Conecta los sensores IMU (placeholder)."""
        logger.info("Conectando sensores IMU...")

        # Simular conexión
        self.sensor_panel.update_all_sensors("connecting")
        self.after(1000, lambda: self.sensor_panel.update_all_sensors("connected"))

        logger.info("Sensores conectados (simulado)")

    def _toggle_recording(self):
        """Alterna entre iniciar y detener grabación."""
        if not self.is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        """Inicia la grabación."""
        logger.info("Iniciando grabación...")

        self.is_recording = True
        self.record_button.configure(
            text="■ Detener Grabación",
            fg_color=COLORS["error"],
            hover_color="#ff5252"
        )
        self.status_label.configure(text="Grabando...")

        logger.info("Grabación iniciada")

    def _stop_recording(self):
        """Detiene la grabación."""
        logger.info("Deteniendo grabación...")

        self.is_recording = False
        self.record_button.configure(
            text="▶ Iniciar Grabación",
            fg_color=COLORS["success"],
            hover_color="#5abf6f"
        )
        self.status_label.configure(text="Grabación completada")

        logger.info("Grabación detenida")
