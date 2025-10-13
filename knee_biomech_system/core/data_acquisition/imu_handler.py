"""
Manejador de Sensores IMU Xsens DOT.

Este módulo gestiona la conexión, configuración y lectura
de datos de los sensores inerciales Xsens DOT vía Bluetooth.
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import time

try:
    from bleak import BleakScanner, BleakClient
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False
    print("Warning: bleak no instalado. Funcionalidad Bluetooth no disponible.")

from config.settings import IMU_CONFIG
from utils.logger import get_logger

logger = get_logger(__name__)


class SensorStatus(Enum):
    """Estado de un sensor."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    CALIBRATING = "calibrating"
    STREAMING = "streaming"
    ERROR = "error"


@dataclass
class IMUData:
    """
    Estructura de datos de un sensor IMU.

    Attributes:
        timestamp: Tiempo de la muestra (segundos)
        quaternion: Orientación como cuaternión [w, x, y, z]
        acceleration: Aceleración lineal [x, y, z] (m/s²)
        angular_velocity: Velocidad angular [x, y, z] (rad/s)
        battery_level: Nivel de batería (0-100%)
    """
    timestamp: float
    quaternion: np.ndarray  # [w, x, y, z]
    acceleration: np.ndarray  # [x, y, z]
    angular_velocity: np.ndarray  # [x, y, z]
    battery_level: Optional[float] = None


class XsensDOTSensor:
    """
    Clase para manejar un sensor Xsens DOT individual.

    Gestiona conexión Bluetooth, configuración y streaming de datos.
    """

    def __init__(self, location: str):
        """
        Inicializa el sensor.

        Args:
            location: Ubicación anatómica del sensor (e.g., 'pelvis', 'femur_right')
        """
        self.location = location
        self.status = SensorStatus.DISCONNECTED
        self.address: Optional[str] = None
        self.client: Optional[BleakClient] = None

        self.data_buffer: List[IMUData] = []
        self.battery_level: float = 100.0
        self.signal_quality: float = 0.0

        self.is_calibrated = False
        self.calibration_offset = {
            'quaternion': np.array([1.0, 0.0, 0.0, 0.0]),
            'acceleration': np.array([0.0, 0.0, 0.0])
        }

        logger.debug(f"Sensor {location} inicializado")

    async def connect(self, address: str, timeout: float = 10.0) -> bool:
        """
        Conecta al sensor vía Bluetooth.

        Args:
            address: Dirección MAC del sensor
            timeout: Tiempo máximo de espera (segundos)

        Returns:
            True si la conexión fue exitosa
        """
        if not BLUETOOTH_AVAILABLE:
            logger.error("Bluetooth no disponible - bleak no instalado")
            return False

        try:
            self.status = SensorStatus.CONNECTING
            self.address = address

            logger.info(f"Conectando a sensor {self.location} ({address})...")

            self.client = BleakClient(address, timeout=timeout)
            await self.client.connect()

            if self.client.is_connected:
                self.status = SensorStatus.CONNECTED
                logger.info(f"Sensor {self.location} conectado exitosamente")

                # Leer nivel de batería (si el servicio está disponible)
                await self.read_battery_level()

                return True
            else:
                self.status = SensorStatus.ERROR
                logger.error(f"No se pudo conectar a sensor {self.location}")
                return False

        except Exception as e:
            self.status = SensorStatus.ERROR
            logger.error(f"Error conectando sensor {self.location}: {str(e)}", exc_info=True)
            return False

    async def disconnect(self) -> bool:
        """Desconecta el sensor."""
        try:
            if self.client and self.client.is_connected:
                await self.client.disconnect()
                logger.info(f"Sensor {self.location} desconectado")

            self.status = SensorStatus.DISCONNECTED
            return True

        except Exception as e:
            logger.error(f"Error desconectando sensor {self.location}: {str(e)}")
            return False

    async def read_battery_level(self) -> Optional[float]:
        """
        Lee el nivel de batería del sensor.

        Returns:
            Nivel de batería (0-100%) o None si falla
        """
        try:
            # UUID estándar para servicio de batería BLE
            BATTERY_SERVICE_UUID = "0000180f-0000-1000-8000-00805f9b34fb"
            BATTERY_CHAR_UUID = "00002a19-0000-1000-8000-00805f9b34fb"

            if self.client and self.client.is_connected:
                battery_bytes = await self.client.read_gatt_char(BATTERY_CHAR_UUID)
                self.battery_level = int.from_bytes(battery_bytes, byteorder='little')
                logger.debug(f"Batería {self.location}: {self.battery_level}%")
                return self.battery_level

        except Exception as e:
            logger.warning(f"No se pudo leer batería de {self.location}: {str(e)}")
            return None

    async def calibrate(self, duration: float = 5.0) -> bool:
        """
        Calibra el sensor en posición estática.

        Args:
            duration: Duración de la calibración en segundos

        Returns:
            True si la calibración fue exitosa
        """
        try:
            self.status = SensorStatus.CALIBRATING
            logger.info(f"Calibrando sensor {self.location} por {duration}s...")

            # Aquí iría la lógica real de calibración con el sensor
            # Por ahora, simulamos una espera
            await asyncio.sleep(duration)

            # En implementación real, calcularíamos offsets basados en datos recolectados
            self.is_calibrated = True
            self.status = SensorStatus.CONNECTED

            logger.info(f"Sensor {self.location} calibrado exitosamente")
            return True

        except Exception as e:
            logger.error(f"Error calibrando sensor {self.location}: {str(e)}")
            self.status = SensorStatus.ERROR
            return False

    async def start_streaming(self, callback: Optional[Callable] = None) -> bool:
        """
        Inicia el streaming de datos del sensor.

        Args:
            callback: Función a llamar cuando lleguen nuevos datos

        Returns:
            True si el streaming inició correctamente
        """
        try:
            if not self.client or not self.client.is_connected:
                logger.error(f"Sensor {self.location} no está conectado")
                return False

            self.status = SensorStatus.STREAMING
            logger.info(f"Streaming iniciado en sensor {self.location}")

            # En implementación real, suscribirse a notificaciones BLE
            # y procesar datos entrantes

            return True

        except Exception as e:
            logger.error(f"Error iniciando streaming en {self.location}: {str(e)}")
            return False

    async def stop_streaming(self) -> bool:
        """Detiene el streaming de datos."""
        try:
            if self.status == SensorStatus.STREAMING:
                # Desuscribirse de notificaciones
                self.status = SensorStatus.CONNECTED
                logger.info(f"Streaming detenido en sensor {self.location}")

            return True

        except Exception as e:
            logger.error(f"Error deteniendo streaming en {self.location}: {str(e)}")
            return False

    def add_data_sample(self, data: IMUData):
        """Añade una muestra de datos al buffer."""
        self.data_buffer.append(data)

    def get_data_buffer(self) -> List[IMUData]:
        """Obtiene el buffer de datos."""
        return self.data_buffer.copy()

    def clear_buffer(self):
        """Limpia el buffer de datos."""
        self.data_buffer.clear()


