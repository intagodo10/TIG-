# Sistema de Análisis Biomecánico

## 📊 Descripción General

El sistema de análisis biomecánico integra **sincronización de señales**, **procesamiento digital**, **cálculo de métricas** y **detección de alertas** para proporcionar evaluación completa del movimiento de rodilla.

---

## 🔧 Componentes del Sistema

### 1. **Sincronizador de Señales** (`synchronizer.py`)

**Propósito**: Sincronizar datos de IMU (60 Hz) con plataforma de fuerza (1000 Hz)

**Métodos clave**:
- `synchronize()`: Sincronización completa
  - Encuentra ventana temporal común
  - Crea vector de tiempo unificado (100 Hz)
  - Interpola datos (método cúbico)
  - Detecta offset temporal por correlación cruzada
  - Calcula calidad de sincronización (0-1)

**Salida**: `SyncResult` con datos sincronizados a 100 Hz

**Validaciones**:
- ✓ Vectores de tiempo monótonos
- ✓ Mínimo 10 muestras por señal
- ✓ Superposición temporal suficiente
- ✓ Offset temporal < umbral máximo (default: 0.5s)

---

### 2. **Procesador de Señales** (`signal_processing.py`)

**Propósito**: Filtrado, detección de eventos y preprocesamiento de señales

**Filtros Butterworth** (forward-backward, sin desfase):
- IMU aceleración: 20 Hz (cutoff)
- IMU giroscopio: 15 Hz
- Plataforma de fuerza: 50 Hz
- Orden: 4 (configurable)

**Métodos principales**:

#### Filtrado
```python
filter_butterworth(data, cutoff, fs, order=4)
filter_imu_acceleration(acceleration, fs=60)
filter_imu_gyro(angular_velocity, fs=60)
filter_force(force, fs=1000)
```

#### Detección de Eventos
```python
detect_events_threshold(signal, threshold, min_duration, fs)
detect_grf_contacts(fz, threshold=20.0, fs=1000, min_contact_time=0.1)
```
- Detecta heel strike (contacto) y toe-off (despegue)
- Filtra eventos por duración mínima

#### Cálculos Cinemáticos
```python
calculate_velocity(acceleration, dt, initial_velocity=0.0)
calculate_displacement(velocity, dt, initial_position=0.0)
calculate_jump_height(time, fz, body_mass, contact_idx, liftoff_idx)
```
- Integración trapezoidal
- Método impulso-momentum para altura de salto

#### Downsampling
```python
downsample(data, original_fs, target_fs)
```
- Aplica anti-aliasing filter antes de decimar
- Evita aliasing

---

### 3. **Calculadora de Métricas** (`metrics_calculator.py`)

**Propósito**: Calcular métricas biomecánicas estándar

#### 3.1 Métricas Cinemáticas (`KinematicMetrics`)
```python
calculate_kinematic_metrics(time, angle)
```
**Métricas**:
- **ROM** (Range of Motion): `max(angle) - min(angle)`
- **Pico de flexión**: Ángulo máximo
- **Pico de extensión**: Ángulo mínimo
- **Ángulo promedio**
- **Velocidad angular pico**: `max(|dθ/dt|)`
- **Aceleración angular pico**: `max(|d²θ/dt²|)`

**Aplicaciones**: Evaluar movilidad, rigidez, control motor

---

#### 3.2 Métricas Dinámicas (`DynamicMetrics`)
```python
calculate_dynamic_metrics(time, moment, angular_velocity, body_mass)
```
**Métricas** (normalizadas por masa corporal):
- **Momento pico**: `max(|M|) / mass` (Nm/kg)
- **Momento promedio**: `mean(|M|) / mass`
- **Potencia pico**: `max(|M·ω|) / mass` (W/kg)
- **Trabajo**: `∫|P|dt / mass` (J/kg)
- **Impulso del momento**: `∫|M|dt / mass` (Nm·s/kg)

**Aplicaciones**: Evaluar carga articular, capacidad muscular, eficiencia

---

