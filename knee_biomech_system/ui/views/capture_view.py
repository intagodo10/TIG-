"""
Vista de captura de datos.

Permite capturar datos de sensores y plataforma de fuerza.
"""

import customtkinter as ctk
import numpy as np
from typing import Optional, Callable
from tkinter import filedialog

from config.ui_theme import COLORS, FONTS
from config.settings import IMU_CONFIG, EXERCISES
from ui.components import SensorPanel, PlotWidget
from core.data_acquisition.force_platform import ForcePlatformHandler
from core.analysis.biomech_analyzer import BiomechAnalyzer
from models.patient import Patient
from utils.logger import get_logger

logger = get_logger(__name__)


class CaptureView(ctk.CTkFrame):
    """
    Vista de captura de datos en tiempo real.

    Permite conectar sensores, configurar ejercicios y capturar datos.
    """

    def __init__(self, master, on_analysis_complete: Optional[Callable] = None, **kwargs):
        """
        Inicializa la vista de captura.

        Args:
            master: Widget padre
            on_analysis_complete: Callback cuando se completa el análisis
        """
        super().__init__(master, **kwargs)

        self.on_analysis_complete = on_analysis_complete
        self.force_handler = ForcePlatformHandler()
        self.is_recording = False
        self.captured_data = None  # Datos capturados para análisis

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

        # Botón de análisis
        self.analyze_button = ctk.CTkButton(
            record_frame,
            text="🔬 Analizar Datos",
            command=self._analyze_data,
            height=45,
            font=ctk.CTkFont(size=FONTS["size_medium"], weight=FONTS["weight_bold"]),
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            state="disabled"
        )
        self.analyze_button.pack(fill="x", pady=(15, 0))

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

                # Habilitar botón de análisis
                self.analyze_button.configure(state="normal")

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

    def _analyze_data(self):
        """Ejecuta el análisis de los datos capturados."""
        if self.force_handler.data is None:
            logger.warning("No hay datos de fuerza para analizar")
            return

        logger.info("Iniciando análisis de datos...")
        self.status_label.configure(text="Analizando datos...")
        self.analyze_button.configure(state="disabled")

        try:
            # Obtener datos de fuerza
            force_data_dict = self.force_handler.get_data_dict()
            time_force = force_data_dict['time']
            force_data = {
                'fx': force_data_dict['fx'],
                'fy': force_data_dict['fy'],
                'fz': force_data_dict['fz'],
                'mx': force_data_dict['mx'],
                'my': force_data_dict['my'],
                'mz': force_data_dict['mz']
            }

            # Generar datos sintéticos de IMU (simulación temporal)
            # En producción, esto vendría de los sensores reales
            time_imu, imu_data = self._generate_synthetic_imu_data(
                duration=time_force[-1],
                fs=60.0
            )

            # Crear paciente de prueba si no existe
            # En producción, esto vendría de la vista de paciente
            patient = Patient(
                patient_id="DEMO001",
                name="Paciente Demo",
                age=30,
                mass=70.0,
                height=1.75,
                sex="M",
                affected_limb="derecha"
            )

            # Crear analizador
            analyzer = BiomechAnalyzer(patient)

            # Obtener tipo de ejercicio seleccionado
            exercise_name = self.exercise_combo.get()
            exercise_type = "squat"  # Por defecto
            for key, value in EXERCISES.items():
                if value["name"] == exercise_name:
                    exercise_type = key
                    break

            # Ejecutar análisis completo
            result = analyzer.analyze_full_session(
                time_imu,
                imu_data,
                time_force,
                force_data,
                exercise_type=exercise_type
            )

            if result.success:
                logger.info("Análisis completado exitosamente")
                self.status_label.configure(text="✓ Análisis completado")

                # Llamar callback si existe
                if self.on_analysis_complete:
                    self.on_analysis_complete(result)
            else:
                logger.error(f"Análisis falló: {result.summary}")
                self.status_label.configure(text="✗ Error en análisis")

        except Exception as e:
            logger.error(f"Error durante el análisis: {str(e)}", exc_info=True)
            self.status_label.configure(text="✗ Error en análisis")

        finally:
            self.analyze_button.configure(state="normal")

    def _generate_synthetic_imu_data(self, duration: float, fs: float = 60.0):
        """
        Genera datos sintéticos de IMU (temporal hasta tener sensores reales).

        Args:
            duration: Duración en segundos
            fs: Frecuencia de muestreo

        Returns:
            Tupla (time, imu_data)
        """
        n_samples = int(duration * fs)
        time = np.linspace(0, duration, n_samples)

        # Frecuencia de movimiento
        frequency = 0.2  # Hz (ciclo de 5 segundos)

        imu_data = {}

        for location in ['pelvis', 'femur_right', 'tibia_right']:
            # Aceleración simulada
            acc_x = np.random.randn(n_samples) * 0.5
            acc_y = np.random.randn(n_samples) * 0.5
            acc_z = 9.81 + np.random.randn(n_samples) * 0.5

            acceleration = np.column_stack([acc_x, acc_y, acc_z])

            # Velocidad angular simulada
            phase_offset = {'pelvis': 0, 'femur_right': 0.2, 'tibia_right': 0.5}
            offset = phase_offset.get(location, 0)

            gyro_x = np.random.randn(n_samples) * 0.1
            gyro_y = 0.5 * np.sin(2 * np.pi * frequency * time + offset) + np.random.randn(n_samples) * 0.05
            gyro_z = np.random.randn(n_samples) * 0.1

            angular_velocity = np.column_stack([gyro_x, gyro_y, gyro_z])

            # Quaternions
            qw = np.ones(n_samples)
            qx = np.zeros(n_samples)
            qy = np.zeros(n_samples)
            qz = np.zeros(n_samples)

            quaternion = np.column_stack([qw, qx, qy, qz])

            imu_data[location] = {
                'acceleration': acceleration,
                'angular_velocity': angular_velocity,
                'quaternion': quaternion
            }

        return time, imu_data
