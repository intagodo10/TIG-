# 🐍 Guía de Versiones de Python para este Proyecto

## ⚠️ IMPORTANTE: Compatibilidad con OpenSim

Este proyecto requiere **OpenSim 4.5**, que tiene limitaciones específicas de versión de Python.

---

## ✅ Versiones Compatibles de Python

| Versión Python | OpenSim 4.5 | Otros Paquetes | Recomendación |
|----------------|-------------|----------------|---------------|
| **3.10.x** | ✅ Sí | ✅ Sí | **⭐ RECOMENDADA** |
| **3.9.x** | ✅ Sí | ✅ Sí | ✅ Buena opción |
| **3.8.x** | ✅ Sí | ✅ Sí | ✅ Funciona bien |
| **3.11.x** | ⚠️ Limitado | ✅ Sí | ⚠️ Puede funcionar |
| **3.12+** | ❌ NO | ✅ Sí | ❌ NO compatible |
| **3.7 o menor** | ❌ NO | ⚠️ Limitado | ❌ NO compatible |

---

## 🎯 Versión Recomendada: Python 3.10.11

**¿Por qué Python 3.10?**

1. ✅ **Totalmente compatible con OpenSim 4.5**
2. ✅ **Compatible con todos los paquetes científicos**
3. ✅ **Estable y bien probada**
4. ✅ **Soporte a largo plazo**
5. ✅ **Mejor balance compatibilidad/características**

---

## 📥 Cómo Instalar Python 3.10

### Windows

#### Opción 1: Desde python.org (Recomendada)

1. **Descargar Python 3.10.11:**
   - Ir a: https://www.python.org/downloads/release/python-31011/
   - Descargar: "Windows installer (64-bit)"

2. **Instalar:**
   - ✅ Marcar: "Add Python 3.10 to PATH"
   - ✅ Seleccionar: "Install for all users" (opcional)
   - Clic en "Install Now"

3. **Verificar instalación:**
   ```bash
   python --version
   # Debe mostrar: Python 3.10.11
   ```

#### Opción 2: Usando pyenv-win (Para múltiples versiones)

```bash
# Instalar pyenv-win
pip install pyenv-win --target $HOME/.pyenv

# Instalar Python 3.10.11
pyenv install 3.10.11

# Establecer como versión global
pyenv global 3.10.11

# Verificar
python --version
```

---

## 🔧 Configuración del Entorno

### Paso 1: Crear Entorno Virtual con Python 3.10

```bash
# Navegar al proyecto
cd "c:\Dev\TESIS INGRID\knee_biomech_system"

# Crear entorno virtual con Python 3.10
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Verificar versión dentro del entorno
python --version
# Debe mostrar: Python 3.10.x
```

### Paso 2: Actualizar pip

```bash
python -m pip install --upgrade pip
```

### Paso 3: Instalar Dependencias (Sin OpenSim primero)

```bash
# Instalar todo excepto OpenSim
pip install numpy scipy pandas scikit-learn
pip install pykalman
pip install bleak pyserial openpyxl
pip install customtkinter pillow tkinterdnd2
pip install matplotlib seaborn plotly
pip install reportlab xlsxwriter jinja2
pip install sqlalchemy python-dateutil pytz tqdm
```

---

## 🦴 Instalación de OpenSim 4.5

OpenSim **NO** se instala correctamente con `pip install opensim` en la mayoría de casos.

### Método Correcto (Windows):

#### Paso 1: Descargar OpenSim

1. Ir a: https://simtk.org/frs/?group_id=91
2. Buscar: **OpenSim 4.5 - Windows**
3. Descargar: `OpenSim-4.5-win64.exe` (~500 MB)

#### Paso 2: Instalar OpenSim

1. Ejecutar el instalador
2. Seguir las instrucciones
3. Ruta de instalación típica: `C:\OpenSim 4.5\`

#### Paso 3: Instalar el Paquete Python de OpenSim

**IMPORTANTE:** Debes tener el entorno virtual activado

```bash
# Activar entorno virtual
venv\Scripts\activate

# Navegar al directorio de Python de OpenSim
cd "C:\OpenSim 4.5\sdk\python"

# Instalar el paquete
python setup.py install

# Volver al proyecto
cd "c:\Dev\TESIS INGRID\knee_biomech_system"
```

#### Paso 4: Verificar Instalación

```bash
python -c "import opensim; print(opensim.__version__)"
# Debe mostrar: 4.5 (o similar)
```

---

## ⚡ Instalación Rápida (Script)

Guarda esto como `setup_environment.bat`:

```batch
@echo off
echo ================================
echo CONFIGURACION DEL ENTORNO
echo ================================
echo.

echo Verificando version de Python...
python --version
echo.

echo Creando entorno virtual...
python -m venv venv
echo.

echo Activando entorno virtual...
call venv\Scripts\activate
echo.

echo Actualizando pip...
python -m pip install --upgrade pip
echo.

