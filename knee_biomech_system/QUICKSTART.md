# 🚀 Inicio Rápido - Sistema de Análisis Biomecánico

Esta guía te permite poner el sistema en funcionamiento en menos de 10 minutos.

---

## ⚡ Pasos Rápidos

### 1. Verificar Python

```bash
python --version
# Debe mostrar Python 3.8 o superior
```

### 2. Instalar Dependencias

```bash
cd c:\Dev\TESIS INGRID\knee_biomech_system
pip install -r requirements.txt
```

⏱️ Tiempo estimado: 3-5 minutos

### 3. Probar el Sistema

```bash
python test_system.py
```

Esto verificará que todos los componentes estén instalados correctamente.

### 4. Generar Datos de Ejemplo

```bash
python generate_sample_data.py
```

Esto creará archivos Excel de ejemplo para probar sin sensores físicos.

### 5. Ejecutar la Aplicación

```bash
python main.py
```

---

## 🎯 Primera Prueba

Una vez que la aplicación esté abierta:

1. **Clic en "🧪 Probar Importación de Valkyria"**

2. **Navegar a:** `data/raw/ejemplos/`

3. **Seleccionar:** `ejemplo_sentadilla_70kg.xlsx`

4. **Ver resultados** en la ventana que aparece

---

## 📊 ¿Qué Puedes Hacer Ahora?

### ✅ Funcionalidades Disponibles

- ✓ Importar datos de plataforma Valkyria desde Excel
- ✓ Calibrar datos (corrección de cero)
- ✓ Calcular estadísticas básicas
- ✓ Calcular Centro de Presión (COP)
- ✓ Detectar eventos de contacto
- ✓ Calcular tasa de carga
- ✓ Calcular impulso
- ✓ Exportar datos procesados

### 🚧 En Desarrollo

- ⏳ Conexión con sensores IMU Xsens DOT
- ⏳ Sincronización de datos IMU + Fuerza
- ⏳ Análisis con OpenSim (IK/ID)
- ⏳ Cálculo de métricas completas
- ⏳ Sistema de alertas
- ⏳ Interfaz gráfica completa
- ⏳ Generación de reportes

---

## 🛠️ Estructura del Código

```
knee_biomech_system/
│
├── main.py                    # ⭐ Ejecutar este archivo
├── test_system.py            # 🧪 Probar instalación
├── generate_sample_data.py   # 📊 Crear datos de ejemplo
│
├── config/                    # ⚙️ Configuración
│   ├── settings.py           # Parámetros del sistema
│   └── ui_theme.py           # Tema de interfaz
│
├── models/                    # 📦 Modelos de datos
│   ├── patient.py            # Modelo de paciente
│   └── session.py            # Modelo de sesión
│
├── core/                      # 🧠 Lógica principal
│   └── data_acquisition/
│       ├── force_platform.py # Manejo de Valkyria ✅
│       └── imu_handler.py    # Manejo de Xsens DOT 🚧
│
├── utils/                     # 🔧 Utilidades
│   ├── logger.py             # Sistema de logging
│   ├── file_manager.py       # Gestión de archivos
│   └── validators.py         # Validadores
│
└── data/                      # 💾 Datos
    ├── raw/ejemplos/         # Datos de ejemplo ⭐
    ├── processed/            # Datos procesados
    └── results/              # Resultados
```

---

## 📝 Ejemplo de Código

### Importar y Procesar Datos de Valkyria

```python
from core.data_acquisition.force_platform import ForcePlatformHandler

# Crear handler
handler = ForcePlatformHandler()

# Importar datos
handler.import_from_excel("data/raw/ejemplos/ejemplo_sentadilla_70kg.xlsx")

# Calibrar (tara)
handler.calibrate_zero(duration=1.0)

# Obtener estadísticas
stats = handler.get_summary_stats()
print(f"Duración: {stats['duration']:.2f}s")
print(f"Pico Fz: {stats['peak_fz']:.2f} N")

# Calcular COP
cop_x, cop_y = handler.calculate_cop()

# Detectar eventos
contact_idx, liftoff_idx = handler.detect_contact_events(threshold=20.0)
print(f"Contactos detectados: {len(contact_idx)}")

# Calcular impulso
impulse = handler.calculate_impulse()
print(f"Impulso Fz: {impulse['fz']:.2f} Ns")

# Exportar datos procesados
handler.export_processed_data("data/processed/output.csv")
```

