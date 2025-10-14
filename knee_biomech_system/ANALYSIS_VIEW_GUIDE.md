# 📈 Guía de la Vista de Análisis

## Descripción General

La **Vista de Análisis** es el componente central para visualizar y evaluar los resultados del análisis biomecánico. Muestra métricas calculadas, gráficos interactivos y alertas clínicas en una interfaz intuitiva de 3 columnas.

---

## 🎯 Características Principales

### 1. **Visualización de Gráficos** (Columna Izquierda)
- 📊 Gráfico de ángulo de rodilla
- 💪 Gráfico de fuerza de reacción al suelo (GRF)
- Gráficos con tema oscuro integrado
- Zoom y navegación interactiva

### 2. **Tabla de Métricas** (Columna Central)
- 🔄 **Cinemática**: ROM, flexión/extensión, velocidades angulares
- ⚡ **Dinámica**: Momentos, potencia, trabajo (requiere OpenSim)
- 💪 **Fuerza**: GRF pico, loading rate, impulso, tiempos de contacto
- ⚖️ **Simetría**: Índice de simetría, ratio de asimetría, déficit bilateral

### 3. **Panel de Alertas** (Columna Derecha)
- ⚠️ Contadores por severidad (Críticas, Errores, Advertencias)
- 🎨 Código de colores según severidad
- 💡 Recomendaciones clínicas automáticas
- 📋 Lista detallada de todas las alertas

---

## 🚀 Flujo de Trabajo Completo

### Paso 1: Ingresar Información del Paciente
1. Ir a la pestaña **"👤 Paciente"**
2. Completar formulario:
   - ID del paciente
   - Nombre completo
   - Edad, sexo
   - Masa corporal (kg)
   - Altura (m)
   - Extremidad afectada
   - Diagnóstico (opcional)
3. Hacer clic en **"Guardar Paciente"**
   - ✅ Se mostrará confirmación en la parte superior
   - El paciente activo aparecerá en el header

### Paso 2: Capturar Datos
1. Ir a la pestaña **"🎯 Captura"**
2. **Configurar ejercicio**:
   - Seleccionar tipo de ejercicio (Squat, Salto, etc.)
   - Duración estimada
   - Número de repeticiones

3. **Importar datos de plataforma de fuerza**:
   - Clic en **"📥 Importar Datos de Valkyria"**
   - Seleccionar archivo Excel de Valkyria
   - ✅ Verificar que el estado muestre "Datos importados"
   - El gráfico de GRF se actualizará automáticamente

4. **Conectar sensores IMU** (opcional - actualmente simulado):
   - Clic en **"🔌 Conectar Sensores"**
   - Los 7 sensores cambiarán a estado "conectado" (verde)

5. **Ejecutar análisis**:
   - Clic en **"🔬 Analizar Datos"**
   - El sistema procesará los datos (5-10 segundos)
   - ✅ Automáticamente cambiará a la pestaña de análisis

### Paso 3: Visualizar Resultados
La **pestaña "📈 Análisis"** se abrirá automáticamente mostrando:

#### **Panel de Gráficos** (Izquierda)
- **Gráfico superior**: Velocidad angular / Ángulo de rodilla
  - Eje X: Tiempo (s)
  - Eje Y: Ángulo (grados) o Velocidad angular (rad/s)
  - Color: Azul turquesa (accent_primary)

- **Gráfico inferior**: Fuerza vertical (Fz)
  - Eje X: Tiempo (s)
  - Eje Y: Fuerza (N)
  - Color: Verde (success)
  - Línea horizontal en 0 N

#### **Tabla de Métricas** (Centro)
Organizada en secciones expandibles:

**🔄 Cinemática**
- Muestra para cada articulación (ej: KNEE_RIGHT):
  - ROM (Range of Motion) en grados
  - Pico de flexión
  - Pico de extensión
  - Ángulo promedio
  - Velocidad angular pico (deg/s)
  - Aceleración angular pico (deg/s²)

**💪 Fuerza**
- Para cada contacto detectado (CONTACT_1, CONTACT_2...):
  - GRF pico (Body Weights)
  - GRF promedio (BW)
  - Loading rate (BW/s) - **Importante para riesgo de lesión**
  - Impulso (N·s)
  - Tiempo de contacto (s)
  - Tiempo al pico (s)

**⚖️ Simetría Bilateral**
- Indicador visual grande con código de colores:
  - 🟢 Verde: SI < 10% (Simétrico)
  - 🟡 Amarillo: 10% ≤ SI < 20% (Asimetría Moderada)
  - 🔴 Rojo: SI ≥ 20% (Asimetría Severa)
