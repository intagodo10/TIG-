"""
Vista de captura de datos.

Permite capturar datos de sensores y plataforma de fuerza.
"""

import customtkinter as ctk
import numpy as np
import asyncio
from typing import Optional, Callable, Dict
from tkinter import filedialog, messagebox
from threading import Thread

from config.ui_theme import COLORS, FONTS
from config.settings import IMU_CONFIG, EXERCISES
from ui.components import SensorPanel, PlotWidget
from ui.dialogs import show_sensor_assignment_dialog
from core.data_acquisition.force_platform import ForcePlatformHandler
from core.data_acquisition.imu_handler import IMUHandler
from core.data_acquisition.xsens_dot_protocol import OutputMode
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
        self.imu_handler = IMUHandler()
        self.is_recording = False
        self.captured_data = None  # Datos capturados para análisis
        self.sensors_connected = False
        self.sensors_calibrated = False

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

        # Botones de sensores
        sensor_buttons_frame = ctk.CTkFrame(sensor_section, fg_color="transparent")
        sensor_buttons_frame.pack(fill="x")

        self.connect_button = ctk.CTkButton(
            sensor_buttons_frame,
            text="🔍 Escanear y Conectar",
            command=self._connect_sensors,
            height=36,
            fg_color=COLORS["accent_secondary"],
            hover_color="#3a8aef"
        )
        self.connect_button.pack(fill="x", pady=(0, 5))

        self.calibrate_button = ctk.CTkButton(
            sensor_buttons_frame,
            text="📐 Calibrar (N-pose)",
            command=self._calibrate_sensors,
            height=36,
            fg_color=COLORS["warning"],
            hover_color="#f0c030",
            state="disabled"
        )
        self.calibrate_button.pack(fill="x")

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
        """Conecta los sensores IMU con escaneo y asignación real."""
        logger.info("Iniciando proceso de conexión de sensores...")

        # Deshabilitar botón
        self.connect_button.configure(state="disabled", text="⏳ Procesando...")

        # Mostrar diálogo de asignación
        required_locations = IMU_CONFIG["locations"]
        assignments = show_sensor_assignment_dialog(self, required_locations)

        if assignments is None:
            # Usuario canceló
            logger.info("Asignación de sensores cancelada por el usuario")
            self.connect_button.configure(state="normal", text="🔍 Escanear y Conectar")
            return

        # Conectar sensores en thread separado
        Thread(target=self._connect_sensors_async, args=(assignments,), daemon=True).start()

    def _connect_sensors_async(self, assignments: Dict[str, str]):
        """
        Conecta sensores de forma asíncrona.

        Args:
            assignments: Diccionario {ubicación: dirección_mac}
        """
        try:
            # Actualizar estado visual
            self.after(0, lambda: self.sensor_panel.update_all_sensors("connecting"))

            # Ejecutar conexión asíncrona
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self.imu_handler.connect_sensors(assignments))
            loop.close()

            if success:
                logger.info("Todos los sensores conectados exitosamente")

                # Configurar sensores (60 Hz, modo Complete Quaternion)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                configured = loop.run_until_complete(
                    self.imu_handler.configure_all_sensors(
                        output_rate=60,
                        output_mode=OutputMode.COMPLETE_QUATERNION
                    )
                )
                loop.close()

                if configured:
                    logger.info("Sensores configurados correctamente")

                    # Actualizar UI
                    self.after(0, self._on_sensors_connected_success)
                else:
                    raise Exception("Error configurando sensores")
            else:
                raise Exception("Error conectando algunos sensores")

        except Exception as e:
            logger.error(f"Error conectando sensores: {e}", exc_info=True)
            self.after(0, lambda: self._on_sensors_connected_error(str(e)))

    def _on_sensors_connected_success(self):
        """Callback cuando los sensores se conectan exitosamente."""
        self.sensors_connected = True

        # Actualizar estado visual
        self.sensor_panel.update_all_sensors("connected")

        # Actualizar botones
        self.connect_button.configure(
            state="normal",
            text="✓ Sensores Conectados",
            fg_color=COLORS["success"]
        )
        self.calibrate_button.configure(state="normal")

        messagebox.showinfo(
            "Sensores Conectados",
            "Todos los sensores se conectaron exitosamente.\n\n"
            "Ahora debes calibrarlos en posición N-pose."
        )

    def _on_sensors_connected_error(self, error_msg: str):
        """Callback cuando hay error conectando sensores."""
        self.sensors_connected = False

        # Actualizar estado visual
        self.sensor_panel.update_all_sensors("error")

        # Rehabilitar botón
        self.connect_button.configure(state="normal", text="🔍 Escanear y Conectar")

        messagebox.showerror(
            "Error de Conexión",
            f"No se pudieron conectar los sensores:\n\n{error_msg}"
        )

    def _calibrate_sensors(self):
        """Calibra los sensores en N-pose."""
        if not self.sensors_connected:
            messagebox.showwarning("Sensores no conectados", "Primero debes conectar los sensores.")
            return

        # Mostrar instrucciones
        response = messagebox.askokcancel(
            "Calibración N-Pose",
            "INSTRUCCIONES DE CALIBRACIÓN:\n\n"
            "1. Párate con pies separados al ancho de hombros\n"
            "2. Brazos relajados a los lados del cuerpo\n"
            "3. Mirada hacia adelante\n"
            "4. Permanece COMPLETAMENTE INMÓVIL durante 5 segundos\n\n"
            "Presiona OK cuando estés listo para iniciar."
        )

        if not response:
            return

        logger.info("Iniciando calibración N-pose...")

        # Deshabilitar botones
        self.calibrate_button.configure(state="disabled", text="⏳ Calibrando...")
        self.connect_button.configure(state="disabled")

        # Ejecutar calibración en thread separado
        Thread(target=self._calibrate_sensors_async, daemon=True).start()

    def _calibrate_sensors_async(self):
        """Ejecuta la calibración de forma asíncrona."""
        try:
            # Countdown visual (3 segundos)
            for i in range(3, 0, -1):
                self.after(0, lambda n=i: self.status_label.configure(text=f"Calibrando en {n}..."))
                import time
                time.sleep(1)

            self.after(0, lambda: self.status_label.configure(text="¡QUIETO! Calibrando..."))

            # Ejecutar calibración (5 segundos)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self.imu_handler.calibrate_all_sensors(duration=5.0))
            loop.close()

            if success:
                logger.info("Calibración completada exitosamente")
                self.after(0, self._on_calibration_success)
            else:
                raise Exception("Error durante la calibración")

        except Exception as e:
            logger.error(f"Error en calibración: {e}", exc_info=True)
            self.after(0, lambda: self._on_calibration_error(str(e)))

    def _on_calibration_success(self):
        """Callback cuando la calibración es exitosa."""
        self.sensors_calibrated = True

        # Actualizar UI
        self.calibrate_button.configure(
            state="normal",
            text="✓ Calibración Completa",
            fg_color=COLORS["success"]
        )
        self.connect_button.configure(state="normal")
        self.status_label.configure(text="Sensores calibrados - Listo para grabar")

        messagebox.showinfo(
            "Calibración Exitosa",
            "Los sensores se calibraron correctamente.\n\n"
            "Ahora puedes iniciar la grabación."
        )

    def _on_calibration_error(self, error_msg: str):
        """Callback cuando hay error en calibración."""
        self.sensors_calibrated = False

        # Rehabilitar botones
        self.calibrate_button.configure(state="normal", text="📐 Calibrar (N-pose)")
        self.connect_button.configure(state="normal")
        self.status_label.configure(text="Error en calibración")

        messagebox.showerror(
            "Error de Calibración",
            f"No se pudo calibrar los sensores:\n\n{error_msg}\n\n"
            "Verifica que estés completamente inmóvil durante el proceso."
        )

    def _toggle_recording(self):
        """Alterna entre iniciar y detener grabación."""
        if not self.is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        """Inicia la grabación."""
        # Verificar que los sensores estén calibrados
        if not self.sensors_calibrated:
            messagebox.showwarning(
                "Sensores no calibrados",
                "Debes calibrar los sensores antes de grabar."
            )
            return

        logger.info("Iniciando grabación de datos IMU...")

        # Limpiar buffers de datos anteriores
        self.imu_handler.clear_all_buffers()

        # Iniciar streaming en thread separado
        Thread(target=self._start_streaming_async, daemon=True).start()

        self.is_recording = True
        self.record_button.configure(
            text="■ Detener Grabación",
            fg_color=COLORS["error"],
            hover_color="#ff5252"
        )
        self.status_label.configure(text="Grabando datos IMU...")

        # Deshabilitar botones de configuración
        self.connect_button.configure(state="disabled")
        self.calibrate_button.configure(state="disabled")

        logger.info("Grabación iniciada")

    def _start_streaming_async(self):
        """Inicia el streaming de datos de forma asíncrona."""
        try:
            # Callback para actualizar gráficos en tiempo real
            def data_callback(location: str, imu_data):
                """Callback para datos en tiempo real."""
                # Aquí podrías actualizar gráficos en tiempo real si lo deseas
                pass

            # Iniciar streaming
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                self.imu_handler.start_streaming_all(callback=data_callback)
            )
            loop.close()

            logger.info("Streaming iniciado en todos los sensores")

        except Exception as e:
            logger.error(f"Error iniciando streaming: {e}", exc_info=True)
            self.after(0, lambda: self._on_streaming_error(str(e)))

    def _on_streaming_error(self, error_msg: str):
        """Callback cuando hay error en streaming."""
        self.is_recording = False

        self.record_button.configure(
            text="▶ Iniciar Grabación",
            fg_color=COLORS["success"],
            hover_color="#5abf6f"
        )
        self.status_label.configure(text="Error en grabación")

        self.connect_button.configure(state="normal")
        self.calibrate_button.configure(state="normal")

        messagebox.showerror(
            "Error de Grabación",
            f"Error iniciando la grabación:\n\n{error_msg}"
        )

    def _stop_recording(self):
        """Detiene la grabación."""
        logger.info("Deteniendo grabación...")

        # Detener streaming en thread separado
        Thread(target=self._stop_streaming_async, daemon=True).start()

        self.is_recording = False
        self.record_button.configure(
            text="▶ Iniciar Grabación",
            fg_color=COLORS["success"],
            hover_color="#5abf6f"
        )
        self.status_label.configure(text="Procesando datos capturados...")

        logger.info("Grabación detenida")

    def _stop_streaming_async(self):
        """Detiene el streaming de forma asíncrona."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.imu_handler.stop_streaming_all())
            loop.close()

            logger.info("Streaming detenido en todos los sensores")

            # Habilitar análisis
            self.after(0, self._on_streaming_stopped)

        except Exception as e:
            logger.error(f"Error deteniendo streaming: {e}", exc_info=True)

    def _on_streaming_stopped(self):
        """Callback cuando el streaming se detiene exitosamente."""
        # Rehabilitar botones
        self.connect_button.configure(state="normal")
        self.calibrate_button.configure(state="normal")

        # Habilitar botón de análisis
        self.analyze_button.configure(state="normal")
        self.status_label.configure(text="Grabación completada - Listo para analizar")

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

            # Obtener datos de IMU (reales o sintéticos)
            if self.sensors_connected and self.sensors_calibrated:
                # Usar datos reales de los sensores
                logger.info("Usando datos REALES de los sensores IMU")
                time_imu, imu_data = self._get_real_imu_data()
            else:
                # Generar datos sintéticos (fallback para testing sin sensores)
                logger.warning("Usando datos SINTÉTICOS de IMU (sensores no conectados)")
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

    def _get_real_imu_data(self):
        """
        Obtiene datos reales de los sensores IMU.

        Returns:
            Tupla (time, imu_data) con los datos capturados
        """
        # Obtener datos de todos los sensores
        all_data = self.imu_handler.get_all_data()

        if not all_data:
            raise ValueError("No hay datos capturados de los sensores")

        # Convertir a formato esperado por el analizador
        imu_data = {}
        time_arrays = []

        for location, data_list in all_data.items():
            if not data_list:
                logger.warning(f"No hay datos para sensor {location}")
                continue

            # Extraer timestamps
            timestamps = np.array([d.timestamp for d in data_list])
            time_arrays.append(timestamps)

            # Extraer datos
            accelerations = np.array([d.acceleration for d in data_list])
            angular_velocities = np.array([d.angular_velocity for d in data_list])
            quaternions = np.array([d.quaternion for d in data_list])

            imu_data[location] = {
                'acceleration': accelerations,
                'angular_velocity': angular_velocities,
                'quaternion': quaternions
            }

            logger.info(f"Sensor {location}: {len(data_list)} muestras capturadas")

        # Usar el array de tiempo más largo (o el primero si todos son iguales)
        time_imu = time_arrays[0] if time_arrays else np.array([])

        logger.info(f"Datos IMU reales obtenidos: {len(time_imu)} muestras, {len(imu_data)} sensores")

        return time_imu, imu_data

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