#### 3.3 Métricas de Fuerza (`ForceMetrics`)
```python
calculate_force_metrics(time, grf, body_weight, contact_start, contact_end)
```
**Métricas** (normalizadas por peso corporal):
- **GRF pico**: `max(Fz) / BW` (Body Weights)
- **GRF promedio**: `mean(Fz) / BW`
- **Loading rate**: Tasa de carga `(Fpeak - F0) / t_peak` (BW/s)
- **Impulso**: `∫Fz·dt` (N·s)
- **Tiempo de contacto**: Duración del contacto (s)
- **Tiempo al pico**: Desde contacto hasta GRF máxima (s)

**Aplicaciones**: Evaluar impacto, estrategias de aterrizaje, riesgo de lesión

**Valores de referencia**:
- Marcha: 1.0-1.5 BW
- Squat: 0.8-2.5 BW
- Salto vertical: 2.0-5.0 BW
- Loading rate seguro: < 75 BW/s

---

#### 3.4 Métricas de Validación (`ValidationMetrics`)
```python
calculate_validation_metrics(measured, reference)
```
**Métricas estadísticas**:
- **RMSE** (Root Mean Square Error): Precisión absoluta
- **MAE** (Mean Absolute Error): Error medio
- **ICC** (Intraclass Correlation): Concordancia (0-1)
  - ICC > 0.90: Excelente
  - ICC 0.75-0.90: Buena
  - ICC < 0.75: Pobre
- **R²** (Coeficiente de determinación): Varianza explicada (0-1)
- **CV** (Coefficient of Variation): Variabilidad relativa (%)

**Aplicaciones**: Validar sistema vs gold standard, evaluar consistencia entre repeticiones

---

#### 3.5 Métricas de Simetría (`SymmetryMetrics`)
```python
calculate_symmetry_metrics(right_limb, left_limb)
```
**Métricas**:
- **Symmetry Index**: `|R - L| / (0.5*(R+L)) * 100` (%)
  - SI < 10%: Simétrico
  - SI 10-20%: Asimetría moderada
  - SI > 20%: Asimetría severa
- **Asymmetry Ratio**: `R / L`
  - Ideal: 1.0
  - Aceptable: 0.85-1.15
- **Diferencia absoluta**: `|R - L|`
- **Bilateral Deficit**: Déficit en tarea bilateral vs unilateral (%)

**Aplicaciones**: Detectar compensaciones, evaluar recuperación post-lesión

---

### 4. **Sistema de Alertas** (`alert_system.py`)

**Propósito**: Detectar condiciones anormales y generar notificaciones

#### Niveles de Severidad
```python
class AlertSeverity(Enum):
    INFO = "info"          # Información
    WARNING = "warning"    # Advertencia (requiere atención)
    ERROR = "error"        # Error (requiere intervención)
    CRITICAL = "critical"  # Crítico (riesgo alto)
```

#### Categorías de Alertas
```python
class AlertCategory(Enum):
    KINEMATIC = "kinematic"    # Cinemática anormal
    DYNAMIC = "dynamic"        # Cargas excesivas
    FORCE = "force"            # Impactos peligrosos
    SYMMETRY = "symmetry"      # Asimetrías significativas
    VALIDATION = "validation"  # Problemas de validación
    TECHNICAL = "technical"    # Problemas técnicos
```

#### Verificaciones Automáticas

##### **Alertas Cinemáticas**
```python
check_rom_alert(rom, joint="knee")
```
- ROM < 70% del mínimo normal → ERROR (rigidez)
- ROM < mínimo normal → WARNING
- ROM > 120% del máximo → WARNING (hipermovilidad)

```python
check_angular_velocity_alert(angular_velocity)
```
- Velocidad > umbral (config) → WARNING/CRITICAL
- Protege contra movimientos balísticos no controlados

##### **Alertas Dinámicas**
```python
check_moment_alert(moment, body_mass)
```
- Momento > 3.5 Nm/kg (default) → WARNING/ERROR
- Detecta sobrecarga articular

##### **Alertas de Fuerza**
```python
check_grf_alert(peak_grf, body_weight, exercise_type)
```
Umbrales por ejercicio:
- Squat: 0.8-2.5 BW
- Jump: 1.5-5.0 BW
- Walk: 0.8-1.5 BW

