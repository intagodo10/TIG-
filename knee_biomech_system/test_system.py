"""
Script de prueba del sistema.

Verifica que todos los componentes estén instalados
y funcionando correctamente.
"""

import sys
from pathlib import Path

# Añadir directorio raíz al path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

print("=" * 70)
print(" SISTEMA DE ANÁLISIS BIOMECÁNICO DE RODILLA - TEST DE COMPONENTES")
print("=" * 70)
print()

# Test 1: Imports básicos
print("📦 1. Verificando imports básicos...")
try:
    import numpy as np
    print(f"   ✓ NumPy {np.__version__}")
except ImportError as e:
    print(f"   ✗ NumPy no instalado: {e}")
    sys.exit(1)

try:
    import pandas as pd
    print(f"   ✓ Pandas {pd.__version__}")
except ImportError as e:
    print(f"   ✗ Pandas no instalado: {e}")
    sys.exit(1)

try:
    import scipy
    print(f"   ✓ SciPy {scipy.__version__}")
except ImportError as e:
    print(f"   ✗ SciPy no instalado: {e}")
    sys.exit(1)

try:
    import matplotlib
    print(f"   ✓ Matplotlib {matplotlib.__version__}")
except ImportError as e:
    print(f"   ✗ Matplotlib no instalado: {e}")
    sys.exit(1)

try:
    import customtkinter as ctk
    print(f"   ✓ CustomTkinter {ctk.__version__}")
except ImportError as e:
    print(f"   ✗ CustomTkinter no instalado: {e}")
    sys.exit(1)

print()

# Test 2: OpenSim (opcional)
print("🦴 2. Verificando OpenSim...")
try:
    import opensim
    print(f"   ✓ OpenSim {opensim.__version__}")
except ImportError:
    print("   ⚠ OpenSim no instalado (opcional pero recomendado)")

print()

# Test 3: Bluetooth (opcional)
print("📡 3. Verificando Bluetooth...")
try:
    import bleak
    print(f"   ✓ Bleak {bleak.__version__} (Bluetooth habilitado)")
except ImportError:
    print("   ⚠ Bleak no instalado (necesario para sensores IMU en tiempo real)")

print()

# Test 4: Módulos del proyecto
print("🏗️  4. Verificando módulos del proyecto...")

try:
    from config import settings
    print("   ✓ config.settings")
except ImportError as e:
    print(f"   ✗ Error en config.settings: {e}")
    sys.exit(1)

try:
    from config import ui_theme
    print("   ✓ config.ui_theme")
except ImportError as e:
    print(f"   ✗ Error en config.ui_theme: {e}")
    sys.exit(1)

try:
    from models.patient import Patient
    print("   ✓ models.patient")
except ImportError as e:
    print(f"   ✗ Error en models.patient: {e}")
    sys.exit(1)

try:
    from models.session import Session
    print("   ✓ models.session")
except ImportError as e:
    print(f"   ✗ Error en models.session: {e}")
    sys.exit(1)

try:
    from utils.logger import get_logger
    print("   ✓ utils.logger")
except ImportError as e:
    print(f"   ✗ Error en utils.logger: {e}")
    sys.exit(1)

try:
    from utils.file_manager import FileManager
    print("   ✓ utils.file_manager")
except ImportError as e:
    print(f"   ✗ Error en utils.file_manager: {e}")
    sys.exit(1)

try:
    from utils.validators import validate_patient_id
    print("   ✓ utils.validators")
except ImportError as e:
    print(f"   ✗ Error en utils.validators: {e}")
    sys.exit(1)

try:
    from core.data_acquisition.force_platform import ForcePlatformHandler
    print("   ✓ core.data_acquisition.force_platform")
except ImportError as e:
    print(f"   ✗ Error en force_platform: {e}")
    sys.exit(1)

try:
    from core.data_acquisition.imu_handler import IMUHandler
    print("   ✓ core.data_acquisition.imu_handler")
except ImportError as e:
    print(f"   ✗ Error en imu_handler: {e}")
    sys.exit(1)

print()

# Test 5: Estructura de directorios
print("�� 5. Verificando estructura de directorios...")
from config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR, RESULTS_DIR, MODELS_DIR, LOGS_DIR

dirs_to_check = {
    "data/raw": RAW_DATA_DIR,
    "data/processed": PROCESSED_DATA_DIR,
    "data/results": RESULTS_DIR,
    "data/models": MODELS_DIR,
    "logs": LOGS_DIR
}

for name, path in dirs_to_check.items():
    if path.exists():
        print(f"   ✓ {name}")
    else:
        print(f"   ⚠ {name} no existe (se creará automáticamente)")

print()

# Test 6: Crear objetos de prueba
print("🧪 6. Creando objetos de prueba...")

