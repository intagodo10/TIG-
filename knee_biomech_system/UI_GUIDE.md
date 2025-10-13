# 🎨 Guía de Interfaz Gráfica

## Sistema de Análisis Biomecánico de Rodilla

---

## ✅ Componentes Implementados

### 📦 Componentes Reutilizables ([ui/components/](ui/components/))

#### 1. MetricCard (metric_card.py)
**Descripción:** Tarjeta para mostrar métricas biomecánicas con valor, unidad y estado visual.

**Uso:**
```python
from ui.components import MetricCard

# Crear tarjeta
card = MetricCard(
    parent,
    title="ROM Flexión",
    value="87.3",
    unit="°",
    status="normal"  # normal, warning, error
)
card.pack()

# Actualizar valor
card.update_value("92.5", status="warning")
```

**Estados:**
- `normal`: Verde - Valor dentro de rango
- `warning`: Amarillo - Valor fuera de rango esperado
- `error`: Rojo - Valor crítico

---

#### 2. SensorStatusIndicator & SensorPanel (sensor_status.py)
**Descripción:** Indicadores de estado de conexión de sensores IMU.

**Uso:**
```python
from ui.components import SensorPanel

# Crear panel
sensor_panel = SensorPanel(
    parent,
    sensor_locations=["pelvis", "femur_right", "femur_left", ...]
)
sensor_panel.pack()

# Actualizar estado de un sensor
sensor_panel.update_sensor_status("pelvis", "connected")

# Actualizar todos
sensor_panel.update_all_sensors("connecting")
```

**Estados posibles:**
- `connected`: Verde - Conectado correctamente
- `connecting`: Amarillo - Conectando...
- `disconnected`: Rojo - Desconectado
- `error`: Rojo - Error de conexión

---

#### 3. AlertToast & AlertManager (alert_toast.py)
**Descripción:** Sistema de notificaciones toast (esquina superior derecha).

**Uso:**
```python
from ui.components import AlertManager

# Crear gestor (una vez en ventana principal)
alert_manager = AlertManager(window)

# Mostrar alertas
alert_manager.info("Información general")
alert_manager.success("Operación exitosa")
alert_manager.warning("Advertencia importante", duration=5000)
alert_manager.error("Error crítico", duration=5000)
```

**Tipos:**
- `info`: Azul - Información
- `success`: Verde - Éxito
- `warning`: Amarillo - Advertencia
- `error`: Rojo - Error

---

#### 4. PlotWidget & MultiPlotWidget (plot_widget.py)
**Descripción:** Gráficos embebidos con matplotlib.

**Uso Básico:**
```python
from ui.components import PlotWidget
import numpy as np

# Crear widget
plot = PlotWidget(parent, title="Fuerza vs Tiempo")
plot.pack()

# Graficar
time = np.linspace(0, 10, 100)
force = np.sin(time) * 100

plot.plot_line(time, force, label="Fz", color="#00d4aa")
plot.set_labels(xlabel="Tiempo (s)", ylabel="Fuerza (N)")
plot.add_grid()
plot.add_legend()
plot.refresh()
```

**Uso Múltiples Gráficos:**
```python
from ui.components import MultiPlotWidget

# Crear widget con 2 filas, 1 columna
multi_plot = MultiPlotWidget(parent, rows=2, cols=1)
multi_plot.pack()

# Obtener subplot y graficar
ax1 = multi_plot.get_subplot(0, 0)
ax1.plot(time, force, color="#00d4aa")
ax1.set_title("Fuerza")

ax2 = multi_plot.get_subplot(1, 0)
ax2.plot(time, angle, color="#4a9eff")
ax2.set_title("Ángulo")

multi_plot.refresh()
```

---

### 📱 Vistas Principales ([ui/views/](ui/views/))

#### 1. PatientView (patient_view.py)
**Descripción:** Vista para gestión de información de pacientes.

**Características:**
- ✅ Formulario completo de paciente
- ✅ Validación en tiempo real
- ✅ Cálculo automático de BMI y peso
- ✅ Callback cuando se guarda paciente

