"""
Sincronizador de señales.

Sincroniza datos de sensores IMU y plataforma de fuerza mediante
interpolación y correlación cruzada.
"""

import numpy as np
from scipy import signal, interpolate
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

from config.settings import SYNC_CONFIG
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SyncResult:
    """
    Resultado de sincronización.

    Attributes:
        time_common: Vector de tiempo común (segundos)
        imu_data_synced: Datos IMU sincronizados
        force_data_synced: Datos de fuerza sincronizados
        time_offset: Offset temporal calculado (segundos)
        sync_quality: Calidad de sincronización (0-1)
        success: Si la sincronización fue exitosa
    """
    time_common: np.ndarray
    imu_data_synced: Dict[str, Dict[str, np.ndarray]]
    force_data_synced: Dict[str, np.ndarray]
    time_offset: float
    sync_quality: float
    success: bool


class DataSynchronizer:
    """
    Sincronizador de datos de múltiples fuentes.

    Sincroniza datos de IMU (60 Hz) con datos de plataforma de fuerza (1000 Hz)
    mediante interpolación a frecuencia común y correlación cruzada.
    """

    def __init__(self):
        """Inicializa el sincronizador."""
        self.target_frequency = SYNC_CONFIG["target_frequency"]
        self.interpolation_method = SYNC_CONFIG["interpolation_method"]
        self.max_time_offset = SYNC_CONFIG["max_time_offset"]
        self.sync_error_threshold = SYNC_CONFIG["sync_error_threshold"]

        logger.info(f"DataSynchronizer inicializado - Frecuencia objetivo: {self.target_frequency} Hz")

    def synchronize(self,
                   time_imu: np.ndarray,
                   imu_data: Dict[str, Dict[str, np.ndarray]],
                   time_force: np.ndarray,
                   force_data: Dict[str, np.ndarray]) -> SyncResult:
        """
        Sincroniza datos de IMU y fuerza.

        Args:
            time_imu: Vector de tiempo IMU (segundos)
            imu_data: Diccionario {sensor_location: {data_type: array}}
            time_force: Vector de tiempo de fuerza (segundos)
            force_data: Diccionario {channel: array}

        Returns:
            SyncResult con datos sincronizados
        """
        try:
            logger.info("Iniciando sincronización de datos...")

            # 1. Validar datos de entrada
            if not self._validate_inputs(time_imu, time_force):
                return self._failed_result()

            # 2. Determinar ventana temporal común
            time_start = max(time_imu[0], time_force[0])
            time_end = min(time_imu[-1], time_force[-1])

            if time_end <= time_start:
                logger.error("No hay superposición temporal entre las señales")
                return self._failed_result()

            logger.info(f"Ventana temporal común: {time_start:.2f}s a {time_end:.2f}s ({time_end - time_start:.2f}s)")

            # 3. Crear vector de tiempo común
            num_samples = int((time_end - time_start) * self.target_frequency)
            time_common = np.linspace(time_start, time_end, num_samples)

            logger.info(f"Vector de tiempo común: {num_samples} muestras @ {self.target_frequency} Hz")

            # 4. Interpolar datos IMU
            imu_data_synced = self._interpolate_imu_data(time_imu, imu_data, time_common)

            # 5. Interpolar datos de fuerza
            force_data_synced = self._interpolate_force_data(time_force, force_data, time_common)

            # 6. Detectar offset temporal mediante correlación cruzada
            time_offset = self._detect_time_offset(
                time_common,
                force_data_synced['fz'],
                imu_data_synced
            )

            logger.info(f"Offset temporal detectado: {time_offset*1000:.2f} ms")

            # 7. Aplicar corrección de offset si es necesario
            if abs(time_offset) > self.sync_error_threshold:
                logger.warning(f"Offset grande detectado: {time_offset*1000:.2f} ms")
                # Aplicar corrección temporal
                time_common = time_common + time_offset

            # 8. Calcular calidad de sincronización
            sync_quality = self._calculate_sync_quality(time_offset)

            logger.info(f"Sincronización completada - Calidad: {sync_quality:.2%}")

            return SyncResult(
                time_common=time_common,
                imu_data_synced=imu_data_synced,
                force_data_synced=force_data_synced,
                time_offset=time_offset,
                sync_quality=sync_quality,
                success=True
            )

        except Exception as e:
            logger.error(f"Error en sincronización: {str(e)}", exc_info=True)
            return self._failed_result()

    def _validate_inputs(self, time_imu: np.ndarray, time_force: np.ndarray) -> bool:
        """
        Valida los datos de entrada.

        Args:
            time_imu: Vector de tiempo IMU
            time_force: Vector de tiempo de fuerza

        Returns:
            True si los datos son válidos
        """
        if len(time_imu) < 10:
            logger.error("Datos IMU insuficientes (< 10 muestras)")
            return False

        if len(time_force) < 10:
            logger.error("Datos de fuerza insuficientes (< 10 muestras)")
            return False

        # Verificar monotonía
        if not np.all(np.diff(time_imu) > 0):
            logger.error("Vector de tiempo IMU no es monótonamente creciente")
            return False

        if not np.all(np.diff(time_force) > 0):
            logger.error("Vector de tiempo de fuerza no es monótonamente creciente")
            return False

        return True

    def _interpolate_imu_data(self,
                             time_orig: np.ndarray,
                             data: Dict[str, Dict[str, np.ndarray]],
                             time_new: np.ndarray) -> Dict[str, Dict[str, np.ndarray]]:
        """
        Interpola datos IMU a nuevo vector de tiempo.

        Args:
            time_orig: Vector de tiempo original
            data: Datos IMU originales
            time_new: Vector de tiempo nuevo

        Returns:
            Datos interpolados
        """
        interpolated = {}

        for sensor_location, sensor_data in data.items():
            interpolated[sensor_location] = {}

            for data_type, values in sensor_data.items():
                # Interpolar cada componente
                if values.ndim == 1:
                    # Escalar
                    f = interpolate.interp1d(
                        time_orig, values,
                        kind=self.interpolation_method,
                        fill_value='extrapolate'
                    )
                    interpolated[sensor_location][data_type] = f(time_new)
                else:
                    # Vector (ej: quaternion, acceleration)
                    interpolated[sensor_location][data_type] = np.zeros((len(time_new), values.shape[1]))
                    for i in range(values.shape[1]):
                        f = interpolate.interp1d(
                            time_orig, values[:, i],
                            kind=self.interpolation_method,
                            fill_value='extrapolate'
                        )
                        interpolated[sensor_location][data_type][:, i] = f(time_new)

        logger.debug(f"Datos IMU interpolados: {len(interpolated)} sensores")
        return interpolated

    def _interpolate_force_data(self,
                               time_orig: np.ndarray,
                               data: Dict[str, np.ndarray],
                               time_new: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Interpola datos de fuerza a nuevo vector de tiempo.

        Args:
            time_orig: Vector de tiempo original
            data: Datos de fuerza originales
            time_new: Vector de tiempo nuevo

        Returns:
            Datos interpolados
        """
        interpolated = {}

        for channel, values in data.items():
            f = interpolate.interp1d(
                time_orig, values,
                kind=self.interpolation_method,
                fill_value='extrapolate'
            )
            interpolated[channel] = f(time_new)

        logger.debug(f"Datos de fuerza interpolados: {len(interpolated)} canales")
        return interpolated

    def _detect_time_offset(self,
                           time_common: np.ndarray,
                           force_vertical: np.ndarray,
                           imu_data: Dict[str, Dict[str, np.ndarray]]) -> float:
        """
        Detecta offset temporal mediante correlación cruzada.

        Usa la fuerza vertical y la aceleración vertical de un sensor IMU.

        Args:
            time_common: Vector de tiempo común
            force_vertical: Fuerza vertical (Fz)
            imu_data: Datos IMU interpolados

        Returns:
            Offset temporal en segundos
        """
        try:
            # Usar aceleración del sensor de pelvis (o primer sensor disponible)
            sensor_locations = ['pelvis', 'femur_right', 'femur_left']
            acc_vertical = None

            for location in sensor_locations:
                if location in imu_data and 'acceleration' in imu_data[location]:
                    # Componente Z (vertical)
                    acc_vertical = imu_data[location]['acceleration'][:, 2]
                    break

            if acc_vertical is None:
                logger.warning("No se encontró aceleración vertical para correlación")
                return 0.0

            # Normalizar señales
            force_norm = (force_vertical - np.mean(force_vertical)) / np.std(force_vertical)
            acc_norm = (acc_vertical - np.mean(acc_vertical)) / np.std(acc_vertical)

            # Calcular correlación cruzada
            correlation = signal.correlate(force_norm, acc_norm, mode='same')
            lags = signal.correlation_lags(len(force_norm), len(acc_norm), mode='same')

            # Encontrar el lag con máxima correlación
            max_corr_idx = np.argmax(np.abs(correlation))
            optimal_lag = lags[max_corr_idx]

            # Convertir lag a tiempo
            dt = time_common[1] - time_common[0]
            time_offset = optimal_lag * dt

            # Limitar offset máximo
            if abs(time_offset) > self.max_time_offset:
                logger.warning(f"Offset muy grande ({time_offset:.3f}s), limitando a {self.max_time_offset}s")
                time_offset = np.sign(time_offset) * self.max_time_offset

            return time_offset

        except Exception as e:
            logger.error(f"Error detectando offset: {str(e)}")
            return 0.0

    def _calculate_sync_quality(self, time_offset: float) -> float:
        """
        Calcula calidad de sincronización (0-1).

        Args:
            time_offset: Offset temporal detectado

        Returns:
            Calidad (0 = pobre, 1 = excelente)
        """
        # Calidad basada en el offset temporal
        # Offset < 1ms = calidad 1.0
        # Offset > 100ms = calidad 0.0

        if abs(time_offset) < 0.001:  # < 1ms
            return 1.0
        elif abs(time_offset) > 0.1:  # > 100ms
            return 0.0
        else:
            # Interpolación lineal
            return 1.0 - (abs(time_offset) - 0.001) / (0.1 - 0.001)

    def _failed_result(self) -> SyncResult:
        """
        Retorna un resultado de sincronización fallido.

        Returns:
            SyncResult con success=False
        """
        return SyncResult(
            time_common=np.array([]),
            imu_data_synced={},
            force_data_synced={},
            time_offset=0.0,
            sync_quality=0.0,
            success=False
        )


# Función de conveniencia
def synchronize_data(time_imu: np.ndarray,
                    imu_data: Dict,
                    time_force: np.ndarray,
                    force_data: Dict) -> SyncResult:
    """
    Sincroniza datos de IMU y fuerza (función de conveniencia).

    Args:
        time_imu: Vector de tiempo IMU
        imu_data: Datos IMU
        time_force: Vector de tiempo de fuerza
        force_data: Datos de fuerza

    Returns:
        SyncResult
    """
    synchronizer = DataSynchronizer()
    return synchronizer.synchronize(time_imu, imu_data, time_force, force_data)
