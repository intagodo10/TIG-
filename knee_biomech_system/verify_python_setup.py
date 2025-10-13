"""
Script de verificación de entorno Python.

Verifica que la versión de Python y las dependencias
sean compatibles con OpenSim 4.5.
"""

import sys

print("=" * 70)
print(" VERIFICACIÓN DE ENTORNO PYTHON")
print("=" * 70)
print()

# ============================================================================
# VERIFICAR VERSIÓN DE PYTHON
# ============================================================================
print("🐍 1. Verificando versión de Python...")
print(f"   Versión instalada: Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
print(f"   Ruta: {sys.executable}")
print()

major, minor = sys.version_info[:2]

if major == 3 and 8 <= minor <= 10:
    print("   ✅ Versión PERFECTA para OpenSim 4.5")
    python_ok = True
elif major == 3 and minor == 11:
    print("   ⚠️ Python 3.11 puede funcionar, pero no es la recomendada")
    print("      Recomendación: Usa Python 3.10.11")
    python_ok = True
elif major == 3 and minor >= 12:
    print("   ❌ Python 3.12+ NO es compatible con OpenSim 4.5")
    print("      ACCIÓN REQUERIDA:")
    print("      1. Desinstala Python 3.12")
    print("      2. Instala Python 3.10.11 desde: https://python.org/downloads/release/python-31011/")
    python_ok = False
elif major == 3 and minor < 8:
    print("   ❌ Python 3.7 o menor es muy antiguo")
    print("      ACCIÓN REQUERIDA: Instala Python 3.10.11")
    python_ok = False
else:
    print(f"   ⚠️ Versión no probada: Python {major}.{minor}")
    python_ok = False

print()

# ============================================================================
# VERIFICAR PAQUETES CORE
# ============================================================================
print("📦 2. Verificando paquetes científicos core...")

core_packages = [
    ('numpy', 'NumPy'),
    ('scipy', 'SciPy'),
    ('pandas', 'Pandas'),
    ('sklearn', 'Scikit-learn')
]

all_core_installed = True

for package_name, display_name in core_packages:
    try:
        mod = __import__(package_name)
        version = getattr(mod, '__version__', 'unknown')
        print(f"   ✅ {display_name}: {version}")
    except ImportError:
        print(f"   ❌ {display_name}: NO instalado")
        all_core_installed = False

print()

# ============================================================================
# VERIFICAR PAQUETES DE INTERFAZ
# ============================================================================
print("🎨 3. Verificando paquetes de interfaz...")

ui_packages = [
    ('customtkinter', 'CustomTkinter'),
    ('PIL', 'Pillow'),
    ('matplotlib', 'Matplotlib')
]

all_ui_installed = True

for package_name, display_name in ui_packages:
    try:
        mod = __import__(package_name)
        version = getattr(mod, '__version__', 'unknown')
        print(f"   ✅ {display_name}: {version}")
    except ImportError:
        print(f"   ❌ {display_name}: NO instalado")
        all_ui_installed = False

print()

# ============================================================================
# VERIFICAR PAQUETES DE DATOS
# ============================================================================
print("📊 4. Verificando paquetes de manejo de datos...")

data_packages = [
    ('openpyxl', 'OpenPyXL (Excel)'),
    ('xlsxwriter', 'XlsxWriter'),
]

for package_name, display_name in data_packages:
    try:
        mod = __import__(package_name)
        version = getattr(mod, '__version__', 'unknown')
        print(f"   ✅ {display_name}: {version}")
    except ImportError:
        print(f"   ⚠️ {display_name}: NO instalado (opcional)")

print()

# ============================================================================
# VERIFICAR OPENSIM (CRÍTICO)
# ============================================================================
print("🦴 5. Verificando OpenSim 4.5...")

opensim_installed = False
try:
    import opensim
    version = getattr(opensim, '__version__', 'unknown')
    print(f"   ✅ OpenSim instalado: versión {version}")
    print(f"   ✅ ¡Excelente! Análisis IK/ID disponibles")
    opensim_installed = True
except ImportError:
    print("   ❌ OpenSim NO instalado")
    print()
    print("   IMPORTANTE: OpenSim es necesario para análisis completo")
    print()
    print("   ┌─────────────────────────────────────────────────────┐")
    print("   │  CÓMO INSTALAR OPENSIM 4.5                          │")
    print("   ├─────────────────────────────────────────────────────┤")
    print("   │  1. Descargar instalador oficial:                   │")
    print("   │     https://simtk.org/frs/?group_id=91              │")
    print("   │                                                      │")
    print("   │  2. Instalar OpenSim 4.5 (programa completo)        │")
    print("   │                                                      │")
    print("   │  3. Instalar paquete Python:                        │")
    print("   │     cd \"C:\\OpenSim 4.5\\sdk\\python\"              │")
    print("   │     python setup.py install                         │")
    print("   │                                                      │")
    print("   │  4. Verificar:                                      │")
    print("   │     python -c \"import opensim\"                     │")
    print("   └─────────────────────────────────────────────────────┘")
    print()
    print("   SIN OPENSIM: El sistema funcionará con limitaciones")
    print("   ✓ Adquisición de datos: SÍ")
    print("   ✓ Procesamiento de señales: SÍ")
    print("   ✗ Cinemática Inversa (IK): NO")
    print("   ✗ Dinámica Inversa (ID): NO")

print()

# ============================================================================
# VERIFICAR BLUETOOTH (OPCIONAL)
# ============================================================================
print("📡 6. Verificando soporte Bluetooth (opcional)...")

try:
    import bleak
    version = getattr(bleak, '__version__', 'unknown')
    print(f"   ✅ Bleak: {version}")
    print(f"   ✅ Conexión con sensores IMU Xsens DOT disponible")
except ImportError:
    print("   ⚠️ Bleak NO instalado")
    print("      Sin Bleak: No puedes conectar sensores IMU en tiempo real")
    print("      Para instalar: pip install bleak")

print()

# ============================================================================
# RESUMEN Y RECOMENDACIONES
# ============================================================================
print("=" * 70)
print(" RESUMEN")
print("=" * 70)
print()

# Evaluar estado general
issues = []
warnings = []

if not python_ok:
    issues.append("Versión de Python incompatible")

if not all_core_installed:
    issues.append("Faltan paquetes científicos core")

if not all_ui_installed:
    issues.append("Faltan paquetes de interfaz")

if not opensim_installed:
    warnings.append("OpenSim no instalado (funcionalidad limitada)")

# Mostrar resultado
if len(issues) == 0:
    print("✅ ESTADO: LISTO PARA USAR")
    print()
    if len(warnings) > 0:
        print("⚠️ ADVERTENCIAS:")
        for warning in warnings:
            print(f"   • {warning}")
        print()
    print("🚀 Puedes ejecutar el sistema con:")
    print("   python main.py")
else:
    print("❌ ESTADO: REQUIERE ATENCIÓN")
    print()
    print("🔧 PROBLEMAS DETECTADOS:")
    for issue in issues:
        print(f"   • {issue}")
    print()
    print("📋 ACCIONES REQUERIDAS:")
    print()

    if not python_ok:
        print("   1. INSTALAR PYTHON 3.10.11")
        print("      → Descargar: https://python.org/downloads/release/python-31011/")
        print("      → Marcar: 'Add Python to PATH'")
        print()

    if not all_core_installed or not all_ui_installed:
        print("   2. INSTALAR DEPENDENCIAS")
        print("      → Ejecutar: pip install -r requirements.txt")
        print()

    if not opensim_installed:
        print("   3. INSTALAR OPENSIM 4.5 (OPCIONAL pero recomendado)")
        print("      → Descargar instalador: https://simtk.org/frs/?group_id=91")
        print("      → Seguir instrucciones en: PYTHON_VERSION.md")
        print()

print()
print("=" * 70)
print()

# Exit code
if len(issues) > 0:
    print("⚠️ Hay problemas que deben resolverse antes de usar el sistema.")
    sys.exit(1)
else:
    print("✨ El entorno está correctamente configurado.")
    sys.exit(0)