class IMUHandler:
    """
    Manejador principal para todos los sensores IMU.

    Coordina la conexión, calibración y captura de datos
    de los 7 sensores Xsens DOT.
    """

    def __init__(self):
        """Inicializa el manejador de IMUs."""
        self.sensors: Dict[str, XsensDOTSensor] = {}
        self.locations = IMU_CONFIG["locations"]
        self.sampling_rate = IMU_CONFIG["sampling_rate"]

        # Crear objetos de sensores para cada ubicación
        for location in self.locations:
            self.sensors[location] = XsensDOTSensor(location)

        self.is_recording = False
        self.start_time: Optional[float] = None

        logger.info(f"IMUHandler inicializado con {len(self.sensors)} sensores")

    async def scan_sensors(self, duration: float = 5.0) -> List[Dict]:
        """
        Escanea sensores Xsens DOT disponibles.

        Args:
            duration: Duración del escaneo en segundos

        Returns:
            Lista de diccionarios con información de sensores encontrados
        """
        if not BLUETOOTH_AVAILABLE:
            logger.error("Bluetooth no disponible")
            return []

        try:
            logger.info(f"Escaneando sensores por {duration}s...")

            devices = await BleakScanner.discover(timeout=duration)

            # Filtrar solo sensores Xsens DOT
            xsens_devices = []
            for device in devices:
                if device.name and "Xsens DOT" in device.name:
                    xsens_devices.append({
                        "name": device.name,
                        "address": device.address,
                        "rssi": device.rssi
                    })

            logger.info(f"Encontrados {len(xsens_devices)} sensores Xsens DOT")
            return xsens_devices

        except Exception as e:
            logger.error(f"Error escaneando sensores: {str(e)}", exc_info=True)
            return []

    async def connect_sensor(self, location: str, address: str) -> bool:
        """
        Conecta un sensor específico.

        Args:
            location: Ubicación del sensor
            address: Dirección MAC del sensor

        Returns:
            True si la conexión fue exitosa
        """
        if location not in self.sensors:
            logger.error(f"Ubicación inválida: {location}")
            return False

        return await self.sensors[location].connect(address)

    async def connect_all_sensors(self, address_mapping: Dict[str, str]) -> bool:
        """
        Conecta todos los sensores según un mapeo de direcciones.

        Args:
            address_mapping: Diccionario {location: address}

        Returns:
            True si todos los sensores se conectaron exitosamente
        """
        try:
            logger.info("Conectando todos los sensores...")

            tasks = []
            for location, address in address_mapping.items():
                if location in self.sensors:
                    tasks.append(self.connect_sensor(location, address))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            success = all(isinstance(r, bool) and r for r in results)

            if success:
                logger.info("✓ Todos los sensores conectados")
            else:
                logger.warning("⚠ Algunos sensores no se pudieron conectar")

            return success

        except Exception as e:
            logger.error(f"Error conectando sensores: {str(e)}", exc_info=True)
            return False

    async def disconnect_all_sensors(self) -> bool:
        """Desconecta todos los sensores."""
        try:
            logger.info("Desconectando todos los sensores...")

            tasks = [sensor.disconnect() for sensor in self.sensors.values()]
            await asyncio.gather(*tasks, return_exceptions=True)

            logger.info("✓ Todos los sensores desconectados")
            return True

        except Exception as e:
            logger.error(f"Error desconectando sensores: {str(e)}")
            return False

    async def calibrate_all_sensors(self, duration: float = 5.0) -> bool:
        """
        Calibra todos los sensores simultáneamente.

        Args:
            duration: Duración de la calibración en segundos

        Returns:
            True si todos se calibraron exitosamente
        """
        try:
            logger.info(f"Calibrando todos los sensores ({duration}s)...")

            tasks = [sensor.calibrate(duration) for sensor in self.sensors.values()]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            success = all(isinstance(r, bool) and r for r in results)

            if success:
                logger.info("✓ Todos los sensores calibrados")
            else:
                logger.warning("⚠ Algunos sensores no se pudieron calibrar")

            return success

        except Exception as e:
            logger.error(f"Error calibrando sensores: {str(e)}", exc_info=True)
            return False

    async def start_recording(self) -> bool:
        """Inicia la grabación de datos de todos los sensores."""
        try:
            if self.is_recording:
                logger.warning("Ya está grabando")
                return False

            logger.info("Iniciando grabación...")

            # Limpiar buffers
            for sensor in self.sensors.values():
                sensor.clear_buffer()

            # Iniciar streaming en todos los sensores
            tasks = [sensor.start_streaming() for sensor in self.sensors.values()]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            if all(isinstance(r, bool) and r for r in results):
                self.is_recording = True
                self.start_time = time.time()
                logger.info("✓ Grabación iniciada")
                return True
            else:
                logger.error("Error iniciando grabación en algunos sensores")
                return False

        except Exception as e:
            logger.error(f"Error iniciando grabación: {str(e)}", exc_info=True)
            return False

    async def stop_recording(self) -> bool:
        """Detiene la grabación de datos."""
        try:
            if not self.is_recording:
                logger.warning("No está grabando")
                return False

            logger.info("Deteniendo grabación...")

            # Detener streaming en todos los sensores
            tasks = [sensor.stop_streaming() for sensor in self.sensors.values()]
            await asyncio.gather(*tasks, return_exceptions=True)

            self.is_recording = False

            duration = time.time() - self.start_time if self.start_time else 0
            logger.info(f"✓ Grabación detenida (duración: {duration:.2f}s)")

            return True

        except Exception as e:
            logger.error(f"Error deteniendo grabación: {str(e)}", exc_info=True)
            return False

    def get_all_data(self) -> Dict[str, List[IMUData]]:
        """
        Obtiene los datos de todos los sensores.

        Returns:
            Diccionario {location: [IMUData]}
        """
        return {
            location: sensor.get_data_buffer()
            for location, sensor in self.sensors.items()
        }

    def get_sensor_status(self, location: str) -> Optional[SensorStatus]:
        """Obtiene el estado de un sensor específico."""
        if location in self.sensors:
            return self.sensors[location].status
        return None

    def get_all_sensors_status(self) -> Dict[str, SensorStatus]:
        """Obtiene el estado de todos los sensores."""
        return {
            location: sensor.status
            for location, sensor in self.sensors.items()
        }

    def is_all_connected(self) -> bool:
        """Verifica si todos los sensores están conectados."""
        return all(
            sensor.status in [SensorStatus.CONNECTED, SensorStatus.STREAMING, SensorStatus.CALIBRATING]
            for sensor in self.sensors.values()
        )

    def is_all_calibrated(self) -> bool:
        """Verifica si todos los sensores están calibrados."""
        return all(sensor.is_calibrated for sensor in self.sensors.values())