### Crear un Paciente

```python
from models.patient import Patient, Sex, AffectedLimb

patient = Patient(
    patient_id="P001",
    name="Juan Pérez",
    age=30,
    mass=70.0,  # kg
    height=1.75,  # metros
    sex=Sex.MALE,
    affected_limb=AffectedLimb.RIGHT,
    diagnosis="Dolor de rodilla"
)

print(f"BMI: {patient.bmi:.1f} kg/m²")
print(f"Peso corporal: {patient.body_weight_newtons:.1f} N")
```

### Crear una Sesión

```python
from models.session import Session, ExerciseType

session = Session(
    session_id="S001",
    patient_id="P001",
    exercise_type=ExerciseType.SQUAT
)

session.start_recording()
# ... captura de datos ...
session.stop_recording()

print(f"Duración: {session.duration:.2f}s")
print(f"Estado: {session.status.value}")
```

---

## 🎓 Siguiente Nivel

### Para Continuar el Desarrollo

1. **Lee:** [PROJECT_STATUS.md](PROJECT_STATUS.md) para ver componentes pendientes

2. **Implementa:** El siguiente módulo en la lista de prioridades

3. **Prueba:** Crea tests para el módulo implementado

4. **Documenta:** Actualiza README y PROJECT_STATUS

### Módulos Prioritarios a Implementar

1. **synchronizer.py** - Sincronización IMU + Fuerza
2. **signal_processing.py** - Filtrado de señales
3. **opensim_interface.py** - Integración con OpenSim
4. **metrics_calculator.py** - Cálculo de métricas

---

## 📚 Documentación Completa

- **[README.md](README.md)** - Documentación completa del sistema
- **[INSTALL.md](INSTALL.md)** - Guía detallada de instalación
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Estado del proyecto
- **Este archivo (QUICKSTART.md)** - Inicio rápido

---

## ❓ Problemas Comunes

### "ModuleNotFoundError: No module named 'customtkinter'"

```bash
pip install customtkinter
```

### "ModuleNotFoundError: No module named 'openpyxl'"

```bash
pip install openpyxl
```

### "Python no reconocido como comando"

Python no está en PATH. Reinstala Python marcando "Add Python to PATH".

### La aplicación no abre

Verifica la instalación ejecutando:

```bash
python test_system.py
```

---

## 💡 Tips

### Usar Entorno Virtual (Recomendado)

```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Ver Logs del Sistema

Los logs se guardan en `logs/system.log`. Útil para debugging.

```bash
# Ver últimas líneas del log
tail -n 50 logs/system.log  # Linux/Mac
Get-Content logs/system.log -Tail 50  # Windows PowerShell
```

### Limpiar Datos Antiguos

```python
from utils.file_manager import file_manager

# Eliminar archivos más antiguos que 30 días
deleted = file_manager.clean_old_files(days=30)
print(f"Archivos eliminados: {deleted}")
```

---

## 🎯 Objetivos del Proyecto

Este sistema debe:

1. ✅ Capturar datos de 7 sensores IMU + plataforma de fuerza
2. ✅ Sincronizar ambas fuentes de datos
3. ✅ Realizar análisis biomecánico con OpenSim
4. ✅ Calcular métricas validadas (RMSE, ICC, etc.)
5. ✅ Generar alertas sobre patrones inadecuados
6. ✅ Producir reportes profesionales en PDF/Excel

**Estado actual:** ~30% completado (ver [PROJECT_STATUS.md](PROJECT_STATUS.md))

---

## 🤝 Soporte

- **Email:** [tu-email@uan.edu.co]
- **Repositorio:** [URL si aplica]
- **Director:** [Nombre del director]

---

## ✨ ¡Comienza Ahora!

```bash
# 1. Instalar
pip install -r requirements.txt

# 2. Probar
python test_system.py

# 3. Generar datos de ejemplo
python generate_sample_data.py

# 4. Ejecutar
python main.py
```

---

**¡Éxito en tu proyecto de tesis!** 🎓🚀

---

*Última actualización: 2025-01-13*
