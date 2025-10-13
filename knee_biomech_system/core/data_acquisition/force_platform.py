"""
Manejador de Plataforma de Fuerza Valkyria.

Este módulo gestiona la importación y procesamiento de datos
desde archivos Excel generados por la plataforma Valkyria.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

from config.settings import FORCE_PLATFORM_CONFIG, PHYSICAL_CONSTANTS
from utils.logger import get_logger

logger = get_logger(__name__)


class ForcePlatformHandler:
    """
    Manejador para importar datos de plataforma de fuerza Valkyria.

    La plataforma genera archivos Excel con las siguientes columnas:
    - Time (s): Tiempo en segundos
    - Fx (N): Fuerza en dirección X (mediolateral)
    - Fy (N): Fuerza en dirección Y (anteroposterior)
    - Fz (N): Fuerza en dirección Z (vertical)
    - Mx (Nm): Momento alrededor del eje X
    - My (Nm): Momento alrededor del eje Y
    - Mz (Nm): Momento alrededor del eje Z
    """

    def __init__(self):
        """Inicializa el manejador de plataforma de fuerza."""
        self.sampling_rate = FORCE_PLATFORM_CONFIG["sampling_rate"]
        self.dimensions = FORCE_PLATFORM_CONFIG["dimensions"]  # (ancho, largo) en metros
        self.zero_threshold = FORCE_PLATFORM_CONFIG["zero_threshold"]

        self.data: Optional[pd.DataFrame] = None
        self.file_path: Optional[Path] = None
        self.is_calibrated = False
        self.offset_values: Dict[str, float] = {}

        logger.info(f"ForcePlatformHandler inicializado - {self.sampling_rate} Hz")

    def import_from_excel(self, file_path: str) -> bool:
        """
        Importa datos desde un archivo Excel de Valkyria.

        Args:
            file_path: Ruta al archivo Excel (.xlsx)

        Returns:
            True si la importación fue exitosa, False en caso contrario
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                logger.error(f"Archivo no encontrado: {file_path}")
                return False

            if file_path.suffix.lower() not in ['.xlsx', '.xls']:
                logger.error(f"Formato de archivo no soportado: {file_path.suffix}")
                return False

            logger.info(f"Importando datos desde: {file_path}")

            # Leer archivo Excel
            df = pd.read_excel(file_path)

            # Mapear nombres de columnas según configuración
            col_mapping = FORCE_PLATFORM_CONFIG["excel_columns"]

            # Verificar que todas las columnas necesarias existen
            required_cols = list(col_mapping.values())
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                logger.error(f"Columnas faltantes en el archivo: {missing_cols}")
                logger.info(f"Columnas encontradas: {df.columns.tolist()}")
                return False

            # Renombrar columnas a formato estándar
            reverse_mapping = {v: k for k, v in col_mapping.items()}
            df = df.rename(columns=reverse_mapping)

            # Verificar datos válidos
            if len(df) == 0:
                logger.error("El archivo no contiene datos")
                return False

            self.data = df
            self.file_path = file_path

            # Información sobre los datos
            duration = df['time'].max() - df['time'].min()
            num_samples = len(df)
            actual_rate = num_samples / duration if duration > 0 else 0

            logger.info(
                f"Datos importados exitosamente: {num_samples} muestras, "
                f"duración: {duration:.2f}s, frecuencia: {actual_rate:.1f} Hz"
            )

            return True

        except Exception as e:
            logger.error(f"Error al importar datos: {str(e)}", exc_info=True)
            return False

    def calibrate_zero(self, duration: float = 1.0) -> bool:
        """
        Calibra el cero de la plataforma usando las primeras muestras.

        Args:
            duration: Duración en segundos para calcular el offset (default: 1.0s)

        Returns:
            True si la calibración fue exitosa
        """
        if self.data is None:
            logger.error("No hay datos cargados para calibrar")
            return False

        try:
            # Seleccionar muestras del inicio
            calibration_data = self.data[self.data['time'] <= duration]

            if len(calibration_data) == 0:
                logger.error(f"No hay suficientes datos para calibrar ({duration}s)")
                return False

            # Calcular offsets (promedios)
            channels = ['fx', 'fy', 'fz', 'mx', 'my', 'mz']
            self.offset_values = {}

            for channel in channels:
                offset = calibration_data[channel].mean()
                self.offset_values[channel] = offset

            # Aplicar corrección de offset
            for channel in channels:
                self.data[channel] = self.data[channel] - self.offset_values[channel]

            self.is_calibrated = True

            logger.info(
                f"Calibración completada - Offsets: "
                f"Fz={self.offset_values['fz']:.2f}N, "
                f"Fx={self.offset_values['fx']:.2f}N, "
                f"Fy={self.offset_values['fy']:.2f}N"
            )

            return True

        except Exception as e:
            logger.error(f"Error en calibración: {str(e)}", exc_info=True)
            return False

    def calculate_cop(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calcula el Centro de Presión (COP).

        El COP se calcula como:
        COPx = -My / Fz
        COPy = Mx / Fz

        Returns:
            Tuple (cop_x, cop_y) en metros
        """
        if self.data is None:
            logger.error("No hay datos cargados")
            return np.array([]), np.array([])

        try:
            fz = self.data['fz'].values
            mx = self.data['mx'].values
            my = self.data['my'].values

            # Evitar división por cero
            fz_safe = np.where(np.abs(fz) < self.zero_threshold, np.nan, fz)

            cop_x = -my / fz_safe
            cop_y = mx / fz_safe

            # Filtrar valores fuera de la plataforma
            width, length = self.dimensions
            cop_x = np.clip(cop_x, -width/2, width/2)
            cop_y = np.clip(cop_y, -length/2, length/2)

            logger.debug(f"COP calculado - {len(cop_x)} puntos")

            return cop_x, cop_y

        except Exception as e:
            logger.error(f"Error al calcular COP: {str(e)}", exc_info=True)
            return np.array([]), np.array([])

    def get_resultant_force(self) -> np.ndarray:
        """
        Calcula la fuerza resultante total.

        Returns:
            Vector de fuerza resultante en N
        """
        if self.data is None:
            return np.array([])

        fx = self.data['fx'].values
        fy = self.data['fy'].values
        fz = self.data['fz'].values

        resultant = np.sqrt(fx**2 + fy**2 + fz**2)

        return resultant

    def get_data_dict(self) -> Dict[str, np.ndarray]:
        """
        Obtiene los datos en formato de diccionario.

        Returns:
            Diccionario con todos los canales de datos
        """
        if self.data is None:
            return {}

        return {
            'time': self.data['time'].values,
            'fx': self.data['fx'].values,
            'fy': self.data['fy'].values,
            'fz': self.data['fz'].values,
            'mx': self.data['mx'].values,
            'my': self.data['my'].values,
            'mz': self.data['mz'].values
        }

    def detect_contact_events(self, threshold: float = 20.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detecta eventos de contacto y despegue en la plataforma.

        Args:
            threshold: Umbral de fuerza vertical para detectar contacto (N)

        Returns:
            Tuple (indices_contacto, indices_despegue)
        """
        if self.data is None:
            return np.array([]), np.array([])

        try:
            fz = self.data['fz'].values

            # Detectar transiciones
            contact_mask = fz > threshold
            diff = np.diff(contact_mask.astype(int))

            # Índices de contacto (0 -> 1) y despegue (1 -> 0)
            contact_indices = np.where(diff == 1)[0] + 1
            liftoff_indices = np.where(diff == -1)[0] + 1

            logger.info(
                f"Eventos detectados: {len(contact_indices)} contactos, "
                f"{len(liftoff_indices)} despegues"
            )

            return contact_indices, liftoff_indices

        except Exception as e:
            logger.error(f"Error al detectar eventos: {str(e)}", exc_info=True)
            return np.array([]), np.array([])

    def calculate_loading_rate(self, contact_indices: np.ndarray,
                               window: float = 0.05) -> np.ndarray:
        """
        Calcula la tasa de carga (loading rate) en cada contacto.

        Args:
            contact_indices: Índices de eventos de contacto
            window: Ventana de tiempo en segundos para calcular la tasa (default: 50ms)

        Returns:
            Array con tasas de carga en N/s
        """
        if self.data is None or len(contact_indices) == 0:
            return np.array([])

        try:
            fz = self.data['fz'].values
            time = self.data['time'].values
            loading_rates = []

            for idx in contact_indices:
                # Ventana después del contacto
                window_mask = (time >= time[idx]) & (time <= time[idx] + window)
                window_indices = np.where(window_mask)[0]

                if len(window_indices) > 1:
                    # Calcular pendiente (tasa de cambio)
                    fz_window = fz[window_indices]
                    time_window = time[window_indices]

                    # Regresión lineal simple
                    slope = np.polyfit(time_window, fz_window, 1)[0]
                    loading_rates.append(slope)
                else:
                    loading_rates.append(0.0)

            return np.array(loading_rates)

        except Exception as e:
            logger.error(f"Error al calcular loading rate: {str(e)}", exc_info=True)
            return np.array([])

    def calculate_impulse(self, start_time: float = None, end_time: float = None) -> Dict[str, float]:
        """
        Calcula el impulso (integral de la fuerza).

        Args:
            start_time: Tiempo de inicio (None = desde el principio)
            end_time: Tiempo de finalización (None = hasta el final)

        Returns:
            Diccionario con impulsos en cada dirección (Ns)
        """
        if self.data is None:
            return {}

        try:
            # Filtrar por tiempo
            mask = np.ones(len(self.data), dtype=bool)
            if start_time is not None:
                mask &= self.data['time'] >= start_time
            if end_time is not None:
                mask &= self.data['time'] <= end_time

            data_segment = self.data[mask]

            if len(data_segment) < 2:
                return {}

            time = data_segment['time'].values

            impulse = {}
            for axis in ['fx', 'fy', 'fz']:
                force = data_segment[axis].values
                # Integración trapezoidal
                impulse[axis] = np.trapz(force, time)

            logger.debug(f"Impulso calculado: Fz={impulse['fz']:.2f} Ns")

            return impulse

        except Exception as e:
            logger.error(f"Error al calcular impulso: {str(e)}", exc_info=True)
            return {}

    def get_summary_stats(self) -> Dict:
        """
        Obtiene estadísticas resumen de los datos.

        Returns:
            Diccionario con estadísticas
        """
        if self.data is None:
            return {}

        try:
            stats = {
                'duration': self.data['time'].max() - self.data['time'].min(),
                'num_samples': len(self.data),
                'sampling_rate': len(self.data) / (self.data['time'].max() - self.data['time'].min()),
                'peak_fz': self.data['fz'].max(),
                'mean_fz': self.data['fz'].mean(),
                'peak_fx': self.data['fx'].abs().max(),
                'peak_fy': self.data['fy'].abs().max(),
                'is_calibrated': self.is_calibrated
            }

            return stats

        except Exception as e:
            logger.error(f"Error al calcular estadísticas: {str(e)}", exc_info=True)
            return {}

    def export_processed_data(self, output_path: str) -> bool:
        """
        Exporta los datos procesados a CSV.

        Args:
            output_path: Ruta de salida

        Returns:
            True si la exportación fue exitosa
        """
        if self.data is None:
            logger.error("No hay datos para exportar")
            return False

        try:
            output_path = Path(output_path)
            self.data.to_csv(output_path, index=False)
            logger.info(f"Datos exportados a: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error al exportar datos: {str(e)}", exc_info=True)
            return False
