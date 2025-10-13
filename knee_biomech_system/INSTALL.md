# Guía de Instalación Detallada
## Sistema de Análisis Biomecánico de Rodilla

---

## Tabla de Contenidos
1. [Requisitos Previos](#requisitos-previos)
2. [Instalación Paso a Paso](#instalación-paso-a-paso)
3. [Configuración de OpenSim](#configuración-de-opensim)
4. [Configuración de Sensores](#configuración-de-sensores)
5. [Verificación de Instalación](#verificación-de-instalación)
6. [Solución de Problemas](#solución-de-problemas)

---

## Requisitos Previos

### Hardware Mínimo
- **Procesador:** Intel Core i5 o equivalente (mínimo)
- **RAM:** 8 GB (recomendado: 16 GB)
- **Almacenamiento:** 10 GB de espacio libre
- **Bluetooth:** 4.0 o superior
- **Sistema Operativo:** Windows 10/11 (64-bit)

### Hardware Específico del Proyecto
- **7 sensores Xsens DOT** con baterías cargadas
- **Plataforma de fuerza Valkyria** (Involution)
- **PC con Microsoft Excel** (para exportar datos de Valkyria)

---

## Instalación Paso a Paso

### Paso 1: Instalar Python

⚠️ **IMPORTANTE:** Este proyecto requiere **Python 3.10.11** (recomendado)

OpenSim 4.5 **NO es compatible con Python 3.12+**

**Versiones compatibles:** Python 3.8, 3.9, 3.10 o 3.11

1. **Descargar Python 3.10.11 (RECOMENDADO):**
   - Ir a: https://www.python.org/downloads/release/python-31011/
   - Descargar: "Windows installer (64-bit)"

2. **Durante la instalación:**
   - ✅ **MARCAR:** "Add Python 3.10 to PATH"
   - ✅ Instalar para todos los usuarios (opcional)

3. **Verificar instalación:**
   ```bash
   python --version
   # Debe mostrar: Python 3.10.11
   ```

4. **Si tienes Python 3.12 instalado:**
   - Desinstalar Python 3.12
   - Instalar Python 3.10.11
   - Ver [PYTHON_VERSION.md](PYTHON_VERSION.md) para más detalles

### Paso 2: Instalar Git (Opcional)

Si vas a clonar el repositorio:

1. Descargar Git desde: https://git-scm.com/download/win

2. Instalar con opciones por defecto

3. Verificar:
   ```bash
   git --version
   ```

### Paso 3: Obtener el Código

**Opción A: Clonar con Git**
```bash
git clone <repository-url>
cd knee_biomech_system
```

**Opción B: Descargar ZIP**
1. Descargar archivo ZIP del proyecto
2. Extraer en ubicación deseada
3. Abrir terminal en la carpeta extraída

### Paso 4: Crear Entorno Virtual

Es **altamente recomendado** usar un entorno virtual:

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate

# Debes ver (venv) al inicio de la línea de comandos
```

### Paso 5: Instalar Dependencias

```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias del proyecto
pip install -r requirements.txt
```

**Nota:** La instalación puede tomar 5-10 minutos dependiendo de la conexión a internet.

---

## Configuración de OpenSim

### Paso 1: Descargar OpenSim

1. Ir a: https://simtk.org/frs/?group_id=91

2. Descargar **OpenSim 4.5** para Windows (64-bit)

3. Ejecutar el instalador y seguir las instrucciones

4. Ruta de instalación típica:
   ```
   C:\OpenSim 4.5\
   ```

### Paso 2: Instalar Paquete Python de OpenSim

**Método 1: Desde instalación de OpenSim**
```bash
# Navegar al directorio de instalación
cd "C:\OpenSim 4.5\sdk\python"

# Instalar el paquete
python setup.py install
```

**Método 2: Pip (si está disponible)**
```bash
pip install opensim
```

### Paso 3: Verificar Instalación de OpenSim

```bash
python -c "import opensim; print(opensim.__version__)"
# Debe mostrar: 4.5 (o similar)
```

### Paso 4: Descargar Modelos Musculoesqueléticos

1. Los modelos vienen con OpenSim en:
   ```
   C:\OpenSim 4.5\Models\
   ```

2. Copiar el modelo **Gait2392** al proyecto:
   ```bash
   # Crear directorio de modelos si no existe
   mkdir data\models

   # Copiar modelo (ajustar ruta según instalación)
   copy "C:\OpenSim 4.5\Models\Gait2392_Simbody\gait2392_simbody.osim" data\models\
   ```

### Paso 5: Configurar Rutas en el Proyecto

Editar `config/settings.py`:

```python
OPENSIM_CONFIG = {
    "model_file": "gait2392_simbody.osim",
    "model_path": MODELS_DIR / "gait2392_simbody.osim",
    # ... resto de configuración
}
```

---

## Configuración de Sensores

### Sensores Xsens DOT

#### Preparación

1. **Cargar baterías:**
   - Conectar cada sensor a cargador USB
   - LED parpadeará durante carga
   - LED fijo indica carga completa

2. **Actualizar firmware (si es necesario):**
   - Descargar app Xsens DOT desde Play Store o App Store
   - Conectar sensores uno por uno
   - Seguir instrucciones de actualización

#### Configuración Bluetooth en PC

1. **Activar Bluetooth:**
   - Ir a Configuración > Dispositivos > Bluetooth
   - Activar Bluetooth

2. **No emparejar manualmente:**
   - La aplicación detectará sensores automáticamente
   - NO usar el emparejamiento de Windows

#### Etiquetado de Sensores

Se recomienda etiquetar físicamente cada sensor:

| Ubicación | Etiqueta Sugerida |
|-----------|------------------|
| Pelvis | PELVIS |
| Fémur Derecho | FEMUR_R |
| Fémur Izquierdo | FEMUR_L |
| Tibia Derecha | TIBIA_R |
| Tibia Izquierda | TIBIA_L |
| Pie Derecho | PIE_R |
| Pie Izquierdo | PIE_L |

### Plataforma de Fuerza Valkyria

#### Configuración de Hardware

1. **Ubicación:**
   - Colocar en superficie plana y nivelada
   - Verificar con nivel de burbuja
   - Asegurar que esté estable

2. **Conexión:**
   - Conectar cable USB a PC con software Valkyria
   - Encender plataforma

3. **Calibración:**
   - Seguir procedimiento del manual de Valkyria
   - Realizar tara (cero) sin peso sobre la plataforma

#### Exportación de Datos

1. **Durante captura:**
   - Usar software Valkyria para grabar
   - Sincronizar inicio con captura de IMUs (manual)

2. **Después de captura:**
   - En software Valkyria: File > Export > Excel
   - Asegurar que incluya columnas:
     - Time (s)
     - Fx (N), Fy (N), Fz (N)
     - Mx (Nm), My (Nm), Mz (Nm)

3. **Guardar archivo:**
   - Nombrar descriptivamente: `PatientID_Exercise_Date.xlsx`
   - Guardar en `data/raw/`

---

## Verificación de Instalación

### Test Completo

Ejecutar script de verificación:

```bash
python -c "
import sys
print('Python:', sys.version)

import numpy
print('NumPy:', numpy.__version__)

import pandas
print('Pandas:', pandas.__version__)

import customtkinter
print('CustomTkinter:', customtkinter.__version__)

import opensim
print('OpenSim:', opensim.__version__)

print('\n✅ Todas las dependencias instaladas correctamente')
"
```

### Probar la Aplicación

```bash
python main.py
```

Si todo está correcto, deberías ver:
- Ventana principal con tema oscuro
- Título del sistema
- Botones funcionales

### Probar Importación de Valkyria

1. En la aplicación, clic en "Probar Importación de Valkyria"
2. Seleccionar un archivo Excel de ejemplo
3. Verificar que muestre estadísticas correctamente

---

## Solución de Problemas

### Error: "Python no reconocido"

**Causa:** Python no está en PATH

**Solución:**
1. Reinstalar Python marcando "Add Python to PATH"
2. O añadir manualmente:
   - Buscar "Variables de entorno"
   - Añadir a PATH: `C:\PythonXX\` y `C:\PythonXX\Scripts\`

### Error: "No module named 'opensim'"

**Causa:** OpenSim Python no instalado correctamente

**Solución:**
```bash
# Método 1
cd "C:\OpenSim 4.5\sdk\python"
python setup.py install

# Método 2
pip install opensim
```

### Error: "No module named 'customtkinter'"

**Causa:** CustomTkinter no instalado

**Solución:**
```bash
pip install customtkinter
```

### Error: Bluetooth no detecta sensores

**Posibles causas y soluciones:**

1. **Sensores apagados:**
   - Presionar botón de encendido
   - LED debe parpadear (azul)

2. **Bluetooth desactivado:**
   - Activar en Configuración de Windows
   - Verificar que adaptador funcione

3. **Sensores conectados a otro dispositivo:**
   - Apagar/encender sensores
   - Desconectar de otros dispositivos

4. **Driver Bluetooth desactualizado:**
   - Actualizar drivers desde Administrador de Dispositivos

### Error: Excel no se puede importar

**Verificar:**
1. Archivo tiene extensión `.xlsx` o `.xls`
2. Archivo no está abierto en Excel
3. Columnas tienen nombres correctos
4. Archivo no está corrupto

### Error: OpenSim model not found

**Solución:**
1. Verificar que archivo `.osim` existe en `data/models/`
2. Verificar ruta en `config/settings.py`
3. Copiar modelo desde instalación de OpenSim

### Aplicación se congela

**Posibles causas:**

1. **Datos muy grandes:**
   - Reducir duración de captura
   - Usar downsampling

2. **RAM insuficiente:**
   - Cerrar otras aplicaciones
   - Aumentar RAM del sistema

3. **Procesamiento bloqueante:**
   - Reportar bug al equipo de desarrollo

---

## Configuración Avanzada

### Personalizar Parámetros

Editar archivos en `config/`:

- **settings.py:** Parámetros generales
- **ui_theme.py:** Colores y estilos
- **opensim_config.py:** Configuración de OpenSim

### Configurar Logging

En `config/settings.py`:

```python
LOGGING_CONFIG = {
    "level": "DEBUG",  # Cambiar a DEBUG para más detalle
    "file_enabled": True,
    "file_path": LOGS_DIR / "system.log"
}
```

### Cambiar Frecuencia de Sincronización

En `config/settings.py`:

```python
SYNC_CONFIG = {
    "target_frequency": 100,  # Cambiar según necesidad
    # ...
}
```

---

## Desinstalación

Si necesitas desinstalar:

```bash
# Desactivar entorno virtual
deactivate

# Eliminar entorno virtual
rmdir /s /q venv

# Eliminar archivos del proyecto (opcional)
# Ten cuidado de respaldar tus datos antes

# Desinstalar OpenSim
# Usar desinstalador de Windows
```

---

## Próximos Pasos

Después de instalar:

1. ✅ Leer [README.md](README.md) para uso del sistema
2. ✅ Revisar [ejemplos] si están disponibles
3. ✅ Realizar capturas de prueba
4. ✅ Familiarizarse con la interfaz

---

## Soporte

Si encuentras problemas:

1. Revisar logs en `logs/system.log`
2. Consultar sección de [Solución de Problemas](#solución-de-problemas)
3. Contactar al equipo de desarrollo
4. Crear issue en repositorio (si aplica)

---

**Versión del documento:** 1.0
**Última actualización:** 2025

---

¡Instalación completa! 🎉