```python
check_loading_rate_alert(loading_rate, body_weight)
```
- Loading rate > 75 BW/s → ERROR/CRITICAL
- **ALTO RIESGO** de lesión por impacto

##### **Alertas de Simetría**
```python
check_symmetry_alert(symmetry_index)
```
- SI > 20% → ERROR (asimetría severa)
- SI > 10% → WARNING (asimetría moderada)

##### **Alertas Técnicas**
```python
check_data_quality_alert(signal, signal_name)
```
- Valores NaN/Inf → ERROR
- Señal constante (std < 1e-6) → ERROR (sensor desconectado)
- Outliers > 5% → WARNING (ruido excesivo)

```python
check_sync_quality_alert(sync_quality)
```
- Calidad < 0.7 → ERROR
- Calidad < 0.85 → WARNING

#### Estructura de Alert
```python
@dataclass
class Alert:
    id: str                    # ID único
    timestamp: datetime        # Momento
    severity: AlertSeverity    # Nivel
    category: AlertCategory    # Categoría
    title: str                 # Título corto
    message: str               # Mensaje detallado
    value: Optional[float]     # Valor que generó alerta
    threshold: Optional[float] # Umbral excedido
    recommendation: str        # Recomendación de acción
    acknowledged: bool         # Si fue reconocida
```

**Ejemplo de alerta**:
```
[ERROR] Impacto Excesivo
GRF pico (4.2 BW) excede el máximo recomendado para squat (2.5 BW).
Recomendación: Reducir intensidad o altura. Alto riesgo de lesión por impacto.
Enseñar técnica de aterrizaje suave y absorción de fuerzas.
```

---

### 5. **Analizador Biomecánico Integrado** (`biomech_analyzer.py`)

**Propósito**: Orquestar todo el flujo de análisis en un solo proceso

#### Flujo de Análisis Completo
```python
analyzer = BiomechAnalyzer(patient)
result = analyzer.analyze_full_session(
    time_imu, imu_data,
    time_force, force_data,
    exercise_type="squat"
)
```

**6 FASES AUTOMÁTICAS**:

1. **SINCRONIZACIÓN**
   - Sincroniza IMU + Fuerza
   - Verifica calidad de sync

2. **PROCESAMIENTO DE SEÑALES**
   - Aplica filtros Butterworth
   - Filtra cada canal apropiadamente

3. **DETECCIÓN DE EVENTOS**
   - Detecta contactos (heel strike/toe-off)
   - Segmenta repeticiones

4. **CÁLCULO DE MÉTRICAS**
   - Cinemáticas (ROM, velocidades)
   - Dinámicas (momentos, potencia)
   - Fuerza (GRF, loading rate)
   - Simetría bilateral

5. **GENERACIÓN DE ALERTAS**
   - Evalúa todas las métricas
   - Genera alertas automáticas
   - Proporciona recomendaciones

6. **GENERACIÓN DE RESUMEN**
   - Resumen textual completo
   - Todas las métricas
   - Alertas activas

#### Resultado (`AnalysisResult`)
```python
@dataclass
class AnalysisResult:
    success: bool
    sync_result: SyncResult
    kinematic_metrics: Dict[str, KinematicMetrics]
    dynamic_metrics: Dict[str, DynamicMetrics]
    force_metrics: Dict[str, ForceMetrics]
    symmetry_metrics: SymmetryMetrics
    alerts: List[Alert]
    processed_data: Dict[str, np.ndarray]
    summary: str
```

---

## 🎯 Casos de Uso

### Caso 1: Evaluación de Sentadilla (Squat)
```python
analyzer = BiomechAnalyzer(patient)
result = analyzer.analyze_full_session(
    time_imu, imu_data,
    time_force, force_data,
    exercise_type="squat"
)

# Acceder a métricas
rom_knee = result.kinematic_metrics['knee_right'].rom
peak_grf = result.force_metrics['contact_1'].peak_grf

# Revisar alertas
critical_alerts = [a for a in result.alerts
                   if a.severity == AlertSeverity.CRITICAL]

print(result.summary)
```