**Campos:**
- ID del Paciente (obligatorio)
- Nombre Completo (obligatorio)
- Edad (años) (obligatorio)
- Sexo (obligatorio)
- Masa (kg) (obligatorio)
- Altura (m) (obligatorio)
- Extremidad Afectada
- Diagnóstico
- Notas Adicionales

**Uso:**
```python
from ui.views import PatientView

def on_patient_saved(patient):
    print(f"Paciente guardado: {patient.name}")

patient_view = PatientView(parent, on_patient_saved=on_patient_saved)
patient_view.pack()
```

---

#### 2. CaptureView (capture_view.py)
**Descripción:** Vista para captura de datos en tiempo real.

**Características:**
- ✅ Importación de datos Valkyria (Excel)
- ✅ Panel de estado de sensores IMU
- ✅ Configuración de ejercicio
- ✅ Gráficos en tiempo real
- ✅ Control de grabación

**Funcionalidades:**
1. **Configurar Ejercicio:** Seleccionar tipo, duración, repeticiones
2. **Importar Datos Valkyria:** Botón para seleccionar archivo Excel
3. **Conectar Sensores:** Auto-detectar sensores IMU (placeholder)
4. **Grabar:** Iniciar/detener captura de datos

**Uso:**
```python
from ui.views import CaptureView

capture_view = CaptureView(parent)
capture_view.pack()
```

---

### 🏠 Ventana Principal (main_window.py)

**Descripción:** Ventana principal con navegación por tabs.

**Estructura:**
```
┌─────────────────────────────────────────────────────┐
│  HEADER: Logo + Título + Info Paciente             │
├─────────────────────────────────────────────────────┤
│  [📊 Dashboard] [👤 Paciente] [🎯 Captura]         │
│  [📈 Análisis] [📄 Reportes]                       │
│  ┌───────────────────────────────────────────────┐ │
│  │                                               │ │
│  │          CONTENIDO DE LA PESTAÑA             │ │
│  │                                               │ │
│  └───────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────┤
│  FOOTER: Estado | Versión                          │
└─────────────────────────────────────────────────────┘
```

**Pestañas:**
1. **📊 Dashboard:** Vista general con métricas resumen
2. **👤 Paciente:** Gestión de información de pacientes
3. **🎯 Captura:** Captura de datos en tiempo real
4. **📈 Análisis:** Procesamiento y análisis (placeholder)
5. **📄 Reportes:** Generación de reportes (placeholder)

**Métodos públicos:**
```python
# Actualizar estado
app.update_status("Procesando datos...")

# Mostrar alerta
app.show_alert("Operación completada", "success")

# Obtener paciente actual
current_patient = app.current_patient
```

---

## 🎨 Tema y Estilos

### Paleta de Colores

```python
from config.ui_theme import COLORS

# Fondos
COLORS["bg_primary"]      # #1e1e1e - Fondo principal
COLORS["bg_secondary"]    # #2d2d2d - Fondo secundario
COLORS["bg_tertiary"]     # #3d3d3d - Fondo terciario

# Acentos
COLORS["accent_primary"]   # #00d4aa - Verde azulado
COLORS["accent_secondary"] # #4a9eff - Azul

# Estados
COLORS["success"]  # #6bcf7f - Verde
COLORS["warning"]  # #ffd93d - Amarillo
COLORS["error"]    # #ff6b6b - Rojo
COLORS["info"]     # #4a9eff - Azul

# Texto
COLORS["text_primary"]   # #e0e0e0 - Texto principal
COLORS["text_secondary"] # #b0b0b0 - Texto secundario
COLORS["text_tertiary"]  # #808080 - Texto terciario
```

### Tipografía

```python
from config.ui_theme import FONTS

FONTS["size_xxlarge"]  # 24pt - Títulos principales
FONTS["size_xlarge"]   # 20pt - Títulos secciones
FONTS["size_large"]    # 16pt - Subtítulos
FONTS["size_medium"]   # 14pt - Texto destacado
FONTS["size_normal"]   # 12pt - Texto normal
FONTS["size_small"]    # 10pt - Texto pequeño
```

---

## 🚀 Cómo Ejecutar

### Instalación de Dependencias

```bash
pip install customtkinter matplotlib numpy pandas
```

### Ejecutar Aplicación

```bash
python main.py
```

### Probar Componentes