echo Instalando dependencias...
pip install -r requirements.txt
echo.

echo ================================
echo INSTALACION COMPLETA
echo ================================
echo.
echo IMPORTANTE: Instala OpenSim manualmente desde:
echo https://simtk.org/frs/?group_id=91
echo.
echo Luego ejecuta:
echo   cd "C:\OpenSim 4.5\sdk\python"
echo   python setup.py install
echo.
pause
```

---

## 🚨 Problemas Comunes y Soluciones

### Problema 1: "Python 3.12 instalado, necesito 3.10"

**Solución:**

1. **Opción A:** Desinstalar Python 3.12 e instalar 3.10
   - Panel de Control → Desinstalar programas
   - Buscar "Python 3.12" y desinstalar
   - Instalar Python 3.10.11

2. **Opción B:** Usar pyenv-win para gestionar múltiples versiones

### Problema 2: "pip install opensim" falla

**Solución:**

NO uses `pip install opensim`. Sigue el método manual descrito arriba.

Errores comunes:
- `error: Microsoft Visual C++ 14.0 is required`
- `Could not build wheels for opensim`
- `Failed to build opensim`

**Todos se resuelven instalando OpenSim desde el instalador oficial.**

### Problema 3: "ImportError: DLL load failed"

**Solución:**

Instala **Visual C++ Redistributable**:
- Descargar: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Instalar
- Reiniciar PC

### Problema 4: "ModuleNotFoundError: No module named 'opensim'"

**Causas posibles:**

1. **OpenSim no instalado correctamente**
   - Verificar que OpenSim 4.5 esté instalado
   - Verificar que el paquete Python esté instalado

2. **Entorno virtual no activado**
   ```bash
   venv\Scripts\activate
   ```

3. **Instalado en Python diferente**
   - Verificar: `python --version`
   - Debe ser 3.10.x

---

## ✅ Verificación Completa

Script de verificación:

```python
# guardar como: verify_python_setup.py

import sys

print("=" * 60)
print("VERIFICACIÓN DE ENTORNO")
print("=" * 60)
print()

# Verificar versión de Python
print(f"Python version: {sys.version}")
major, minor = sys.version_info[:2]

if (major == 3 and 8 <= minor <= 11):
    print("✅ Versión de Python compatible con OpenSim")
elif (major == 3 and minor == 12):
    print("❌ Python 3.12 NO es compatible con OpenSim 4.5")
    print("   Instala Python 3.10.11")
else:
    print(f"⚠️ Versión no probada: Python {major}.{minor}")

print()

# Verificar paquetes
packages = [
    'numpy', 'scipy', 'pandas', 'sklearn',
    'matplotlib', 'customtkinter', 'openpyxl'
]

for package in packages:
    try:
        mod = __import__(package)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✅ {package}: {version}")
    except ImportError:
        print(f"❌ {package}: NO instalado")

print()

# Verificar OpenSim (especial)
try:
    import opensim
    print(f"✅ opensim: {opensim.__version__}")
    print("   ¡OpenSim instalado correctamente!")
except ImportError:
    print("⚠️ opensim: NO instalado")
    print("   El sistema funcionará sin análisis IK/ID")
    print("   Instala desde: https://simtk.org/frs/?group_id=91")

print()
print("=" * 60)
```

Ejecutar:
```bash
python verify_python_setup.py
```

---

## 📊 Resumen de Instalación

```
┌─────────────────────────────────────┐
│  PASO 1: Instalar Python 3.10.11   │
│  https://python.org/downloads       │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  PASO 2: Crear entorno virtual      │
│  python -m venv venv                │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  PASO 3: Instalar dependencias      │
│  pip install -r requirements.txt    │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  PASO 4: Instalar OpenSim 4.5       │
│  Descarga instalador oficial        │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  PASO 5: Instalar paquete Python    │
│  cd "C:\OpenSim 4.5\sdk\python"     │
│  python setup.py install            │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  ✅ LISTO PARA USAR                 │
│  python main.py                     │
└─────────────────────────────────────┘
```

---

## 🎯 Recomendación Final

**Para este proyecto específico:**

1. ✅ Usa **Python 3.10.11** (mejor compatibilidad)
2. ✅ Instala OpenSim desde el **instalador oficial**
3. ✅ Usa **entorno virtual** para aislar dependencias
4. ✅ Verifica instalación con `verify_python_setup.py`

**El sistema funcionará parcialmente sin OpenSim**, pero necesitarás OpenSim para:
- Cinemática Inversa (IK)
- Dinámica Inversa (ID)
- Análisis musculoesquelético completo

---

## 📞 Soporte

Si tienes problemas de instalación:

1. Ejecuta: `python verify_python_setup.py`
2. Revisa los logs en: `logs/system.log`
3. Consulta documentación oficial de OpenSim: https://simtk-confluence.stanford.edu/

---

**Última actualización:** 2025-01-13
**Versión recomendada:** Python 3.10.11 + OpenSim 4.5
