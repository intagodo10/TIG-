# Sistema Integrado de Análisis Biomecánico de Rodilla

## Universidad Antonio Nariño (UAN) - Ingeniería Biomédica

### Descripción

Sistema profesional para análisis biomecánico de rodilla que integra:
- **7 sensores IMU Xsens DOT** (60 Hz) para cinemática
- **Plataforma de fuerza Valkyria** (1000 Hz) para cinética
- **OpenSim 4.5** para análisis musculoesquelético
- **Interfaz CustomTkinter** moderna y profesional

---

## Características Principales

### Adquisición de Datos
- ✅ Conexión Bluetooth con sensores Xsens DOT
- ✅ Importación de datos Excel desde plataforma Valkyria
- ✅ Sincronización automática de señales (correlación cruzada)
- ✅ Visualización en tiempo real
- ✅ Detección de calidad de señal

### Análisis Biomecánico
- ✅ Cinemática Inversa (IK) con OpenSim
- ✅ Dinámica Inversa (ID) con OpenSim
- ✅ Cálculo de métricas: ROM, momentos, fuerzas, potencia
- ✅ Validación con RMSE, MAE, ICC
- ✅ Comparación con valores de referencia científicos

### Sistema de Alertas
- ⚠️ Detección de patrones inadecuados
- ⚠️ Alertas de riesgo de lesión
- ⚠️ Evaluación de simetría bilateral
- ⚠️ Umbrales basados en literatura

### Reportes Profesionales
- 📄 Exportación PDF con gráficos
- 📄 Excel con datos y análisis
- 📄 CSV para análisis externo
- 📄 Comparación con sesiones previas

---

## Requisitos del Sistema

### Hardware
- **PC con Windows 10/11** (mínimo 8 GB RAM)
- **Bluetooth 4.0+** para sensores Xsens DOT
- **7 sensores Xsens DOT**
- **Plataforma de fuerza Valkyria** (Involution)