```bash
# Generar datos de ejemplo
python generate_sample_data.py

# Ejecutar aplicación
python main.py

# Ir a pestaña "Captura"
# Clic en "Importar Datos de Valkyria"
# Seleccionar: data/raw/ejemplos/ejemplo_sentadilla_70kg.xlsx
```

---

## �� Flujo de Uso Típico

### 1. Ingresar Paciente
1. Ir a pestaña **👤 Paciente**
2. Llenar formulario
3. Clic en "Guardar Paciente"
4. Ver confirmación en alerta verde

### 2. Capturar Datos
1. Ir a pestaña **🎯 Captura**
2. Seleccionar tipo de ejercicio
3. Clic en "📥 Importar Datos de Valkyria"
4. Seleccionar archivo Excel
5. Ver gráfico de fuerzas actualizado
6. (Opcional) Conectar sensores IMU
7. Clic en "▶ Iniciar Grabación"
8. Realizar ejercicio
9. Clic en "■ Detener Grabación"

### 3. Analizar Resultados (En Desarrollo)
1. Ir a pestaña **📈 Análisis**
2. Ver métricas calculadas
3. Ver gráficos comparativos
4. Revisar alertas

### 4. Exportar Reporte (En Desarrollo)
1. Ir a pestaña **📄 Reportes**
2. Seleccionar formato (PDF/Excel/CSV)
3. Clic en "Exportar"

---

## 🎯 Próximas Funcionalidades

### A Implementar

- [ ] Vista de Análisis completa
- [ ] Vista de Reportes completa
- [ ] Conexión real con sensores IMU Xsens DOT
- [ ] Gráficos en tiempo real durante grabación
- [ ] Sincronización IMU + Fuerza
- [ ] Integración con OpenSim
- [ ] Cálculo de métricas biomecánicas
- [ ] Sistema de alertas en análisis
- [ ] Exportación PDF con gráficos
- [ ] Exportación Excel avanzada
- [ ] Historial de sesiones
- [ ] Comparación entre sesiones
- [ ] Búsqueda de pacientes
- [ ] Base de datos SQLite integrada

---

## 🐛 Problemas Conocidos

### 1. Importación de Excel falla
**Síntoma:** Error al importar archivo Excel de Valkyria

**Solución:**
- Verificar que el archivo tenga las columnas correctas:
  - "Time (s)", "Fx (N)", "Fy (N)", "Fz (N)", "Mx (Nm)", "My (Nm)", "Mz (Nm)"
- Usar archivos de ejemplo en `data/raw/ejemplos/`

### 2. Gráficos no se muestran
**Síntoma:** Los gráficos aparecen vacíos

**Solución:**
- Verificar que matplotlib esté instalado: `pip install matplotlib`
- Reiniciar la aplicación

### 3. Sensores IMU no conectan
**Síntoma:** Los sensores no se detectan

**Estado:** Funcionalidad en desarrollo (actualmente simulada)

**Solución temporal:** Los sensores cambiarán a "conectado" automáticamente al hacer clic

---

## 📞 Soporte

Para dudas sobre la interfaz:
- Revisar este documento
- Revisar código fuente en `ui/`
- Consultar [README.md](README.md) para documentación general

---

## 🎓 Notas para Desarrollo

### Añadir Nueva Vista

1. Crear archivo en `ui/views/nueva_vista.py`
2. Heredar de `ctk.CTkFrame`
3. Implementar `__init__` y `_create_widgets`
4. Importar en `main_window.py`
5. Añadir tab en `_create_widgets`:
   ```python
   self.tab_nueva = self.tabview.add("🆕 Nueva")
   self.nueva_view = NuevaVista(self.tab_nueva)
   self.nueva_view.pack(fill="both", expand=True)
   ```

### Añadir Nuevo Componente

1. Crear archivo en `ui/components/nuevo_componente.py`
2. Heredar de `ctk.CTkFrame`
3. Implementar widgets y métodos públicos
4. Exportar en `ui/components/__init__.py`
5. Usar donde se necesite

---

**Versión:** 1.0
**Última actualización:** 2025-01-13
**Estado:** ✅ Funcional - 🚧 En Desarrollo Activo

---

¡La interfaz está lista para usar y expandir! 🚀