### Caso 2: Comparación Bilateral
```python
# Obtener métricas de ambas rodillas
rom_right = result.kinematic_metrics['knee_right'].rom
rom_left = result.kinematic_metrics['knee_left'].rom

# Simetría automática
symmetry = result.symmetry_metrics
if symmetry.symmetry_index > 20:
    print(f"⚠️ Asimetría severa: {symmetry.symmetry_index:.1f}%")
```

### Caso 3: Validación de Técnica
```python
# Verificar alertas de técnica
technique_alerts = [a for a in result.alerts
                    if a.category in [AlertCategory.KINEMATIC,
                                     AlertCategory.FORCE]]

for alert in technique_alerts:
    print(f"[{alert.severity.value}] {alert.title}")
    print(f"Recomendación: {alert.recommendation}")
```

---

## 📈 Integración con Interfaz

El sistema de análisis se integra con la UI a través de:

1. **Vista de Análisis** (`ui/views/analysis_view.py` - pendiente)
   - Muestra métricas en tiempo real
   - Gráficos comparativos
   - Panel de alertas

2. **Sistema de Alertas Toast**
   - Notificaciones emergentes para alertas críticas
   - Color según severidad

3. **Reportes PDF/Excel**
   - Exporta todos los resultados
   - Gráficos incluidos

---

## 🔬 Validación y Referencias

### Valores de Referencia (Literatura)

**ROM Rodilla**:
- Normal: 0-135° (Norkin & White, 2016)
- Post-ACL: 90-120° aceptable
- Rigidez: < 90°

**GRF**:
- Marcha: 1.0-1.5 BW (Perry & Burnfield, 2010)
- Squat: 0.8-2.5 BW
- Salto: 2-5 BW (Linthorne, 2001)

**Loading Rate**:
- Seguro: < 75 BW/s
- Lesión ACL: > 100 BW/s asociado con mayor riesgo

**Simetría**:
- Normal: SI < 10%
- Clínicamente relevante: SI > 15-20% (Herzog et al., 1989)

---

## ⚙️ Configuración

Todos los umbrales y parámetros se configuran en `config/settings.py`:

```python
ALERT_THRESHOLDS = {
    "max_angular_velocity": 500,      # deg/s
    "max_knee_moment": 3.5,           # Nm/kg
    "max_loading_rate": 75,           # BW/s
    "moderate_asymmetry": 10,         # %
    "severe_asymmetry": 20,           # %
}

REFERENCE_VALUES = {
    "knee_flexion_rom": (0, 135),     # grados
    "hip_flexion_rom": (0, 120),
    "ankle_dorsiflexion_rom": (-20, 30),
    # ...
}
```

---

## 🚀 Próximos Pasos

1. **Integración OpenSim** (opcional si instalado)
   - Inverse Kinematics (IK) para ángulos articulares precisos
   - Inverse Dynamics (ID) para momentos articulares reales
   - Archivo: `core/opensim_interface.py` (pendiente)

2. **Base de Datos**
   - Almacenar resultados de análisis
   - Comparar evolución temporal
   - SQLite local

3. **Reportes Automatizados**
   - PDF con gráficos
   - Excel con datos completos
   - Comparación con valores normativos

4. **Machine Learning** (futuro)
   - Clasificación de patrones de movimiento
   - Predicción de riesgo de lesión
   - Recomendaciones personalizadas

---

## 📚 Referencias

1. Norkin, C. C., & White, D. J. (2016). *Measurement of joint motion: a guide to goniometry*. FA Davis.
2. Perry, J., & Burnfield, J. M. (2010). *Gait analysis: normal and pathological function*. SLACK Incorporated.
3. Linthorne, N. P. (2001). Analysis of standing vertical jumps using a force platform. *American Journal of Physics*, 69(11), 1198-1204.
4. Herzog, W., et al. (1989). Asymmetries in ground reaction force patterns in normal human gait. *Medicine and Science in Sports and Exercise*, 21(1), 110-114.

---

**Estado del Sistema**: ✅ **COMPLETAMENTE FUNCIONAL**

Todos los módulos de análisis están implementados y listos para integración con la interfaz gráfica.