- Métricas detalladas:
  - Índice de Simetría (%)
  - Ratio de Asimetría
  - Diferencia Absoluta
  - Déficit Bilateral (%)

#### **Panel de Alertas** (Derecha)

**Contadores de Resumen**:
```
Críticas    Errores    Advertencias
   0          1            2
```

**Lista de Alertas**:
Cada alerta muestra:
- **Badge de severidad** (CRITICAL/ERROR/WARNING/INFO)
- **Título descriptivo**
- **Mensaje detallado** con valores y umbrales
- **💡 Recomendación clínica** (si aplica)

**Ejemplo de alerta**:
```
┌─────────────────────────────────────────┐
│ ERROR   Sincronización Pobre            │
│                                         │
│ Calidad de sincronización (0.0%) es    │
│ insuficiente.                           │
│                                         │
│ 💡 Recomendación: Los datos de IMU y   │
│ plataforma de fuerza pueden no estar   │
│ correctamente sincronizados. Verificar │
│ marcadores de tiempo y repetir captura.│
└─────────────────────────────────────────┘
```

### Paso 4: Exportar Reporte
1. Clic en **"📄 Exportar Reporte"** (en desarrollo)
2. Seleccionar formato (PDF/Excel)
3. Guardar archivo

---

## 🎨 Código de Colores

### Estados de Alerta
| Severidad | Color | Icono | Significado |
|-----------|-------|-------|-------------|
| INFO | 🔵 Azul | ℹ | Información general |
| WARNING | 🟡 Amarillo | ⚠ | Requiere atención |
| ERROR | 🟠 Naranja | ⛔ | Requiere intervención |
| CRITICAL | 🔴 Rojo | 🚨 | Riesgo alto inmediato |

### Simetría
| Rango SI | Color | Estado |
|----------|-------|--------|
| < 10% | 🟢 Verde | Simétrico |
| 10-20% | 🟡 Amarillo | Asimetría Moderada |
| > 20% | 🔴 Rojo | Asimetría Severa |

---

## 📊 Métricas Clave y su Interpretación

### **Loading Rate (Tasa de Carga)**
```
Valor: XX.X BW/s
Umbral seguro: < 75 BW/s
```
**Interpretación**:
- < 50 BW/s: Excelente control de impacto
- 50-75 BW/s: Aceptable
- 75-100 BW/s: ⚠️ Alto riesgo
- > 100 BW/s: 🚨 Riesgo crítico de lesión

**Acción si está elevado**:
- Enseñar técnica de aterrizaje suave
- Reducir altura de saltos
- Usar superficies más blandas
- Fortalecer musculatura excéntrica

### **GRF Pico (Peak Ground Reaction Force)**
```
Valor: X.XX BW
Rangos por ejercicio:
- Marcha: 1.0-1.5 BW
- Squat: 0.8-2.5 BW
- Salto: 2.0-5.0 BW
```
**Interpretación**:
- Dentro del rango: ✅ Ejecución normal
- Por debajo: ⚠️ Posible evasión de carga
- Por encima: ⚠️ Impacto excesivo

### **ROM (Range of Motion) - Rodilla**
```
Valor: XXX°
Normal: 0-135°
Post-ACL aceptable: 90-120°
```
**Interpretación**:
- < 60°: 🔴 Rigidez significativa
- 60-90°: 🟡 ROM reducido
- 90-135°: 🟢 ROM normal
- > 135°: 🟡 Posible hipermovilidad

### **Índice de Simetría (Symmetry Index)**
```
SI = |R - L| / (0.5*(R+L)) * 100
```
**Interpretación**:
- < 5%: Excelente simetría
- 5-10%: Simetría aceptable
- 10-20%: ⚠️ Asimetría moderada (requiere atención)
- > 20%: 🔴 Asimetría severa (intervención necesaria)

**Causas comunes de asimetría**:
- Compensación por dolor
- Debilidad muscular unilateral
- Déficit de control motor
- Lesión previa no rehabilitada

---

## ⚙️ Configuración de Umbrales

Los umbrales de alertas se pueden ajustar en `config/settings.py`:

```python
ALERT_THRESHOLDS = {
    "max_angular_velocity": 500,      # deg/s
    "max_knee_moment": 3.5,           # Nm/kg
    "max_loading_rate": 75,           # BW/s
    "moderate_asymmetry": 10,         # %
    "severe_asymmetry": 20,           # %
}
```