### Software
- **Python 3.8 o superior**
- **OpenSim 4.5**
- **Microsoft Excel** (para exportar datos de Valkyria)

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd knee_biomech_system
```

### 2. Crear entorno virtual

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Instalar OpenSim

Descarga e instala OpenSim 4.5 desde:
https://simtk.org/frs/?group_id=91

Luego instala el paquete de Python:

```bash
python -m pip install opensim
```

### 5. Configurar rutas

Edita `config/settings.py` y ajusta las rutas según tu sistema:

```python
OPENSIM_CONFIG = {
    "model_path": "C:/path/to/opensim/models/gait2392_simbody.osim",
    # ...
}
```

---

## Uso del Sistema

### Inicio Rápido

```bash
python main.py
```

### Flujo de Trabajo

#### 1. Configurar Paciente
- Ingresar datos: ID, nombre, edad, masa, altura
- Especificar extremidad afectada y diagnóstico
- Guardar información

#### 2. Conectar Sensores
- **Sensores IMU:**
  - Activar Bluetooth del PC
  - Encender los 7 sensores Xsens DOT
  - Clic en "Auto-detectar sensores"
  - Asignar ubicaciones anatómicas

- **Plataforma de Fuerza:**
  - Exportar datos desde software Valkyria a Excel
  - Nota: La plataforma NO se conecta en tiempo real
  - Los datos se importarán después de la captura

#### 3. Calibración
- Paciente en posición N-pose o T-pose
- Clic en "Calibrar sensores"
- Mantener posición estática 5 segundos
- Verificar luz verde en todos los sensores

#### 4. Captura de Datos
- Seleccionar tipo de ejercicio:
  - **Sentadilla (Squat):** Flexo-extensión controlada
  - **CMJ:** Salto con contra-movimiento
  - **Squat Jump:** Salto desde sentadilla estática
- Configurar repeticiones y duración
- Clic en "Iniciar Grabación"
- El paciente realiza el ejercicio sobre la plataforma
- Clic en "Detener" al finalizar

#### 5. Importar Datos de Plataforma
- Clic en "Importar datos Valkyria"
- Seleccionar archivo Excel generado por Valkyria
- El sistema automáticamente sincronizará con datos IMU

#### 6. Análisis
- Clic en "Procesar Datos"
- El sistema ejecuta:
  1. Sincronización de señales
  2. Filtrado y procesamiento
  3. Cinemática inversa (OpenSim IK)
  4. Dinámica inversa (OpenSim ID)
  5. Cálculo de métricas
  6. Validación y alertas

#### 7. Resultados
- Visualización de gráficos:
  - Ángulos articulares vs tiempo
  - Momentos articulares vs tiempo
  - Fuerzas de reacción vs tiempo
- Tarjetas con métricas clave
- Alertas si hay patrones inadecuados
- Comparación con valores de referencia

#### 8. Generar Reporte
- Clic en "Exportar Reporte"
- Seleccionar formato (PDF, Excel, CSV)
- El reporte incluye:
  - Datos del paciente
  - Gráficos de análisis
  - Tabla de métricas
  - Alertas y recomendaciones

---

## Estructura del Proyecto

```
knee_biomech_system/
│
├── config/                     # Configuración
│   ├── settings.py            # Parámetros generales
│   ├── opensim_config.py      # Configuración OpenSim
│   └── ui_theme.py            # Tema de interfaz
│
├── core/                       # Lógica central
│   ├── data_acquisition/      # Adquisición de datos
│   │   ├── imu_handler.py     # Manejo de Xsens DOT
│   │   ├── force_platform.py  # Manejo de Valkyria
│   │   └── synchronizer.py    # Sincronización
│   │
│   ├── processing/            # Procesamiento
│   │   ├── opensim_interface.py
│   │   ├── inverse_kinematics.py
│   │   ├── inverse_dynamics.py
│   │   └── signal_processing.py
│   │
│   └── analysis/              # Análisis
│       ├── metrics_calculator.py
│       ├── validation.py
│       └── alert_system.py
│
├── ui/                        # Interfaz gráfica
│   ├── main_window.py         # Ventana principal
│   ├── components/            # Componentes reutilizables
│   └── views/                 # Vistas (pestañas)
│
├── models/                    # Modelos de datos
│   ├── patient.py
│   ├── session.py
│   └── results.py
│
├── utils/                     # Utilidades
│   ├── logger.py
│   ├── file_manager.py
│   └── validators.py
│
├── data/                      # Datos
│   ├── raw/                  # Datos crudos
│   ├── processed/            # Datos procesados
│   ├── results/              # Resultados
│   └── models/               # Modelos OpenSim
│
├── main.py                    # Punto de entrada
└── requirements.txt           # Dependencias
```

---

## Ejercicios Soportados

### Sentadilla (Squat)
- **ROM esperado:** 60-90° (normal), hasta 130° (profunda)
- **Momento pico:** 1.5-2.5 Nm/kg
- **GRF:** 0.8-1.5 × peso corporal

### Countermovement Jump (CMJ)
- **Altura de salto:** 20-45 cm
- **GRF despegue:** 2.0-3.5 × PC
- **GRF aterrizaje:** 2.5-5.0 × PC
- **Tiempo de contacto:** 300-600 ms

### Squat Jump
- **Altura de salto:** 15-40 cm
- **GRF despegue:** 2.5-4.0 × PC
- **GRF aterrizaje:** 3.0-6.0 × PC

---

## Métricas Calculadas

### Cinemáticas
- ROM (Range of Motion) de rodilla
- Flexión/extensión máxima y mínima
- Velocidad angular pico
- Aceleración angular pico
- Simetría bilateral (%)

### Dinámicas
- Momento pico de flexión/extensión (Nm/kg)
- Momento pico de abducción/aducción (Nm/kg)
- Potencia articular (W/kg)
- Trabajo articular (J)

### Fuerzas
- GRF pico vertical, AP, ML (N y × PC)
- GRF normalizada por peso corporal
- Tasa de carga (loading rate) en N/s
- Impulso (Ns)
- Tiempo de contacto y vuelo (s)

### Validación
- RMSE (Root Mean Square Error)
- MAE (Mean Absolute Error)
- ICC (Intraclass Correlation Coefficient)

---

## Criterios de Validación

### Cinemática
- **RMSE < 5°:** Excelente
- **RMSE 5-10°:** Aceptable
- **RMSE > 10°:** Revisar configuración

### Dinámica
- **RMSE < 10%:** Excelente
- **RMSE 10-20%:** Aceptable
- **RMSE > 20%:** Revisar configuración

### Repetibilidad (ICC)
- **ICC < 0.50:** Pobre
- **ICC 0.50-0.75:** Moderado
- **ICC 0.75-0.90:** Bueno
- **ICC > 0.90:** Excelente

---

## Sistema de Alertas

El sistema genera alertas automáticas cuando detecta:

### Alertas Críticas (Rojo)
- 🔴 Momento excesivo (> 2.5 Nm/kg)
- 🔴 GRF excesiva en aterrizaje (> 6.0 × PC)
- 🔴 Tasa de carga muy alta (> 100 BW/s)
- 🔴 Patrón de valgo dinámico

### Alertas de Advertencia (Amarillo)
- 🟡 ROM fuera de rango (< 60° o > 130°)
- 🟡 Asimetría significativa (> 15%)
- 🟡 Calidad de señal baja (< 60%)

### Alertas Informativas (Azul)
- 🔵 Valores dentro de rango normal
- 🔵 Sesión completada exitosamente

---

## Solución de Problemas

### Sensores IMU no se conectan
- Verificar que Bluetooth esté activado
- Asegurar que sensores tengan batería
- Reiniciar sensores y PC si es necesario
- Verificar que no estén conectados a otro dispositivo

### Datos de Valkyria no se importan
- Verificar formato del archivo Excel
- Confirmar que columnas tengan nombres correctos:
  - "Time (s)", "Fx (N)", "Fy (N)", "Fz (N)", "Mx (Nm)", "My (Nm)", "Mz (Nm)"
- Verificar que archivo no esté corrupto

### Error en sincronización
- Verificar que ambas capturas cubran el mismo movimiento
- Aumentar duración de captura si es muy corta
- Verificar que haya señal de movimiento clara en ambos sistemas

### OpenSim no se encuentra
- Verificar instalación de OpenSim 4.5
- Verificar que `opensim` esté instalado en Python:
  ```bash
  python -c "import opensim; print(opensim.__version__)"
  ```
- Configurar ruta del modelo en `config/settings.py`

### Interfaz se congela
- Verificar que procesamiento asíncrono esté activo
- Reducir tamaño de datos si es muy grande
- Aumentar RAM disponible

---

## Soporte y Contacto

**Proyecto de Grado - Ingeniería Biomédica**
**Universidad Antonio Nariño (UAN)**

Para dudas, reportar bugs o sugerencias:
- Crear un issue en el repositorio
- Contactar al equipo de desarrollo

---

## Referencias Científicas

### Valores de Referencia
- **Squat:** Escamilla et al. (2001), Schoenfeld (2010)
- **CMJ:** Linthorne (2001), Bobbert et al. (1996)
- **Loading Rate:** Zadpoor & Nikooyan (2011)

### Validación
- **ICC:** Koo & Li (2016), Shrout & Fleiss (1979)
- **IMU vs Optical:** Robert-Lachaine et al. (2017)

### Biomecánica
- **OpenSim:** Delp et al. (2007), Seth et al. (2018)
- **Knee Biomechanics:** Mündermann et al. (2005)

---

## Licencia

Este proyecto es parte de un trabajo académico de grado.
Desarrollado para fines educativos y de investigación.

---

## Agradecimientos

- Universidad Antonio Nariño - Programa de Ingeniería Biomédica
- Movidy Lab
- Comunidad OpenSim
- Xsens Technologies
- Involution (Plataforma Valkyria)

---

**Versión:** 1.0.0
**Última actualización:** 2025
