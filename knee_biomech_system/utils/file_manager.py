"""
Gestión de archivos y datos del sistema.

Proporciona funcionalidades para guardar, cargar, exportar
y gestionar archivos de datos del sistema biomecánico.
"""

import os
import json
import pickle
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import shutil

import pandas as pd
import numpy as np

from config.settings import (
    RAW_DATA_DIR, PROCESSED_DATA_DIR, RESULTS_DIR,
    MODELS_DIR, DATABASE_CONFIG
)
from utils.logger import get_logger

logger = get_logger(__name__)


class FileManager:
    """
    Gestor de archivos del sistema.

    Maneja operaciones de I/O, organización de datos,
    y exportación en diferentes formatos.
    """

    def __init__(self):
        """Inicializa el gestor de archivos."""
        self.raw_dir = RAW_DATA_DIR
        self.processed_dir = PROCESSED_DATA_DIR
        self.results_dir = RESULTS_DIR
        self.models_dir = MODELS_DIR

        # Asegurar que directorios existen
        self._ensure_directories()

    def _ensure_directories(self):
        """Crea directorios si no existen."""
        for directory in [self.raw_dir, self.processed_dir, self.results_dir, self.models_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def generate_filename(self, patient_id: str, exercise: str,
                         category: str = "session", extension: str = "pkl") -> str:
        """
        Genera un nombre de archivo único con timestamp.

        Args:
            patient_id: ID del paciente
            exercise: Tipo de ejercicio
            category: Categoría del archivo (session, analysis, report)
            extension: Extensión del archivo

        Returns:
            Nombre de archivo con formato: PatientID_Exercise_Category_Timestamp.ext
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{patient_id}_{exercise}_{category}_{timestamp}.{extension}"
        return filename

    def save_session_data(self, session_id: str, patient_id: str,
                         exercise: str, data: Dict[str, Any]) -> Optional[Path]:
        """
        Guarda datos de una sesión en formato pickle.

        Args:
            session_id: ID de la sesión
            patient_id: ID del paciente
            exercise: Tipo de ejercicio
            data: Diccionario con datos a guardar

        Returns:
            Path del archivo guardado o None si falla
        """
        try:
            filename = self.generate_filename(patient_id, exercise, "session", "pkl")
            filepath = self.processed_dir / filename

            # Añadir metadata
            data['_metadata'] = {
                'session_id': session_id,
                'patient_id': patient_id,
                'exercise': exercise,
                'saved_at': datetime.now().isoformat(),
                'version': '1.0'
            }

            with open(filepath, 'wb') as f:
                pickle.dump(data, f)

            logger.info(f"Sesión guardada: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error guardando sesión: {str(e)}", exc_info=True)
            return None

    def load_session_data(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """
        Carga datos de una sesión desde archivo pickle.

        Args:
            filepath: Ruta al archivo

        Returns:
            Diccionario con datos o None si falla
        """
        try:
            if not filepath.exists():
                logger.error(f"Archivo no encontrado: {filepath}")
                return None

            with open(filepath, 'rb') as f:
                data = pickle.load(f)

            logger.info(f"Sesión cargada: {filepath}")
            return data

        except Exception as e:
            logger.error(f"Error cargando sesión: {str(e)}", exc_info=True)
            return None

    def save_results(self, session_id: str, patient_id: str,
                    exercise: str, results: Dict[str, Any]) -> Optional[Path]:
        """
        Guarda resultados de análisis en formato JSON.

        Args:
            session_id: ID de la sesión
            patient_id: ID del paciente
            exercise: Tipo de ejercicio
            results: Diccionario con resultados

        Returns:
            Path del archivo guardado o None si falla
        """
        try:
            filename = self.generate_filename(patient_id, exercise, "results", "json")
            filepath = self.results_dir / filename

            # Convertir numpy arrays a listas para JSON
            results_serializable = self._make_json_serializable(results)

            # Añadir metadata
            results_serializable['_metadata'] = {
                'session_id': session_id,
                'patient_id': patient_id,
                'exercise': exercise,
                'analyzed_at': datetime.now().isoformat()
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results_serializable, f, indent=2, ensure_ascii=False)

            logger.info(f"Resultados guardados: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error guardando resultados: {str(e)}", exc_info=True)
            return None

    def _make_json_serializable(self, obj: Any) -> Any:
        """
        Convierte objetos a formato serializable en JSON.

        Args:
            obj: Objeto a convertir

        Returns:
            Objeto serializable
        """
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        else:
            return obj

    def export_to_csv(self, data: pd.DataFrame, patient_id: str,
                     exercise: str, data_type: str = "timeseries") -> Optional[Path]:
        """
        Exporta datos a formato CSV.

        Args:
            data: DataFrame con datos
            patient_id: ID del paciente
            exercise: Tipo de ejercicio
            data_type: Tipo de datos (timeseries, metrics, etc.)

        Returns:
            Path del archivo exportado o None si falla
        """
        try:
            filename = self.generate_filename(patient_id, exercise, data_type, "csv")
            filepath = self.results_dir / filename

            data.to_csv(filepath, index=False, encoding='utf-8')

            logger.info(f"Datos exportados a CSV: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error exportando CSV: {str(e)}", exc_info=True)
            return None

    def export_to_excel(self, data_dict: Dict[str, pd.DataFrame],
                       patient_id: str, exercise: str) -> Optional[Path]:
        """
        Exporta múltiples DataFrames a archivo Excel con hojas separadas.

        Args:
            data_dict: Diccionario {nombre_hoja: DataFrame}
            patient_id: ID del paciente
            exercise: Tipo de ejercicio

        Returns:
            Path del archivo exportado o None si falla
        """
        try:
            filename = self.generate_filename(patient_id, exercise, "full_report", "xlsx")
            filepath = self.results_dir / filename

            with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
                for sheet_name, df in data_dict.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

            logger.info(f"Datos exportados a Excel: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error exportando Excel: {str(e)}", exc_info=True)
            return None

    def list_sessions(self, patient_id: Optional[str] = None) -> List[Path]:
        """
        Lista archivos de sesiones disponibles.

        Args:
            patient_id: Filtrar por ID de paciente (opcional)

        Returns:
            Lista de rutas a archivos de sesión
        """
        try:
            pattern = f"{patient_id}_*_session_*.pkl" if patient_id else "*_session_*.pkl"
            sessions = list(self.processed_dir.glob(pattern))

            logger.debug(f"Encontradas {len(sessions)} sesiones")
            return sorted(sessions, key=lambda x: x.stat().st_mtime, reverse=True)

        except Exception as e:
            logger.error(f"Error listando sesiones: {str(e)}", exc_info=True)
            return []

    def list_results(self, patient_id: Optional[str] = None) -> List[Path]:
        """
        Lista archivos de resultados disponibles.

        Args:
            patient_id: Filtrar por ID de paciente (opcional)

        Returns:
            Lista de rutas a archivos de resultados
        """
        try:
            pattern = f"{patient_id}_*_results_*.json" if patient_id else "*_results_*.json"
            results = list(self.results_dir.glob(pattern))

            logger.debug(f"Encontrados {len(results)} resultados")
            return sorted(results, key=lambda x: x.stat().st_mtime, reverse=True)

        except Exception as e:
            logger.error(f"Error listando resultados: {str(e)}", exc_info=True)
            return []

    def backup_data(self, backup_dir: Optional[Path] = None) -> bool:
        """
        Crea backup de todos los datos.

        Args:
            backup_dir: Directorio de backup (por defecto: data/backups/)

        Returns:
            True si el backup fue exitoso
        """
        try:
            if backup_dir is None:
                backup_dir = Path(RAW_DATA_DIR).parent / "backups"

            backup_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"backup_{timestamp}"

            # Copiar directorios
            shutil.copytree(self.processed_dir, backup_path / "processed")
            shutil.copytree(self.results_dir, backup_path / "results")

            # Copiar base de datos si existe
            db_path = DATABASE_CONFIG["path"]
            if db_path.exists():
                shutil.copy2(db_path, backup_path / db_path.name)

            logger.info(f"Backup creado: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Error creando backup: {str(e)}", exc_info=True)
            return False

    def clean_old_files(self, days: int = 30) -> int:
        """
        Limpia archivos más antiguos que X días.

        Args:
            days: Días de antigüedad para eliminar

        Returns:
            Número de archivos eliminados
        """
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
            deleted_count = 0

            for directory in [self.processed_dir, self.results_dir]:
                for file in directory.glob("*"):
                    if file.is_file() and file.stat().st_mtime < cutoff_time:
                        file.unlink()
                        deleted_count += 1
                        logger.debug(f"Eliminado: {file}")

            logger.info(f"Limpieza completada: {deleted_count} archivos eliminados")
            return deleted_count

        except Exception as e:
            logger.error(f"Error limpiando archivos: {str(e)}", exc_info=True)
            return 0

    def get_file_info(self, filepath: Path) -> Dict[str, Any]:
        """
        Obtiene información sobre un archivo.

        Args:
            filepath: Ruta al archivo

        Returns:
            Diccionario con información del archivo
        """
        try:
            stat = filepath.stat()

            info = {
                'name': filepath.name,
                'path': str(filepath),
                'size_bytes': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'exists': filepath.exists()
            }

            return info

        except Exception as e:
            logger.error(f"Error obteniendo info de archivo: {str(e)}")
            return {}


# Instancia global del gestor
file_manager = FileManager()


# Funciones de conveniencia
def save_session(session_id: str, patient_id: str, exercise: str, data: Dict) -> Optional[Path]:
    """Guarda datos de sesión (función de conveniencia)."""
    return file_manager.save_session_data(session_id, patient_id, exercise, data)


def load_session(filepath: Path) -> Optional[Dict]:
    """Carga datos de sesión (función de conveniencia)."""
    return file_manager.load_session_data(filepath)


def export_csv(data: pd.DataFrame, patient_id: str, exercise: str) -> Optional[Path]:
    """Exporta a CSV (función de conveniencia)."""
    return file_manager.export_to_csv(data, patient_id, exercise)


def export_excel(data_dict: Dict[str, pd.DataFrame], patient_id: str, exercise: str) -> Optional[Path]:
    """Exporta a Excel (función de conveniencia)."""
    return file_manager.export_to_excel(data_dict, patient_id, exercise)
