"""
Analizador biomecánico integrado.

Orquesta el flujo completo de análisis: sincronización, procesamiento,
cálculo de métricas y generación de alertas.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from core.data_acquisition.synchronizer import DataSynchronizer, SyncResult
from core.processing.signal_processing import SignalProcessor
from core.analysis.metrics_calculator import (
    MetricsCalculator,
    KinematicMetrics,
    DynamicMetrics,
    ForceMetrics,
    SymmetryMetrics
)
from core.analysis.alert_system import AlertSystem, Alert
from models.patient import Patient
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AnalysisResult:
    """
    Resultado completo de análisis biomecánico.

    Attributes:
        success: Si el análisis fue exitoso
        sync_result: Resultado de sincronización
        kinematic_metrics: Métricas cinemáticas (dict por articulación)
        dynamic_metrics: Métricas dinámicas (dict por articulación)
        force_metrics: Métricas de fuerza (dict por contacto)
        symmetry_metrics: Métricas de simetría
        alerts: Lista de alertas generadas
        processed_data: Datos procesados y filtrados
        summary: Resumen textual del análisis
    """
    success: bool
    sync_result: Optional[SyncResult]
    kinematic_metrics: Dict[str, KinematicMetrics]
    dynamic_metrics: Dict[str, DynamicMetrics]
    force_metrics: Dict[str, ForceMetrics]
    symmetry_metrics: Optional[SymmetryMetrics]
    alerts: List[Alert]
    processed_data: Dict[str, np.ndarray]
    summary: str


class BiomechAnalyzer:
    """
    Analizador biomecánico integrado.

    Coordina todos los módulos de procesamiento y análisis para
    generar resultados completos a partir de datos crudos.
    """

    def __init__(self, patient: Optional[Patient] = None):
        """
        Inicializa el analizador.

        Args:
            patient: Información del paciente (opcional)
        """
        self.patient = patient

        # Inicializar componentes
        self.synchronizer = DataSynchronizer()
        self.signal_processor = SignalProcessor()
        self.metrics_calculator = MetricsCalculator()
        self.alert_system = AlertSystem()

        logger.info("BiomechAnalyzer inicializado")

    def analyze_full_session(self,
                            time_imu: np.ndarray,
                            imu_data: Dict[str, Dict[str, np.ndarray]],
                            time_force: np.ndarray,
                            force_data: Dict[str, np.ndarray],
                            exercise_type: str = "squat") -> AnalysisResult:
        """
        Realiza análisis completo de una sesión de captura.

        Args:
            time_imu: Vector de tiempo IMU (s)
            imu_data: Datos IMU {sensor_location: {data_type: array}}
            time_force: Vector de tiempo fuerza (s)
            force_data: Datos de fuerza {channel: array}
            exercise_type: Tipo de ejercicio ("squat", "jump", "lunge", etc.)

        Returns:
            AnalysisResult con todos los resultados
        """
        try:
            logger.info(f"=== Iniciando análisis completo de sesión ({exercise_type}) ===")

            # ========== FASE 1: SINCRONIZACIÓN ==========
            logger.info("FASE 1: Sincronizando señales...")
            sync_result = self.synchronizer.synchronize(
                time_imu, imu_data, time_force, force_data
            )

            if not sync_result.success:
                logger.error("Fallo en sincronización")
                return self._failed_result("Sincronización fallida")

            # Verificar calidad de sincronización
            sync_alert = self.alert_system.check_sync_quality_alert(sync_result.sync_quality)
            if sync_alert:
                logger.warning(f"Alerta de sincronización: {sync_alert.title}")

            # ========== FASE 2: PROCESAMIENTO DE SEÑALES ==========
            logger.info("FASE 2: Procesando señales...")
            processed_data = self._process_signals(sync_result)

            # Verificar calidad de datos
            self._check_data_quality(processed_data)

            # ========== FASE 3: DETECCIÓN DE EVENTOS ==========
            logger.info("FASE 3: Detectando eventos...")
            events = self._detect_events(processed_data, exercise_type)

            # ========== FASE 4: CÁLCULO DE MÉTRICAS ==========
            logger.info("FASE 4: Calculando métricas...")
            kinematic_metrics = self._calculate_kinematic_metrics(
                sync_result.time_common,
                processed_data,
                events
            )
            dynamic_metrics = self._calculate_dynamic_metrics(
                sync_result.time_common,
                processed_data,
                events
            )
            force_metrics = self._calculate_force_metrics(
                sync_result.time_common,
                processed_data,
                events,
                exercise_type
            )
            symmetry_metrics = self._calculate_symmetry_metrics(
                kinematic_metrics,
                dynamic_metrics
            )

            # ========== FASE 5: GENERACIÓN DE ALERTAS ==========
            logger.info("FASE 5: Evaluando alertas...")
            self._generate_biomechanical_alerts(
                kinematic_metrics,
                dynamic_metrics,
                force_metrics,
                symmetry_metrics,
                exercise_type
            )

            # ========== FASE 6: GENERACIÓN DE RESUMEN ==========
            logger.info("FASE 6: Generando resumen...")
            summary = self._generate_summary(
                kinematic_metrics,
                dynamic_metrics,
                force_metrics,
                symmetry_metrics
            )

            logger.info("=== Análisis completado exitosamente ===")

            return AnalysisResult(
                success=True,
                sync_result=sync_result,
                kinematic_metrics=kinematic_metrics,
                dynamic_metrics=dynamic_metrics,
                force_metrics=force_metrics,
                symmetry_metrics=symmetry_metrics,
                alerts=self.alert_system.get_active_alerts(),
                processed_data=processed_data,
                summary=summary
            )

        except Exception as e:
            logger.error(f"Error en análisis completo: {str(e)}", exc_info=True)
            return self._failed_result(f"Error: {str(e)}")

    def _process_signals(self, sync_result: SyncResult) -> Dict[str, np.ndarray]:
        """
        Procesa todas las señales sincronizadas.

        Args:
            sync_result: Resultado de sincronización

        Returns:
            Diccionario con señales procesadas
        """
        processed = {}

        # Frecuencia de muestreo común
        fs = 1.0 / np.mean(np.diff(sync_result.time_common))

        # Procesar fuerza vertical
        fz_raw = sync_result.force_data_synced['fz']
        fz_filtered = self.signal_processor.filter_force(fz_raw, fs)
        processed['fz'] = fz_filtered

        # Procesar otras componentes de fuerza
        for channel in ['fx', 'fy']:
            if channel in sync_result.force_data_synced:
                processed[channel] = self.signal_processor.filter_force(
                    sync_result.force_data_synced[channel], fs
                )

        # Procesar datos IMU
        for sensor_location, sensor_data in sync_result.imu_data_synced.items():
            # Aceleración
            if 'acceleration' in sensor_data:
                acc_filtered = self.signal_processor.filter_imu_acceleration(
                    sensor_data['acceleration'], fs
                )
                processed[f'{sensor_location}_acc'] = acc_filtered

            # Velocidad angular
            if 'angular_velocity' in sensor_data:
                gyro_filtered = self.signal_processor.filter_imu_gyro(
                    sensor_data['angular_velocity'], fs
                )
                processed[f'{sensor_location}_gyro'] = gyro_filtered

            # Quaternions (sin filtrar - son orientaciones)
            if 'quaternion' in sensor_data:
                processed[f'{sensor_location}_quat'] = sensor_data['quaternion']

        logger.info(f"Señales procesadas: {len(processed)} canales")

        return processed

    def _check_data_quality(self, processed_data: Dict[str, np.ndarray]):
        """
        Verifica calidad de todas las señales procesadas.

        Args:
            processed_data: Datos procesados
        """
        for signal_name, signal in processed_data.items():
            if signal.ndim == 1:
                # Señal 1D
                alert = self.alert_system.check_data_quality_alert(signal, signal_name)
                if alert:
                    logger.warning(f"Alerta de calidad en {signal_name}: {alert.title}")
            else:
                # Señal multidimensional - verificar cada componente
                for i in range(signal.shape[1]):
                    alert = self.alert_system.check_data_quality_alert(
                        signal[:, i], f"{signal_name}[{i}]"
                    )
                    if alert:
                        logger.warning(f"Alerta de calidad en {signal_name}[{i}]: {alert.title}")

    def _detect_events(self,
                      processed_data: Dict[str, np.ndarray],
                      exercise_type: str) -> Dict[str, List[Tuple[int, int]]]:
        """
        Detecta eventos (contactos, ciclos) en los datos.

        Args:
            processed_data: Datos procesados
            exercise_type: Tipo de ejercicio

        Returns:
            Diccionario con eventos detectados
        """
        events = {}

        # Detectar contactos de pie con plataforma de fuerza
        if 'fz' in processed_data:
            fz = processed_data['fz']

            # Umbral según tipo de ejercicio
            thresholds = {
                "squat": 50.0,  # N
                "jump": 20.0,
                "walk": 20.0,
                "lunge": 50.0
            }
            threshold = thresholds.get(exercise_type, 30.0)

            contacts, liftoffs = self.signal_processor.detect_grf_contacts(
                fz, threshold=threshold, fs=100, min_contact_time=0.1
            )

            # Crear lista de eventos (inicio, fin)
            contact_events = list(zip(contacts, liftoffs))
            events['foot_contacts'] = contact_events

            logger.info(f"Detectados {len(contact_events)} contactos/repeticiones")

        return events

    def _calculate_kinematic_metrics(self,
                                    time: np.ndarray,
                                    processed_data: Dict[str, np.ndarray],
                                    events: Dict) -> Dict[str, KinematicMetrics]:
        """
        Calcula métricas cinemáticas para cada articulación.

        Args:
            time: Vector de tiempo
            processed_data: Datos procesados
            events: Eventos detectados

        Returns:
            Diccionario de métricas por articulación
        """
        kinematic_metrics = {}

        # TODO: Aquí se integraría con OpenSim para obtener ángulos articulares
        # Por ahora, calcularemos métricas aproximadas desde datos IMU

        # Ejemplo: Calcular ángulo de rodilla aproximado desde giroscopio
        if 'femur_right_gyro' in processed_data and 'tibia_right_gyro' in processed_data:
            # Velocidad angular relativa
            femur_gyro = processed_data['femur_right_gyro']
            tibia_gyro = processed_data['tibia_right_gyro']

            # Componente sagital (Y - flexión/extensión)
            relative_angular_velocity = femur_gyro[:, 1] - tibia_gyro[:, 1]

            # Integrar para obtener ángulo (aproximación)
            dt = np.mean(np.diff(time))
            knee_angle = np.cumsum(relative_angular_velocity) * dt
            knee_angle = np.rad2deg(knee_angle)  # Convertir a grados

            # Calcular métricas
            metrics = self.metrics_calculator.calculate_kinematic_metrics(time, knee_angle)
            kinematic_metrics['knee_right'] = metrics

            logger.info(f"ROM rodilla derecha: {metrics.rom:.1f}°")

        # TODO: Repetir para rodilla izquierda, cadera, tobillo

        return kinematic_metrics

    def _calculate_dynamic_metrics(self,
                                  time: np.ndarray,
                                  processed_data: Dict[str, np.ndarray],
                                  events: Dict) -> Dict[str, DynamicMetrics]:
        """
        Calcula métricas dinámicas (momentos, potencia).

        Args:
            time: Vector de tiempo
            processed_data: Datos procesados
            events: Eventos detectados

        Returns:
            Diccionario de métricas por articulación
        """
        dynamic_metrics = {}

        # TODO: Integrar con OpenSim Inverse Dynamics para obtener momentos reales

        # Por ahora, retornar diccionario vacío
        # En implementación completa, esto vendría de OpenSim ID

        return dynamic_metrics

    def _calculate_force_metrics(self,
                                time: np.ndarray,
                                processed_data: Dict[str, np.ndarray],
                                events: Dict,
                                exercise_type: str) -> Dict[str, ForceMetrics]:
        """
        Calcula métricas de fuerza para cada contacto.

        Args:
            time: Vector de tiempo
            processed_data: Datos procesados
            events: Eventos detectados
            exercise_type: Tipo de ejercicio

        Returns:
            Diccionario de métricas por contacto
        """
        force_metrics_dict = {}

        if 'fz' in processed_data and 'foot_contacts' in events:
            fz = processed_data['fz']
            contacts = events['foot_contacts']

            # Peso corporal
            body_weight = self.patient.body_weight if self.patient else 700.0  # N (default)

            # Calcular métricas para cada contacto
            for i, (start, end) in enumerate(contacts):
                metrics = self.metrics_calculator.calculate_force_metrics(
                    time, fz, body_weight, start, end
                )
                force_metrics_dict[f'contact_{i+1}'] = metrics

                logger.info(f"Contacto {i+1}: GRF pico = {metrics.peak_grf:.2f} BW, "
                          f"Contacto = {metrics.contact_time:.3f} s")

        return force_metrics_dict

    def _calculate_symmetry_metrics(self,
                                   kinematic_metrics: Dict[str, KinematicMetrics],
                                   dynamic_metrics: Dict[str, DynamicMetrics]) -> Optional[SymmetryMetrics]:
        """
        Calcula métricas de simetría bilateral.

        Args:
            kinematic_metrics: Métricas cinemáticas
            dynamic_metrics: Métricas dinámicas

        Returns:
            SymmetryMetrics o None si no hay datos bilaterales
        """
        # Verificar si hay datos de ambas piernas
        if 'knee_right' in kinematic_metrics and 'knee_left' in kinematic_metrics:
            right_rom = kinematic_metrics['knee_right'].rom
            left_rom = kinematic_metrics['knee_left'].rom

            # Crear arrays para cálculo
            right_data = np.array([right_rom])
            left_data = np.array([left_rom])

            metrics = self.metrics_calculator.calculate_symmetry_metrics(right_data, left_data)

            logger.info(f"Simetría: SI = {metrics.symmetry_index:.1f}%, "
                       f"Ratio = {metrics.asymmetry_ratio:.2f}")

            return metrics

        return None

    def _generate_biomechanical_alerts(self,
                                      kinematic_metrics: Dict[str, KinematicMetrics],
                                      dynamic_metrics: Dict[str, DynamicMetrics],
                                      force_metrics: Dict[str, ForceMetrics],
                                      symmetry_metrics: Optional[SymmetryMetrics],
                                      exercise_type: str):
        """
        Genera alertas biomecánicas basadas en todas las métricas.

        Args:
            kinematic_metrics: Métricas cinemáticas
            dynamic_metrics: Métricas dinámicas
            force_metrics: Métricas de fuerza
            symmetry_metrics: Métricas de simetría
            exercise_type: Tipo de ejercicio
        """
        # Alertas cinemáticas
        for joint, metrics in kinematic_metrics.items():
            self.alert_system.check_rom_alert(metrics.rom, joint.replace('_right', '').replace('_left', ''))
            self.alert_system.check_angular_velocity_alert(metrics.angular_velocity_peak)

        # Alertas dinámicas
        if self.patient:
            for joint, metrics in dynamic_metrics.items():
                self.alert_system.check_moment_alert(
                    metrics.peak_moment * self.patient.mass,  # Convertir a Nm
                    self.patient.mass
                )

        # Alertas de fuerza
        if self.patient:
            body_weight = self.patient.body_weight

            for contact_id, metrics in force_metrics.items():
                self.alert_system.check_grf_alert(
                    metrics.peak_grf * body_weight,  # Convertir a N
                    body_weight,
                    exercise_type
                )
                self.alert_system.check_loading_rate_alert(
                    metrics.loading_rate * body_weight,  # Convertir a N/s
                    body_weight
                )

        # Alertas de simetría
        if symmetry_metrics:
            self.alert_system.check_symmetry_alert(symmetry_metrics.symmetry_index)

    def _generate_summary(self,
                         kinematic_metrics: Dict[str, KinematicMetrics],
                         dynamic_metrics: Dict[str, DynamicMetrics],
                         force_metrics: Dict[str, ForceMetrics],
                         symmetry_metrics: Optional[SymmetryMetrics]) -> str:
        """
        Genera resumen textual del análisis.

        Args:
            kinematic_metrics: Métricas cinemáticas
            dynamic_metrics: Métricas dinámicas
            force_metrics: Métricas de fuerza
            symmetry_metrics: Métricas de simetría

        Returns:
            Resumen en texto
        """
        lines = ["=== RESUMEN DE ANÁLISIS BIOMECÁNICO ===\n"]

        # Información del paciente
        if self.patient:
            lines.append(f"Paciente: {self.patient.name} (ID: {self.patient.patient_id})")
            lines.append(f"Masa: {self.patient.mass} kg | Altura: {self.patient.height} m | "
                        f"IMC: {self.patient.bmi:.1f}\n")

        # Métricas cinemáticas
        if kinematic_metrics:
            lines.append("--- CINEMÁTICA ---")
            for joint, metrics in kinematic_metrics.items():
                lines.append(f"{joint.upper()}: ROM = {metrics.rom:.1f}°, "
                           f"Flexión máx = {metrics.peak_flexion:.1f}°, "
                           f"Vel. ang. máx = {metrics.angular_velocity_peak:.1f} deg/s")
            lines.append("")

        # Métricas de fuerza
        if force_metrics:
            lines.append("--- CINÉTICA ---")
            for contact_id, metrics in force_metrics.items():
                lines.append(f"{contact_id.upper()}: GRF pico = {metrics.peak_grf:.2f} BW, "
                           f"Tasa carga = {metrics.loading_rate:.1f} BW/s, "
                           f"Tiempo contacto = {metrics.contact_time:.3f} s")
            lines.append("")

        # Métricas de simetría
        if symmetry_metrics:
            lines.append("--- SIMETRÍA ---")
            lines.append(f"Índice de simetría: {symmetry_metrics.symmetry_index:.1f}%")
            lines.append(f"Ratio asimetría: {symmetry_metrics.asymmetry_ratio:.2f}")
            lines.append("")

        # Alertas
        alert_summary = self.alert_system.get_alert_summary()
        if alert_summary['total'] > 0:
            lines.append("--- ALERTAS ---")
            lines.append(f"Total: {alert_summary['total']} | "
                        f"Críticas: {alert_summary['critical']} | "
                        f"Errores: {alert_summary['error']} | "
                        f"Advertencias: {alert_summary['warning']}")

        return "\n".join(lines)

    def _failed_result(self, error_message: str) -> AnalysisResult:
        """
        Crea un resultado de análisis fallido.

        Args:
            error_message: Mensaje de error

        Returns:
            AnalysisResult con success=False
        """
        return AnalysisResult(
            success=False,
            sync_result=None,
            kinematic_metrics={},
            dynamic_metrics={},
            force_metrics={},
            symmetry_metrics=None,
            alerts=[],
            processed_data={},
            summary=f"ANÁLISIS FALLIDO: {error_message}"
        )

    def get_alerts(self) -> List[Alert]:
        """Obtiene todas las alertas activas."""
        return self.alert_system.get_active_alerts()

    def clear_alerts(self):
        """Limpia todas las alertas."""
        self.alert_system.clear_alerts()