---

## 🔬 Casos de Uso Clínicos

### Caso 1: Rehabilitación Post-Cirugía ACL

**Objetivo**: Evaluar ROM y simetría durante squat

**Protocolo**:
1. Configurar ejercicio: Squat, 10s, 5 repeticiones
2. Analizar datos
3. Verificar:
   - ✅ ROM ≥ 90°
   - ✅ SI < 15%
   - ✅ Loading rate < 75 BW/s
4. Seguimiento semanal para ver evolución

**Ejemplo de progreso**:
```
Semana 1: ROM=65°, SI=28%  → Asimetría severa
Semana 4: ROM=85°, SI=18%  → Mejorando
Semana 8: ROM=110°, SI=8%  → Alta médica
```

### Caso 2: Prevención de Lesiones en Atletas

**Objetivo**: Identificar factores de riesgo

**Protocolo**:
1. Salto vertical (CMJ)
2. Analizar:
   - Loading rate bilateral
   - Simetría de GRF entre piernas
   - Tiempo de contacto

**Flags de riesgo**:
- 🚩 Loading rate > 100 BW/s
- 🚩 SI > 15%
- 🚩 GRF pico > 5.0 BW

### Caso 3: Evaluación de Técnica de Movimiento

**Objetivo**: Optimizar patrón de movimiento

**Protocolo**:
1. Captura de ejercicio funcional
2. Revisar alertas de técnica
3. Intervenir según recomendaciones
4. Re-evaluar

---

## 🐛 Solución de Problemas

### "No hay resultados de análisis"
**Causa**: No se ha ejecutado un análisis
**Solución**:
1. Ir a pestaña Captura
2. Importar datos de Valkyria
3. Clic en "Analizar Datos"

### "Sincronización Pobre"
**Causa**: Datos IMU y fuerza no se alinean correctamente
**Solución**:
- Verificar que ambos archivos correspondan a la misma sesión
- Revisar marcas de tiempo
- En producción: sincronizar dispositivos antes de capturar

### Gráficos no se actualizan
**Causa**: Error en procesamiento de señales
**Solución**:
1. Revisar logs en `logs/app.log`
2. Verificar formato de datos de entrada
3. Reiniciar análisis

### Alertas críticas constantes
**Causa**: Umbrales muy estrictos o problema real
**Solución**:
1. Verificar si el paciente tiene limitaciones reales
2. Ajustar umbrales en `config/settings.py` si es necesario
3. Consultar con fisioterapeuta

---

## 📚 Referencias de Valores Normativos

### ROM Articular (Norkin & White, 2016)
- Rodilla flexión: 0-135°
- Cadera flexión: 0-120°
- Tobillo dorsiflexión: -20 a 30°

### GRF durante Marcha (Perry & Burnfield, 2010)
- Primer pico: 1.1-1.2 BW (loading response)
- Valle: 0.8 BW (mid-stance)
- Segundo pico: 1.1 BW (terminal stance)

### Loading Rate (Milner et al., 2006)
- Corredores sanos: 40-75 BW/s
- Alto riesgo: > 100 BW/s
- Asociado con lesiones por estrés

### Simetría (Herzog et al., 1989)
- Normal: < 10%
- Clínicamente relevante: > 15-20%
- Post-lesión: Objetivo < 10% para alta

---

## 🚀 Próximas Funcionalidades

### En Desarrollo
- [ ] Exportación de reportes PDF/Excel
- [ ] Comparación entre sesiones
- [ ] Gráficos de evolución temporal
- [ ] Integración OpenSim para IK/ID

### Futuro
- [ ] Machine Learning para clasificación de patrones
- [ ] Predicción de riesgo de lesión
- [ ] Biblioteca de ejercicios normalizados
- [ ] Conexión con base de datos en la nube

---

## 💡 Tips de Uso

1. **Siempre ingresar datos del paciente primero** - Permite normalizar métricas por peso corporal

2. **Revisar alertas antes de métricas** - Las alertas priorizan los problemas más importantes

3. **Documentar sesiones** - Anotar observaciones clínicas junto con datos objetivos

4. **Comparar con sesiones anteriores** - La evolución es más importante que valores absolutos

5. **No ignorar alertas de sincronización** - Datos mal sincronizados invalidan el análisis

6. **Usar valores de referencia como guía** - Considerar contexto individual del paciente

---

**Última actualización**: Octubre 14, 2025
**Versión**: 1.0.0
**Estado**: ✅ **TOTALMENTE FUNCIONAL**