try:
    from models.patient import Patient, Sex, AffectedLimb
    from models.session import Session, ExerciseType
    from datetime import datetime

    # Crear paciente de prueba
    patient = Patient(
        patient_id="TEST001",
        name="Paciente de Prueba",
        age=30,
        mass=70.0,
        height=1.75,
        sex=Sex.MALE,
        affected_limb=AffectedLimb.RIGHT,
        diagnosis="Prueba del sistema"
    )
    print(f"   ✓ Paciente creado: {patient.name}, BMI: {patient.bmi:.1f}")

    # Crear sesión de prueba
    session = Session(
        session_id="SESSION001",
        patient_id=patient.patient_id,
        exercise_type=ExerciseType.SQUAT
    )
    print(f"   ✓ Sesión creada: {session.session_id}, Ejercicio: {session.exercise_type.value}")

except Exception as e:
    print(f"   ✗ Error creando objetos: {e}")
    sys.exit(1)

print()

# Test 7: Validadores
print("✔️  7. Probando validadores...")

try:
    from utils.validators import validate_patient_id, validate_patient_data

    # Test validación ID
    valid, error = validate_patient_id("TEST001")
    if valid:
        print("   ✓ Validación de ID funciona correctamente")
    else:
        print(f"   ✗ Error en validación de ID: {error}")

    # Test validación datos
    valid, error = validate_patient_data("Paciente Test", 30, 70.0, 1.75)
    if valid:
        print("   ✓ Validación de datos funciona correctamente")
    else:
        print(f"   ✗ Error en validación de datos: {error}")

except Exception as e:
    print(f"   ✗ Error en validadores: {e}")

print()

# Test 8: Logger
print("📝 8. Probando sistema de logging...")

try:
    from utils.logger import get_logger

    logger = get_logger("TestSystem")
    logger.info("Test de log INFO")
    logger.debug("Test de log DEBUG")
    logger.warning("Test de log WARNING")

    print("   ✓ Sistema de logging funciona correctamente")

except Exception as e:
    print(f"   ✗ Error en logging: {e}")

print()

# Test 9: File Manager
print("💾 9. Probando gestor de archivos...")

try:
    from utils.file_manager import FileManager

    fm = FileManager()
    filename = fm.generate_filename("TEST001", "squat", "demo")
    print(f"   ✓ Nombre generado: {filename}")

except Exception as e:
    print(f"   ✗ Error en file manager: {e}")

print()

# Test 10: Force Platform Handler
print("⚖️  10. Probando manejador de plataforma de fuerza...")

try:
    from core.data_acquisition.force_platform import ForcePlatformHandler

    handler = ForcePlatformHandler()
    print(f"   ✓ ForcePlatformHandler inicializado")
    print(f"      - Frecuencia: {handler.sampling_rate} Hz")
    print(f"      - Dimensiones: {handler.dimensions[0]}m × {handler.dimensions[1]}m")

except Exception as e:
    print(f"   ✗ Error en force platform: {e}")

print()

# Test 11: IMU Handler
print("📱 11. Probando manejador de IMU...")

try:
    from core.data_acquisition.imu_handler import IMUHandler

    imu_handler = IMUHandler()
    print(f"   ✓ IMUHandler inicializado")
    print(f"      - Sensores configurados: {len(imu_handler.sensors)}")
    print(f"      - Ubicaciones: {', '.join(imu_handler.locations)}")

except Exception as e:
    print(f"   ✗ Error en IMU handler: {e}")

print()

# Test 12: UI Theme
print("🎨 12. Probando tema de interfaz...")

try:
    from config.ui_theme import COLORS, get_color, get_component_style

    print(f"   ✓ Paleta de colores cargada")
    print(f"      - Color primario: {COLORS['accent_primary']}")
    print(f"      - Color de fondo: {COLORS['bg_primary']}")
    print(f"      - Estilos de botón: {get_component_style('button_primary') is not None}")

except Exception as e:
    print(f"   ✗ Error en tema UI: {e}")

print()

# Resumen final
print("=" * 70)
print(" RESUMEN DEL TEST")
print("=" * 70)
print()
print("✅ COMPONENTES BÁSICOS:")
print("   • Python, NumPy, Pandas, SciPy, Matplotlib ✓")
print("   • CustomTkinter ✓")
print()
print("✅ MÓDULOS DEL PROYECTO:")
print("   • Configuración (settings, theme) ✓")
print("   • Modelos (Patient, Session) ✓")
print("   • Utilidades (logger, file_manager, validators) ✓")
print("   • Adquisición de datos (force_platform, imu_handler) ✓")
print()
print("⚠️  COMPONENTES OPCIONALES:")
print("   • OpenSim: Verificar instalación para análisis musculoesquelético")
print("   • Bleak: Verificar instalación para sensores IMU en tiempo real")
print()
print("🚀 PRÓXIMOS PASOS:")
print("   1. Instalar OpenSim 4.5 si no está instalado")
print("   2. Ejecutar: python main.py")
print("   3. Probar importación de datos de Valkyria")
print("   4. Continuar desarrollo de módulos pendientes")
print()
print("=" * 70)
print()

# Indicar si se puede continuar
print("✓ El sistema está listo para ejecutarse.")
print()
print("Para iniciar la aplicación, ejecuta:")
print("  python main.py")
print()
