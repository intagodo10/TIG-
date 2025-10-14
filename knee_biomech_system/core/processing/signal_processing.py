"""
Procesamiento de señales biomecánicas.

Filtrado, detección de eventos y preprocesamiento de señales
de sensores y plataforma de fuerza.
"""

import numpy as np
from scipy import signal
from typing import Dict, Tuple, List, Optional

from config.settings import SIGNAL_PROCESSING, PHYSICAL_CONSTANTS
from utils.logger import get_logger

logger = get_logger(__name__)


class SignalProcessor:
    """
    Procesador de señales biomecánicas.

    Aplica filtros, detecta eventos y preprocesa señales para análisis.
    """

    def __init__(self):
        """Inicializa el procesador de señales."""
        self.filter_type = SIGNAL_PROCESSING["filter_type"]
        self.filter_order = SIGNAL_PROCESSING["filter_order"]
        self.cutoff_frequencies = SIGNAL_PROCESSING["cutoff_frequencies"]
        self.gravity = PHYSICAL_CONSTANTS["gravity"]

        logger.info("SignalProcessor inicializado")

    def filter_butterworth(self,
                          data: np.ndarray,
                          cutoff: float,
                          fs: float,
                          order: Optional[int] = None,
                          btype: str = 'low') -> np.ndarray:
        """
        Aplica filtro Butterworth a los datos.

        Args:
            data: Señal a filtrar
            cutoff: Frecuencia de corte (Hz)
            fs: Frecuencia de muestreo (Hz)
            order: Orden del filtro (default: de config)
            btype: Tipo de filtro ('low', 'high', 'band')

        Returns:
            Señal filtrada
        """
        try:
            if order is None:
                order = self.filter_order

            # Normalizar frecuencia de corte
            nyquist = fs / 2
            normalized_cutoff = cutoff / nyquist

            if normalized_cutoff >= 1.0:
                logger.warning(f"Frecuencia de corte ({cutoff} Hz) >= Nyquist ({nyquist} Hz). Retornando señal original.")
                return data

            # Diseñar filtro
            sos = signal.butter(order, normalized_cutoff, btype=btype, output='sos')

            # Aplicar filtro (filtfilt = forward-backward, sin desfase)
            filtered = signal.sosfiltfilt(sos, data)

            logger.debug(f"Filtro Butterworth aplicado: {btype}pass @ {cutoff} Hz, orden {order}")

            return filtered

        except Exception as e:
            logger.error(f"Error aplicando filtro: {str(e)}")
            return data  # Retornar señal original si falla

    def filter_imu_acceleration(self, acceleration: np.ndarray, fs: float = 60) -> np.ndarray:
        """
        Filtra datos de aceleración IMU.

        Args:
            acceleration: Datos de aceleración [N x 3] (x, y, z)
            fs: Frecuencia de muestreo (Hz)

        Returns:
            Aceleración filtrada
        """
        cutoff = self.cutoff_frequencies['imu_acc']

        if acceleration.ndim == 1:
            return self.filter_butterworth(acceleration, cutoff, fs)
        else:
            # Filtrar cada componente
            filtered = np.zeros_like(acceleration)
            for i in range(acceleration.shape[1]):
                filtered[:, i] = self.filter_butterworth(acceleration[:, i], cutoff, fs)
            return filtered

    def filter_imu_gyro(self, angular_velocity: np.ndarray, fs: float = 60) -> np.ndarray:
        """
        Filtra datos de velocidad angular IMU.

        Args:
            angular_velocity: Velocidad angular [N x 3] (x, y, z)
            fs: Frecuencia de muestreo (Hz)

        Returns:
            Velocidad angular filtrada
        """
        cutoff = self.cutoff_frequencies['imu_gyro']

        if angular_velocity.ndim == 1:
            return self.filter_butterworth(angular_velocity, cutoff, fs)
        else:
            filtered = np.zeros_like(angular_velocity)
            for i in range(angular_velocity.shape[1]):
                filtered[:, i] = self.filter_butterworth(angular_velocity[:, i], cutoff, fs)
            return filtered

    def filter_force(self, force: np.ndarray, fs: float = 1000) -> np.ndarray:
        """
        Filtra datos de fuerza de plataforma.

        Args:
            force: Datos de fuerza [N] o [N x 3]
            fs: Frecuencia de muestreo (Hz)

        Returns:
            Fuerza filtrada
        """
        cutoff = self.cutoff_frequencies['force']

        if force.ndim == 1:
            return self.filter_butterworth(force, cutoff, fs)
        else:
            filtered = np.zeros_like(force)
            for i in range(force.shape[1]):
                filtered[:, i] = self.filter_butterworth(force[:, i], cutoff, fs)
            return filtered

    def remove_gravity(self, acceleration: np.ndarray, axis: int = 2) -> np.ndarray:
        """
        Remueve la componente gravitacional de la aceleración.

        Args:
            acceleration: Aceleración [N x 3]
            axis: Eje vertical (default: 2 = Z)

        Returns:
            Aceleración sin gravedad
        """
        corrected = acceleration.copy()

        if acceleration.ndim == 1:
            # Vector 1D
            corrected = corrected - self.gravity
        else:
            # Vector multidimensional
            corrected[:, axis] = corrected[:, axis] - self.gravity

        logger.debug("Gravedad removida de aceleración")
        return corrected

    def detect_events_threshold(self,
                                signal_data: np.ndarray,
                                threshold: float,
                                min_duration: Optional[float] = None,
                                fs: Optional[float] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detecta eventos mediante umbral.

        Args:
            signal_data: Señal a analizar
            threshold: Umbral de detección
            min_duration: Duración mínima del evento (segundos)
            fs: Frecuencia de muestreo (Hz)

        Returns:
            Tuple (índices_inicio, índices_fin)
        """
        # Detectar cruces de umbral
        above_threshold = signal_data > threshold
        crossings = np.diff(above_threshold.astype(int))

        # Índices de inicio (cruce hacia arriba)
        start_indices = np.where(crossings == 1)[0] + 1

        # Índices de fin (cruce hacia abajo)
        end_indices = np.where(crossings == -1)[0] + 1

        # Asegurar que cada inicio tenga un fin
        if len(start_indices) > 0 and len(end_indices) > 0:
            if start_indices[0] > end_indices[0]:
                end_indices = end_indices[1:]
            if len(start_indices) > len(end_indices):
                start_indices = start_indices[:len(end_indices)]
            elif len(end_indices) > len(start_indices):
                end_indices = end_indices[:len(start_indices)]

        # Filtrar por duración mínima si se especifica
        if min_duration is not None and fs is not None:
            min_samples = int(min_duration * fs)
            valid_events = (end_indices - start_indices) >= min_samples
            start_indices = start_indices[valid_events]
            end_indices = end_indices[valid_events]

        logger.debug(f"Eventos detectados: {len(start_indices)}")

        return start_indices, end_indices

    def detect_grf_contacts(self,
                           fz: np.ndarray,
                           threshold: float = 20.0,
                           fs: float = 1000,
                           min_contact_time: float = 0.1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detecta contactos en fuerza vertical de reacción al suelo.

        Args:
            fz: Fuerza vertical (N)
            threshold: Umbral de detección (N)
            fs: Frecuencia de muestreo (Hz)
            min_contact_time: Tiempo mínimo de contacto (segundos)

        Returns:
            Tuple (contactos, despegues) - índices
        """
        contacts, liftoffs = self.detect_events_threshold(
            fz, threshold, min_duration=min_contact_time, fs=fs
        )

        logger.info(f"Contactos detectados: {len(contacts)}, Despegues: {len(liftoffs)}")

        return contacts, liftoffs

    def calculate_velocity(self,
                          acceleration: np.ndarray,
                          dt: float,
                          initial_velocity: float = 0.0) -> np.ndarray:
        """
        Calcula velocidad mediante integración de aceleración.

        Args:
            acceleration: Aceleración (m/s²)
            dt: Paso de tiempo (segundos)
            initial_velocity: Velocidad inicial (m/s)

        Returns:
            Velocidad (m/s)
        """
        # Integración trapezoidal
        velocity = np.zeros_like(acceleration)
        velocity[0] = initial_velocity

        for i in range(1, len(acceleration)):
            velocity[i] = velocity[i-1] + 0.5 * (acceleration[i] + acceleration[i-1]) * dt

        return velocity

    def calculate_displacement(self,
                              velocity: np.ndarray,
                              dt: float,
                              initial_position: float = 0.0) -> np.ndarray:
        """
        Calcula desplazamiento mediante integración de velocidad.

        Args:
            velocity: Velocidad (m/s)
            dt: Paso de tiempo (segundos)
            initial_position: Posición inicial (m)

        Returns:
            Desplazamiento (m)
        """
        # Integración trapezoidal
        position = np.zeros_like(velocity)
        position[0] = initial_position

        for i in range(1, len(velocity)):
            position[i] = position[i-1] + 0.5 * (velocity[i] + velocity[i-1]) * dt

        return position

    def calculate_jump_height(self,
                             time: np.ndarray,
                             fz: np.ndarray,
                             body_mass: float,
                             contact_idx: int,
                             liftoff_idx: int) -> float:
        """
        Calcula altura de salto usando método impulso-momentum.

        Args:
            time: Vector de tiempo (s)
            fz: Fuerza vertical (N)
            body_mass: Masa corporal (kg)
            contact_idx: Índice de contacto inicial
            liftoff_idx: Índice de despegue

        Returns:
            Altura de salto (m)
        """
        try:
            # Obtener segmento de propulsión
            time_segment = time[contact_idx:liftoff_idx+1]
            fz_segment = fz[contact_idx:liftoff_idx+1]

            # Peso corporal
            body_weight = body_mass * self.gravity

            # Fuerza neta (GRF - peso)
            net_force = fz_segment - body_weight

            # Calcular impulso (integral de fuerza neta)
            impulse = np.trapz(net_force, time_segment)

            # Velocidad de despegue
            takeoff_velocity = impulse / body_mass

            # Altura del salto (cinemática)
            jump_height = (takeoff_velocity ** 2) / (2 * self.gravity)

            logger.debug(f"Altura de salto calculada: {jump_height:.3f} m (v_takeoff: {takeoff_velocity:.2f} m/s)")

            return max(0.0, jump_height)  # Evitar valores negativos

        except Exception as e:
            logger.error(f"Error calculando altura de salto: {str(e)}")
            return 0.0

    def segment_repetitions(self,
                           time: np.ndarray,
                           signal_data: np.ndarray,
                           threshold: float,
                           fs: float) -> List[Tuple[int, int]]:
        """
        Segmenta repeticiones en una señal.

        Args:
            time: Vector de tiempo
            signal_data: Señal a segmentar
            threshold: Umbral de detección
            fs: Frecuencia de muestreo

        Returns:
            Lista de tuplas (inicio, fin) de cada repetición
        """
        start_indices, end_indices = self.detect_events_threshold(
            signal_data, threshold, min_duration=0.5, fs=fs
        )

        repetitions = list(zip(start_indices, end_indices))

        logger.info(f"Repeticiones segmentadas: {len(repetitions)}")

        return repetitions

    def downsample(self,
                   data: np.ndarray,
                   original_fs: float,
                   target_fs: float) -> np.ndarray:
        """
        Reduce la frecuencia de muestreo (downsampling).

        Args:
            data: Señal original
            original_fs: Frecuencia original (Hz)
            target_fs: Frecuencia objetivo (Hz)

        Returns:
            Señal con frecuencia reducida
        """
        if target_fs >= original_fs:
            logger.warning("Frecuencia objetivo >= original. No se hace downsampling.")
            return data

        # Calcular factor de decimación
        decimation_factor = int(original_fs / target_fs)

        # Aplicar anti-aliasing filter antes de decimar
        nyquist = original_fs / 2
        cutoff = target_fs / 2

        if data.ndim == 1:
            # Filtrar
            filtered = self.filter_butterworth(data, cutoff, original_fs)
            # Decimar
            downsampled = filtered[::decimation_factor]
        else:
            # Múltiples columnas
            downsampled = np.zeros((len(data) // decimation_factor, data.shape[1]))
            for i in range(data.shape[1]):
                filtered = self.filter_butterworth(data[:, i], cutoff, original_fs)
                downsampled[:, i] = filtered[::decimation_factor]

        logger.debug(f"Downsampling: {original_fs} Hz -> {target_fs} Hz (factor: {decimation_factor})")

        return downsampled


# Funciones de conveniencia
def filter_signal(data: np.ndarray, cutoff: float, fs: float, order: int = 4) -> np.ndarray:
    """Filtra una señal (función de conveniencia)."""
    processor = SignalProcessor()
    return processor.filter_butterworth(data, cutoff, fs, order)


def detect_contacts(fz: np.ndarray, threshold: float = 20.0, fs: float = 1000) -> Tuple[np.ndarray, np.ndarray]:
    """Detecta contactos en GRF (función de conveniencia)."""
    processor = SignalProcessor()
    return processor.detect_grf_contacts(fz, threshold, fs)
