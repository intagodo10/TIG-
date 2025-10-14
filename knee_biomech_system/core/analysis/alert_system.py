"""
Sistema de alertas biomecánicas.

Detecta y notifica anomalías, valores fuera de rango y patrones
de riesgo durante la evaluación y análisis de movimiento.
"""

import numpy as np
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from config.settings import ALERT_THRESHOLDS, REFERENCE_VALUES
from utils.logger import get_logger

logger = get_logger(__name__)


class AlertSeverity(Enum):
    """Niveles de severidad de alertas."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertCategory(Enum):
    """Categorías de alertas."""
    KINEMATIC = "kinematic"
    DYNAMIC = "dynamic"
    FORCE = "force"
    SYMMETRY = "symmetry"
    VALIDATION = "validation"
    TECHNICAL = "technical"


@dataclass
class Alert:
    """
    Alerta biomecánica.

    Attributes:
        id: ID único de la alerta
        timestamp: Momento de generación
        severity: Nivel de severidad
        category: Categoría de la alerta
        title: Título corto
        message: Mensaje detallado
        value: Valor que generó la alerta
        threshold: Umbral excedido
        recommendation: Recomendación de acción
        acknowledged: Si la alerta ha sido reconocida
    """
    id: str
    timestamp: datetime
    severity: AlertSeverity
    category: AlertCategory
    title: str
    message: str
    value: Optional[float] = None
    threshold: Optional[float] = None
    recommendation: Optional[str] = None
    acknowledged: bool = False


class AlertSystem:
    """
    Sistema de alertas biomecánicas.

    Detecta condiciones anormales y genera alertas con recomendaciones
    para el fisioterapeuta o investigador.
    """

    def __init__(self, callback: Optional[Callable[[Alert], None]] = None):
        """
        Inicializa el sistema de alertas.

        Args:
            callback: Función callback para notificaciones (opcional)
        """
        self.alerts: List[Alert] = []
        self.callback = callback
        self.alert_counter = 0

        # Cargar umbrales de configuración
        self.thresholds = ALERT_THRESHOLDS
        self.reference_values = REFERENCE_VALUES

        logger.info("AlertSystem inicializado")

    # ==================== ALERTAS CINEMÁTICAS ====================

    def check_rom_alert(self, rom: float, joint: str = "knee") -> Optional[Alert]:
        """
        Verifica si el ROM está fuera de rango normal.

        Args:
            rom: Rango de movimiento (grados)
            joint: Articulación ("knee", "hip", "ankle")

        Returns:
            Alert si hay problema, None si está bien
        """
        try:
            # Obtener rango de referencia
            if joint == "knee":
                ref_min, ref_max = self.reference_values["knee_flexion_rom"]
            else:
                logger.warning(f"Articulación '{joint}' no tiene referencia definida")
                return None

            # ROM demasiado bajo (rigidez)
            if rom < ref_min * 0.7:  # < 70% del mínimo normal
                return self._create_alert(
                    severity=AlertSeverity.ERROR,
                    category=AlertCategory.KINEMATIC,
                    title="ROM Limitado",
                    message=f"El rango de movimiento de {joint} es {rom:.1f}°, "
                           f"significativamente inferior al rango normal ({ref_min:.1f}-{ref_max:.1f}°).",
                    value=rom,
                    threshold=ref_min * 0.7,
                    recommendation="Evaluar rigidez articular, contracturas o dolor limitante. "
                                  "Considerar ejercicios de movilidad progresiva."
                )

            # ROM bajo (advertencia)
            elif rom < ref_min:
                return self._create_alert(
                    severity=AlertSeverity.WARNING,
                    category=AlertCategory.KINEMATIC,
                    title="ROM Reducido",
                    message=f"El rango de movimiento de {joint} ({rom:.1f}°) está por debajo "
                           f"del rango normal ({ref_min:.1f}-{ref_max:.1f}°).",
                    value=rom,
                    threshold=ref_min,
                    recommendation="Continuar monitoreando. Considerar protocolo de movilidad si persiste."
                )

            # ROM excesivo (hipermovilidad)
            elif rom > ref_max * 1.2:  # > 120% del máximo normal
                return self._create_alert(
                    severity=AlertSeverity.WARNING,
                    category=AlertCategory.KINEMATIC,
                    title="Hipermovilidad Detectada",
                    message=f"El rango de movimiento de {joint} ({rom:.1f}°) excede "
                           f"significativamente el rango normal ({ref_min:.1f}-{ref_max:.1f}°).",
                    value=rom,
                    threshold=ref_max * 1.2,
                    recommendation="Evaluar laxitud ligamentaria e inestabilidad articular. "
                                  "Considerar fortalecimiento muscular periarticular."
                )

            return None

        except Exception as e:
            logger.error(f"Error verificando ROM: {str(e)}")
            return None

    def check_angular_velocity_alert(self, angular_velocity: float) -> Optional[Alert]:
        """
        Verifica velocidad angular excesiva (riesgo de lesión).

        Args:
            angular_velocity: Velocidad angular máxima (deg/s)

        Returns:
            Alert si hay problema, None si está bien
        """
        try:
            threshold = self.thresholds["max_angular_velocity"]

            if angular_velocity > threshold:
                severity = AlertSeverity.CRITICAL if angular_velocity > threshold * 1.5 else AlertSeverity.WARNING

                return self._create_alert(
                    severity=severity,
                    category=AlertCategory.KINEMATIC,
                    title="Velocidad Angular Excesiva",
                    message=f"Velocidad angular de {angular_velocity:.1f} deg/s excede el umbral "
                           f"seguro ({threshold:.1f} deg/s).",
                    value=angular_velocity,
                    threshold=threshold,
                    recommendation="Reducir velocidad de ejecución. Riesgo elevado de lesión ligamentaria "
                                  "o meniscal con movimientos balísticos no controlados."
                )

            return None

        except Exception as e:
            logger.error(f"Error verificando velocidad angular: {str(e)}")
            return None

    # ==================== ALERTAS DINÁMICAS ====================

    def check_moment_alert(self, moment: float, body_mass: float) -> Optional[Alert]:
        """
        Verifica momentos articulares excesivos.

        Args:
            moment: Momento articular (Nm)
            body_mass: Masa corporal (kg)

        Returns:
            Alert si hay problema, None si está bien
        """
        try:
            moment_normalized = moment / body_mass  # Nm/kg

            # Umbral de momento máximo (de config)
            threshold = self.thresholds.get("max_knee_moment", 3.5)  # Nm/kg

            if moment_normalized > threshold:
                severity = AlertSeverity.ERROR if moment_normalized > threshold * 1.3 else AlertSeverity.WARNING

                return self._create_alert(
                    severity=severity,
                    category=AlertCategory.DYNAMIC,
                    title="Momento Articular Elevado",
                    message=f"Momento de rodilla ({moment_normalized:.2f} Nm/kg) excede el umbral "
                           f"recomendado ({threshold:.2f} Nm/kg).",
                    value=moment_normalized,
                    threshold=threshold,
                    recommendation="Sobrecargar articular detectada. Reducir carga externa o rango de movimiento. "
                                  "Evaluar técnica de ejecución y fortalecimiento muscular progresivo."
                )

            return None

        except Exception as e:
            logger.error(f"Error verificando momento: {str(e)}")
            return None

    # ==================== ALERTAS DE FUERZA ====================

    def check_grf_alert(self, peak_grf: float, body_weight: float,
                       exercise_type: str = "squat") -> Optional[Alert]:
        """
        Verifica picos de fuerza de reacción al suelo.

        Args:
            peak_grf: Pico de GRF (N)
            body_weight: Peso corporal (N)
            exercise_type: Tipo de ejercicio ("squat", "jump", "walk")

        Returns:
            Alert si hay problema, None si está bien
        """
        try:
            grf_normalized = peak_grf / body_weight  # BW

            # Umbrales por tipo de ejercicio
            thresholds = {
                "squat": (0.8, 2.5),  # (mín, máx) en BW
                "jump": (1.5, 5.0),
                "walk": (0.8, 1.5)
            }

            min_threshold, max_threshold = thresholds.get(exercise_type, (0.5, 3.0))

            # GRF muy baja (falta de carga)
            if grf_normalized < min_threshold:
                return self._create_alert(
                    severity=AlertSeverity.WARNING,
                    category=AlertCategory.FORCE,
                    title="Carga Insuficiente",
                    message=f"GRF pico ({grf_normalized:.2f} BW) es menor que el mínimo esperado "
                           f"para {exercise_type} ({min_threshold:.2f} BW).",
                    value=grf_normalized,
                    threshold=min_threshold,
                    recommendation="Verificar ejecución completa del movimiento. "
                                  "Paciente puede estar evitando cargar completamente."
                )

            # GRF excesiva (impacto alto)
            elif grf_normalized > max_threshold:
                severity = AlertSeverity.CRITICAL if grf_normalized > max_threshold * 1.5 else AlertSeverity.ERROR

                return self._create_alert(
                    severity=severity,
                    category=AlertCategory.FORCE,
                    title="Impacto Excesivo",
                    message=f"GRF pico ({grf_normalized:.2f} BW) excede el máximo recomendado "
                           f"para {exercise_type} ({max_threshold:.2f} BW).",
                    value=grf_normalized,
                    threshold=max_threshold,
                    recommendation="Reducir intensidad o altura. Alto riesgo de lesión por impacto. "
                                  "Enseñar técnica de aterrizaje suave y absorción de fuerzas."
                )

            return None

        except Exception as e:
            logger.error(f"Error verificando GRF: {str(e)}")
            return None

    def check_loading_rate_alert(self, loading_rate: float,
                                 body_weight: float) -> Optional[Alert]:
        """
        Verifica tasa de carga (loading rate).

        Args:
            loading_rate: Tasa de carga (N/s)
            body_weight: Peso corporal (N)

        Returns:
            Alert si hay problema, None si está bien
        """
        try:
            loading_rate_normalized = loading_rate / body_weight  # BW/s

            # Umbral de tasa de carga rápida
            threshold = self.thresholds.get("max_loading_rate", 75)  # BW/s

            if loading_rate_normalized > threshold:
                severity = AlertSeverity.CRITICAL if loading_rate_normalized > threshold * 1.5 else AlertSeverity.ERROR

                return self._create_alert(
                    severity=severity,
                    category=AlertCategory.FORCE,
                    title="Tasa de Carga Elevada",
                    message=f"Tasa de carga ({loading_rate_normalized:.1f} BW/s) excede el umbral "
                           f"seguro ({threshold:.1f} BW/s).",
                    value=loading_rate_normalized,
                    threshold=threshold,
                    recommendation="RIESGO ALTO de lesión por impacto. Enseñar técnica de absorción gradual. "
                                  "Considerar superficie más blanda o reducir altura/velocidad."
                )

            return None

        except Exception as e:
            logger.error(f"Error verificando loading rate: {str(e)}")
            return None

    # ==================== ALERTAS DE SIMETRÍA ====================

    def check_symmetry_alert(self, symmetry_index: float) -> Optional[Alert]:
        """
        Verifica asimetrías bilaterales.

        Args:
            symmetry_index: Índice de simetría (%)

        Returns:
            Alert si hay problema, None si está bien
        """
        try:
            # Umbrales de asimetría
            moderate_threshold = self.thresholds.get("moderate_asymmetry", 10)  # %
            severe_threshold = self.thresholds.get("severe_asymmetry", 20)  # %

            if symmetry_index > severe_threshold:
                return self._create_alert(
                    severity=AlertSeverity.ERROR,
                    category=AlertCategory.SYMMETRY,
                    title="Asimetría Severa",
                    message=f"Asimetría bilateral del {symmetry_index:.1f}% excede el umbral crítico "
                           f"({severe_threshold:.1f}%).",
                    value=symmetry_index,
                    threshold=severe_threshold,
                    recommendation="ASIMETRÍA CRÍTICA detectada. Evaluar compensaciones, debilidad muscular "
                                  "o dolor unilateral. Priorizar trabajo de equilibrio bilateral."
                )

            elif symmetry_index > moderate_threshold:
                return self._create_alert(
                    severity=AlertSeverity.WARNING,
                    category=AlertCategory.SYMMETRY,
                    title="Asimetría Moderada",
                    message=f"Asimetría bilateral del {symmetry_index:.1f}% está por encima del umbral "
                           f"aceptable ({moderate_threshold:.1f}%).",
                    value=symmetry_index,
                    threshold=moderate_threshold,
                    recommendation="Monitorear asimetría. Considerar ejercicios unilaterales para fortalecer "
                                  "extremidad más débil."
                )

            return None

        except Exception as e:
            logger.error(f"Error verificando simetría: {str(e)}")
            return None

    # ==================== ALERTAS DE VALIDACIÓN ====================

    def check_data_quality_alert(self, signal: np.ndarray,
                                 signal_name: str = "señal") -> Optional[Alert]:
        """
        Verifica calidad de datos (ruido, gaps, outliers).

        Args:
            signal: Señal a verificar
            signal_name: Nombre de la señal

        Returns:
            Alert si hay problema, None si está bien
        """
        try:
            # Verificar NaN o infinitos
            if np.any(np.isnan(signal)) or np.any(np.isinf(signal)):
                return self._create_alert(
                    severity=AlertSeverity.ERROR,
                    category=AlertCategory.TECHNICAL,
                    title="Datos Inválidos",
                    message=f"La {signal_name} contiene valores NaN o infinitos.",
                    recommendation="Verificar conexión de sensores y calibración. "
                                  "Reiniciar captura si el problema persiste."
                )

            # Verificar señal constante (sensor desconectado)
            if np.std(signal) < 1e-6:
                return self._create_alert(
                    severity=AlertSeverity.ERROR,
                    category=AlertCategory.TECHNICAL,
                    title="Señal Constante",
                    message=f"La {signal_name} no presenta variación (std < 1e-6).",
                    recommendation="Sensor puede estar desconectado o congelado. "
                                  "Verificar conexión y reiniciar dispositivo."
                )

            # Verificar outliers extremos (> 5 desviaciones estándar)
            z_scores = np.abs((signal - np.mean(signal)) / np.std(signal))
            outlier_count = np.sum(z_scores > 5)
            outlier_percent = (outlier_count / len(signal)) * 100

            if outlier_percent > 5:  # > 5% de outliers
                return self._create_alert(
                    severity=AlertSeverity.WARNING,
                    category=AlertCategory.TECHNICAL,
                    title="Ruido Excesivo",
                    message=f"La {signal_name} contiene {outlier_percent:.1f}% de outliers extremos.",
                    recommendation="Calidad de señal comprometida. Verificar interferencias, "
                                  "calibración y fijación de sensores."
                )

            return None

        except Exception as e:
            logger.error(f"Error verificando calidad de datos: {str(e)}")
            return None

    def check_sync_quality_alert(self, sync_quality: float) -> Optional[Alert]:
        """
        Verifica calidad de sincronización entre dispositivos.

        Args:
            sync_quality: Calidad de sincronización (0-1)

        Returns:
            Alert si hay problema, None si está bien
        """
        try:
            if sync_quality < 0.7:
                return self._create_alert(
                    severity=AlertSeverity.ERROR,
                    category=AlertCategory.TECHNICAL,
                    title="Sincronización Pobre",
                    message=f"Calidad de sincronización ({sync_quality:.1%}) es insuficiente.",
                    value=sync_quality,
                    threshold=0.7,
                    recommendation="Los datos de IMU y plataforma de fuerza pueden no estar correctamente "
                                  "sincronizados. Verificar marcadores de tiempo y repetir captura."
                )

            elif sync_quality < 0.85:
                return self._create_alert(
                    severity=AlertSeverity.WARNING,
                    category=AlertCategory.TECHNICAL,
                    title="Sincronización Subóptima",
                    message=f"Calidad de sincronización ({sync_quality:.1%}) es aceptable pero no ideal.",
                    value=sync_quality,
                    threshold=0.85,
                    recommendation="Considerar repetir captura para mejorar precisión temporal."
                )

            return None

        except Exception as e:
            logger.error(f"Error verificando sincronización: {str(e)}")
            return None

    # ==================== GESTIÓN DE ALERTAS ====================

    def _create_alert(self,
                     severity: AlertSeverity,
                     category: AlertCategory,
                     title: str,
                     message: str,
                     value: Optional[float] = None,
                     threshold: Optional[float] = None,
                     recommendation: Optional[str] = None) -> Alert:
        """
        Crea y registra una nueva alerta.

        Args:
            severity: Nivel de severidad
            category: Categoría
            title: Título
            message: Mensaje
            value: Valor que generó la alerta
            threshold: Umbral excedido
            recommendation: Recomendación

        Returns:
            Alert creada
        """
        alert = Alert(
            id=f"alert_{self.alert_counter:04d}",
            timestamp=datetime.now(),
            severity=severity,
            category=category,
            title=title,
            message=message,
            value=value,
            threshold=threshold,
            recommendation=recommendation
        )

        self.alert_counter += 1
        self.alerts.append(alert)

        # Llamar callback si existe
        if self.callback:
            try:
                self.callback(alert)
            except Exception as e:
                logger.error(f"Error en callback de alerta: {str(e)}")

        logger.info(f"Alerta generada [{severity.value}]: {title}")

        return alert

    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """
        Obtiene alertas activas (no reconocidas).

        Args:
            severity: Filtrar por severidad (opcional)

        Returns:
            Lista de alertas activas
        """
        active = [a for a in self.alerts if not a.acknowledged]

        if severity:
            active = [a for a in active if a.severity == severity]

        return active

    def acknowledge_alert(self, alert_id: str):
        """
        Marca una alerta como reconocida.

        Args:
            alert_id: ID de la alerta
        """
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                logger.info(f"Alerta {alert_id} reconocida")
                break

    def clear_alerts(self):
        """Limpia todas las alertas."""
        self.alerts.clear()
        logger.info("Todas las alertas eliminadas")

    def get_alert_summary(self) -> Dict[str, int]:
        """
        Obtiene resumen de alertas por severidad.

        Returns:
            Diccionario con conteo por severidad
        """
        active = self.get_active_alerts()

        return {
            'critical': sum(1 for a in active if a.severity == AlertSeverity.CRITICAL),
            'error': sum(1 for a in active if a.severity == AlertSeverity.ERROR),
            'warning': sum(1 for a in active if a.severity == AlertSeverity.WARNING),
            'info': sum(1 for a in active if a.severity == AlertSeverity.INFO),
            'total': len(active)
        }


# Función de conveniencia
def create_alert_system(callback: Optional[Callable] = None) -> AlertSystem:
    """Crea un sistema de alertas (función de conveniencia)."""
    return AlertSystem(callback=callback)
