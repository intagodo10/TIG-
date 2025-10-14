"""
Calculadora de métricas biomecánicas.

Calcula métricas cinemáticas, dinámicas y de validación para análisis
de movimiento de rodilla.
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from config.settings import METRICS_CONFIG, PHYSICAL_CONSTANTS, REFERENCE_VALUES
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class KinematicMetrics:
    """
    Métricas cinemáticas.

    Attributes:
        rom: Rango de movimiento (grados)
        peak_flexion: Flexión máxima (grados)
        peak_extension: Extensión máxima (grados)
        mean_angle: Ángulo promedio (grados)
        angular_velocity_peak: Velocidad angular máxima (deg/s)
        angular_acceleration_peak: Aceleración angular máxima (deg/s²)
    """
    rom: float
    peak_flexion: float
    peak_extension: float
    mean_angle: float
    angular_velocity_peak: float
    angular_acceleration_peak: float


@dataclass
class DynamicMetrics:
    """
    Métricas dinámicas.

    Attributes:
        peak_moment: Momento máximo (Nm/kg)
        mean_moment: Momento promedio (Nm/kg)
        peak_power: Potencia máxima (W/kg)
        work: Trabajo total (J/kg)
        moment_impulse: Impulso del momento (Nm·s/kg)
    """
    peak_moment: float
    mean_moment: float
    peak_power: float
    work: float
    moment_impulse: float


@dataclass
class ForceMetrics:
    """
    Métricas de fuerza.

    Attributes:
        peak_grf: Pico de GRF (BW - Body Weights)
        mean_grf: GRF promedio (BW)
        loading_rate: Tasa de carga (BW/s)
        impulse: Impulso (N·s)
        contact_time: Tiempo de contacto (s)
        time_to_peak: Tiempo al pico (s)
    """
    peak_grf: float
    mean_grf: float
    loading_rate: float
    impulse: float
    contact_time: float
    time_to_peak: float


@dataclass
class ValidationMetrics:
    """
    Métricas de validación estadística.

    Attributes:
        rmse: Root Mean Square Error
        mae: Mean Absolute Error
        icc: Intraclass Correlation Coefficient
        r_squared: Coeficiente de determinación
        cv: Coefficient of Variation (%)
    """
    rmse: float
    mae: float
    icc: float
    r_squared: float
    cv: float


@dataclass
class SymmetryMetrics:
    """
    Métricas de simetría entre extremidades.

    Attributes:
        symmetry_index: Índice de simetría (%)
        asymmetry_ratio: Ratio de asimetría
        difference: Diferencia absoluta
        bilateral_deficit: Déficit bilateral (%)
    """
    symmetry_index: float
    asymmetry_ratio: float
    difference: float
    bilateral_deficit: float


class MetricsCalculator:
    """
    Calculadora de métricas biomecánicas.

    Calcula métricas cinemáticas, dinámicas, de fuerza y validación
    para análisis de movimiento y evaluación de rodilla.
    """

    def __init__(self):
        """Inicializa la calculadora de métricas."""
        self.gravity = PHYSICAL_CONSTANTS["gravity"]
        self.reference_values = REFERENCE_VALUES

        logger.info("MetricsCalculator inicializado")

    # ==================== MÉTRICAS CINEMÁTICAS ====================

    def calculate_kinematic_metrics(self,
                                    time: np.ndarray,
                                    angle: np.ndarray) -> KinematicMetrics:
        """
        Calcula métricas cinemáticas a partir de ángulos articulares.

        Args:
            time: Vector de tiempo (s)
            angle: Ángulo articular (grados)

        Returns:
            KinematicMetrics con las métricas calculadas
        """
        try:
            # ROM (Range of Motion)
            rom = np.max(angle) - np.min(angle)

            # Picos
            peak_flexion = np.max(angle)
            peak_extension = np.min(angle)

            # Promedio
            mean_angle = np.mean(angle)

            # Velocidad angular (derivada numérica)
            dt = np.mean(np.diff(time))
            angular_velocity = np.gradient(angle, dt)
            angular_velocity_peak = np.max(np.abs(angular_velocity))

            # Aceleración angular (segunda derivada)
            angular_acceleration = np.gradient(angular_velocity, dt)
            angular_acceleration_peak = np.max(np.abs(angular_acceleration))

            logger.debug(f"Métricas cinemáticas calculadas: ROM={rom:.1f}°, "
                        f"Flexión máx={peak_flexion:.1f}°")

            return KinematicMetrics(
                rom=rom,
                peak_flexion=peak_flexion,
                peak_extension=peak_extension,
                mean_angle=mean_angle,
                angular_velocity_peak=angular_velocity_peak,
                angular_acceleration_peak=angular_acceleration_peak
            )

        except Exception as e:
            logger.error(f"Error calculando métricas cinemáticas: {str(e)}")
            return self._empty_kinematic_metrics()

    def calculate_rom_multiple_cycles(self,
                                     angles: np.ndarray,
                                     cycles: List[Tuple[int, int]]) -> Dict[str, float]:
        """
        Calcula ROM para múltiples ciclos y estadísticas.

        Args:
            angles: Array de ángulos
            cycles: Lista de tuplas (inicio, fin) de cada ciclo

        Returns:
            Diccionario con ROM promedio, std, min, max
        """
        roms = []

        for start, end in cycles:
            cycle_angles = angles[start:end]
            rom = np.max(cycle_angles) - np.min(cycle_angles)
            roms.append(rom)

        return {
            'mean_rom': np.mean(roms),
            'std_rom': np.std(roms),
            'min_rom': np.min(roms),
            'max_rom': np.max(roms),
            'cv_rom': (np.std(roms) / np.mean(roms)) * 100  # Coeficiente de variación
        }

    # ==================== MÉTRICAS DINÁMICAS ====================

    def calculate_dynamic_metrics(self,
                                  time: np.ndarray,
                                  moment: np.ndarray,
                                  angular_velocity: np.ndarray,
                                  body_mass: float) -> DynamicMetrics:
        """
        Calcula métricas dinámicas (momentos, potencia, trabajo).

        Args:
            time: Vector de tiempo (s)
            moment: Momento articular (Nm)
            angular_velocity: Velocidad angular (rad/s)
            body_mass: Masa corporal (kg)

        Returns:
            DynamicMetrics con las métricas calculadas
        """
        try:
            # Normalizar por masa corporal
            moment_normalized = moment / body_mass

            # Pico y promedio de momento
            peak_moment = np.max(np.abs(moment_normalized))
            mean_moment = np.mean(np.abs(moment_normalized))

            # Potencia (P = M * ω)
            power = moment * angular_velocity  # W
            power_normalized = power / body_mass  # W/kg
            peak_power = np.max(np.abs(power_normalized))

            # Trabajo (integral de potencia)
            work = np.trapz(np.abs(power), time)  # J
            work_normalized = work / body_mass  # J/kg

            # Impulso del momento
            moment_impulse = np.trapz(np.abs(moment_normalized), time)  # Nm·s/kg

            logger.debug(f"Métricas dinámicas calculadas: Momento máx={peak_moment:.2f} Nm/kg, "
                        f"Potencia máx={peak_power:.1f} W/kg")

            return DynamicMetrics(
                peak_moment=peak_moment,
                mean_moment=mean_moment,
                peak_power=peak_power,
                work=work_normalized,
                moment_impulse=moment_impulse
            )

        except Exception as e:
            logger.error(f"Error calculando métricas dinámicas: {str(e)}")
            return self._empty_dynamic_metrics()

    # ==================== MÉTRICAS DE FUERZA ====================

    def calculate_force_metrics(self,
                                time: np.ndarray,
                                grf: np.ndarray,
                                body_weight: float,
                                contact_start: int,
                                contact_end: int) -> ForceMetrics:
        """
        Calcula métricas de fuerza de reacción al suelo (GRF).

        Args:
            time: Vector de tiempo (s)
            grf: Fuerza vertical (N)
            body_weight: Peso corporal (N)
            contact_start: Índice de inicio de contacto
            contact_end: Índice de fin de contacto

        Returns:
            ForceMetrics con las métricas calculadas
        """
        try:
            # Extraer segmento de contacto
            time_contact = time[contact_start:contact_end+1]
            grf_contact = grf[contact_start:contact_end+1]

            # Normalizar por peso corporal
            grf_normalized = grf_contact / body_weight  # BW

            # Pico de GRF
            peak_grf = np.max(grf_normalized)

            # GRF promedio
            mean_grf = np.mean(grf_normalized)

            # Tiempo de contacto
            contact_time = time_contact[-1] - time_contact[0]

            # Tiempo al pico
            peak_idx = np.argmax(grf_contact)
            time_to_peak = time_contact[peak_idx] - time_contact[0]

            # Tasa de carga (loading rate)
            # Desde inicio hasta pico
            if peak_idx > 0:
                loading_rate = (grf_normalized[peak_idx] - grf_normalized[0]) / time_to_peak
            else:
                loading_rate = 0.0

            # Impulso (integral de fuerza)
            impulse = np.trapz(grf_contact, time_contact)  # N·s

            logger.debug(f"Métricas de fuerza calculadas: GRF máx={peak_grf:.2f} BW, "
                        f"Tasa carga={loading_rate:.1f} BW/s")

            return ForceMetrics(
                peak_grf=peak_grf,
                mean_grf=mean_grf,
                loading_rate=loading_rate,
                impulse=impulse,
                contact_time=contact_time,
                time_to_peak=time_to_peak
            )

        except Exception as e:
            logger.error(f"Error calculando métricas de fuerza: {str(e)}")
            return self._empty_force_metrics()

    def calculate_grf_peaks_multiple_contacts(self,
                                              grf: np.ndarray,
                                              contacts: List[Tuple[int, int]],
                                              body_weight: float) -> Dict[str, float]:
        """
        Calcula picos de GRF para múltiples contactos.

        Args:
            grf: Fuerza vertical (N)
            contacts: Lista de tuplas (inicio, fin) de contactos
            body_weight: Peso corporal (N)

        Returns:
            Diccionario con estadísticas de picos
        """
        peaks = []

        for start, end in contacts:
            grf_segment = grf[start:end]
            peak = np.max(grf_segment) / body_weight
            peaks.append(peak)

        return {
            'mean_peak': np.mean(peaks),
            'std_peak': np.std(peaks),
            'min_peak': np.min(peaks),
            'max_peak': np.max(peaks),
            'cv_peak': (np.std(peaks) / np.mean(peaks)) * 100
        }

    # ==================== MÉTRICAS DE VALIDACIÓN ====================

    def calculate_validation_metrics(self,
                                     measured: np.ndarray,
                                     reference: np.ndarray) -> ValidationMetrics:
        """
        Calcula métricas de validación entre datos medidos y referencia.

        Args:
            measured: Datos medidos
            reference: Datos de referencia (gold standard)

        Returns:
            ValidationMetrics con las métricas calculadas
        """
        try:
            # Asegurar misma longitud
            if len(measured) != len(reference):
                logger.warning("Longitudes diferentes, truncando al mínimo")
                min_len = min(len(measured), len(reference))
                measured = measured[:min_len]
                reference = reference[:min_len]

            # RMSE (Root Mean Square Error)
            rmse = np.sqrt(np.mean((measured - reference) ** 2))

            # MAE (Mean Absolute Error)
            mae = np.mean(np.abs(measured - reference))

            # ICC (Intraclass Correlation Coefficient)
            icc = self._calculate_icc(measured, reference)

            # R² (Coeficiente de determinación)
            correlation = np.corrcoef(measured, reference)[0, 1]
            r_squared = correlation ** 2

            # CV (Coefficient of Variation)
            mean_val = np.mean(measured)
            std_val = np.std(measured)
            cv = (std_val / mean_val) * 100 if mean_val != 0 else 0.0

            logger.debug(f"Métricas de validación calculadas: RMSE={rmse:.3f}, ICC={icc:.3f}")

            return ValidationMetrics(
                rmse=rmse,
                mae=mae,
                icc=icc,
                r_squared=r_squared,
                cv=cv
            )

        except Exception as e:
            logger.error(f"Error calculando métricas de validación: {str(e)}")
            return self._empty_validation_metrics()

    def _calculate_icc(self, x: np.ndarray, y: np.ndarray) -> float:
        """
        Calcula ICC (2,1) - Intraclass Correlation Coefficient.

        Args:
            x: Primera serie de mediciones
            y: Segunda serie de mediciones

        Returns:
            ICC value (0-1)
        """
        try:
            # ICC(2,1) - Two-way random effects, absolute agreement
            n = len(x)

            # Crear matriz de datos (n x 2)
            data = np.column_stack([x, y])

            # Promedios
            grand_mean = np.mean(data)
            subject_means = np.mean(data, axis=1)
            rater_means = np.mean(data, axis=0)

            # Sumas de cuadrados
            ss_total = np.sum((data - grand_mean) ** 2)
            ss_rows = 2 * np.sum((subject_means - grand_mean) ** 2)
            ss_cols = n * np.sum((rater_means - grand_mean) ** 2)
            ss_error = ss_total - ss_rows - ss_cols

            # Medias cuadradas
            ms_rows = ss_rows / (n - 1)
            ms_error = ss_error / ((n - 1) * (2 - 1))

            # ICC(2,1)
            icc = (ms_rows - ms_error) / (ms_rows + ms_error)

            return max(0.0, min(1.0, icc))  # Limitar a [0, 1]

        except Exception as e:
            logger.error(f"Error calculando ICC: {str(e)}")
            return 0.0

    # ==================== MÉTRICAS DE SIMETRÍA ====================

    def calculate_symmetry_metrics(self,
                                   right_limb: np.ndarray,
                                   left_limb: np.ndarray) -> SymmetryMetrics:
        """
        Calcula métricas de simetría bilateral.

        Args:
            right_limb: Datos de extremidad derecha
            left_limb: Datos de extremidad izquierda

        Returns:
            SymmetryMetrics con las métricas calculadas
        """
        try:
            # Promedios
            right_mean = np.mean(right_limb)
            left_mean = np.mean(left_limb)

            # Índice de simetría (%)
            # SI = (|R - L| / 0.5*(R + L)) * 100
            symmetry_index = (np.abs(right_mean - left_mean) /
                             (0.5 * (right_mean + left_mean))) * 100

            # Ratio de asimetría
            asymmetry_ratio = right_mean / left_mean if left_mean != 0 else 1.0

            # Diferencia absoluta
            difference = np.abs(right_mean - left_mean)

            # Déficit bilateral (%)
            # BD = ((R + L) / (2 * max(R, L)) - 1) * 100
            max_limb = max(right_mean, left_mean)
            bilateral_deficit = ((right_mean + left_mean) / (2 * max_limb) - 1) * 100

            logger.debug(f"Métricas de simetría calculadas: SI={symmetry_index:.1f}%, "
                        f"Ratio={asymmetry_ratio:.2f}")

            return SymmetryMetrics(
                symmetry_index=symmetry_index,
                asymmetry_ratio=asymmetry_ratio,
                difference=difference,
                bilateral_deficit=bilateral_deficit
            )

        except Exception as e:
            logger.error(f"Error calculando métricas de simetría: {str(e)}")
            return self._empty_symmetry_metrics()

    # ==================== ANÁLISIS ESTADÍSTICO ====================

    def calculate_repetition_statistics(self,
                                        values: List[float]) -> Dict[str, float]:
        """
        Calcula estadísticas descriptivas de repeticiones.

        Args:
            values: Lista de valores (ej: ROM de cada repetición)

        Returns:
            Diccionario con estadísticas
        """
        if not values or len(values) == 0:
            return {
                'mean': 0.0,
                'std': 0.0,
                'min': 0.0,
                'max': 0.0,
                'median': 0.0,
                'cv': 0.0,
                'count': 0
            }

        arr = np.array(values)
        mean_val = np.mean(arr)

        return {
            'mean': mean_val,
            'std': np.std(arr),
            'min': np.min(arr),
            'max': np.max(arr),
            'median': np.median(arr),
            'cv': (np.std(arr) / mean_val * 100) if mean_val != 0 else 0.0,
            'count': len(values)
        }

    def perform_normality_test(self, data: np.ndarray) -> Tuple[bool, float]:
        """
        Realiza test de normalidad (Shapiro-Wilk).

        Args:
            data: Array de datos

        Returns:
            Tupla (es_normal, p_value)
        """
        try:
            if len(data) < 3:
                logger.warning("Datos insuficientes para test de normalidad")
                return False, 1.0

            statistic, p_value = stats.shapiro(data)
            is_normal = p_value > 0.05

            logger.debug(f"Test de normalidad: p={p_value:.4f}, normal={is_normal}")

            return is_normal, p_value

        except Exception as e:
            logger.error(f"Error en test de normalidad: {str(e)}")
            return False, 1.0

    # ==================== COMPARACIÓN CON REFERENCIA ====================

    def compare_with_reference(self,
                               metric_name: str,
                               value: float,
                               reference_range: Tuple[float, float]) -> Dict[str, any]:
        """
        Compara métrica con valores de referencia.

        Args:
            metric_name: Nombre de la métrica
            value: Valor medido
            reference_range: Tupla (min, max) del rango de referencia

        Returns:
            Diccionario con análisis de comparación
        """
        ref_min, ref_max = reference_range
        ref_mean = (ref_min + ref_max) / 2

        # Determinar estado
        if ref_min <= value <= ref_max:
            status = "normal"
            deviation = 0.0
        elif value < ref_min:
            status = "below"
            deviation = ((ref_min - value) / ref_mean) * 100
        else:  # value > ref_max
            status = "above"
            deviation = ((value - ref_max) / ref_mean) * 100

        return {
            'metric': metric_name,
            'value': value,
            'reference_min': ref_min,
            'reference_max': ref_max,
            'reference_mean': ref_mean,
            'status': status,
            'deviation_percent': deviation
        }

    # ==================== MÉTRICAS COMPUESTAS ====================

    def calculate_functional_score(self,
                                   rom: float,
                                   symmetry_index: float,
                                   peak_grf: float) -> float:
        """
        Calcula puntuación funcional compuesta (0-100).

        Args:
            rom: Rango de movimiento (grados)
            symmetry_index: Índice de simetría (%)
            peak_grf: Pico de GRF (BW)

        Returns:
            Puntuación funcional (0-100)
        """
        try:
            # Componente de ROM (40 puntos)
            # ROM normal rodilla: 0-135°
            rom_score = min((rom / 135) * 40, 40)

            # Componente de simetría (30 puntos)
            # SI perfecto = 0%, SI > 15% = 0 puntos
            symmetry_score = max(30 - (symmetry_index / 15) * 30, 0)

            # Componente de GRF (30 puntos)
            # GRF normal = 1.5-3.0 BW
            if 1.5 <= peak_grf <= 3.0:
                grf_score = 30
            elif peak_grf < 1.5:
                grf_score = (peak_grf / 1.5) * 30
            else:
                grf_score = max(30 - ((peak_grf - 3.0) / 3.0) * 30, 0)

            total_score = rom_score + symmetry_score + grf_score

            logger.debug(f"Puntuación funcional calculada: {total_score:.1f}/100")

            return total_score

        except Exception as e:
            logger.error(f"Error calculando puntuación funcional: {str(e)}")
            return 0.0

    # ==================== MÉTODOS AUXILIARES ====================

    def _empty_kinematic_metrics(self) -> KinematicMetrics:
        """Retorna métricas cinemáticas vacías."""
        return KinematicMetrics(
            rom=0.0,
            peak_flexion=0.0,
            peak_extension=0.0,
            mean_angle=0.0,
            angular_velocity_peak=0.0,
            angular_acceleration_peak=0.0
        )

    def _empty_dynamic_metrics(self) -> DynamicMetrics:
        """Retorna métricas dinámicas vacías."""
        return DynamicMetrics(
            peak_moment=0.0,
            mean_moment=0.0,
            peak_power=0.0,
            work=0.0,
            moment_impulse=0.0
        )

    def _empty_force_metrics(self) -> ForceMetrics:
        """Retorna métricas de fuerza vacías."""
        return ForceMetrics(
            peak_grf=0.0,
            mean_grf=0.0,
            loading_rate=0.0,
            impulse=0.0,
            contact_time=0.0,
            time_to_peak=0.0
        )

    def _empty_validation_metrics(self) -> ValidationMetrics:
        """Retorna métricas de validación vacías."""
        return ValidationMetrics(
            rmse=0.0,
            mae=0.0,
            icc=0.0,
            r_squared=0.0,
            cv=0.0
        )

    def _empty_symmetry_metrics(self) -> SymmetryMetrics:
        """Retorna métricas de simetría vacías."""
        return SymmetryMetrics(
            symmetry_index=0.0,
            asymmetry_ratio=1.0,
            difference=0.0,
            bilateral_deficit=0.0
        )


# Funciones de conveniencia
def calculate_rom(angles: np.ndarray) -> float:
    """Calcula ROM (función de conveniencia)."""
    return np.max(angles) - np.min(angles)


def calculate_peak_grf(grf: np.ndarray, body_weight: float) -> float:
    """Calcula pico de GRF normalizado (función de conveniencia)."""
    return np.max(grf) / body_weight


def calculate_icc_simple(x: np.ndarray, y: np.ndarray) -> float:
    """Calcula ICC (función de conveniencia)."""
    calculator = MetricsCalculator()
    return calculator._calculate_icc(x, y)
