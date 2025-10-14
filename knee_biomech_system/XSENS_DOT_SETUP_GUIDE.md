# 📡 Guía Completa de Configuración Xsens DOT

## Sistema de Análisis Biomecánico de Rodilla
**Universidad Antonio Nariño - Ingeniería Biomédica**

---

## 📋 Contenido

1. [Introducción](#introducción)
2. [Especificaciones del Sensor](#especificaciones-del-sensor)
3. [Preparación del Hardware](#preparación-del-hardware)
4. [Colocación de Sensores](#colocación-de-sensores)
5. [Conexión Bluetooth](#conexión-bluetooth)
6. [Calibración en N-Pose](#calibración-en-n-pose)
7. [Captura de Datos](#captura-de-datos)
8. [Solución de Problemas](#solución-de-problemas)

---

## 🎯 Introducción

Los sensores **Xsens DOT** (también conocidos como **Movella DOT**) son dispositivos IMU (Inertial Measurement Unit) inalámbricos de alta precisión que miden:
- **Orientación** (cuaterniones/ángulos de Euler)
- **Aceleración lineal** (3 ejes, hasta 16g)
- **Velocidad angular** (3 ejes, hasta 2000°/s)

Este sistema utiliza **7 sensores** colocados estratégicamente en el cuerpo para capturar cinemática de rodilla durante movimientos funcionales.

---

## 📊 Especificaciones del Sensor

### Características Técnicas

| Especificación | Valor |
|----------------|-------|
| **Rango de aceleración** | ±16 g |
| **Rango giroscopio** | ±2000 deg/s |
| **Frecuencias soportadas** | 1, 4, 10, 12, 15, 20, 30, 60, 120 Hz |
| **Resolución acelerómetro** | 0.000488 g/LSB (16-bit) |
| **Resolución giroscopio** | 0.061 deg/s/LSB (16-bit) |
| **Conectividad** | Bluetooth 5.0 BLE |
| **Batería** | 150 mAh (6-12 horas) |
| **Dimensiones** | 36 × 30 × 11 mm |
| **Peso** | 11.2 g |
| **Resistencia al agua** | IPX7 (sumergible hasta 1m) |

### Modos de Salida de Datos

1. **Complete Quaternion** (recomendado)
   - Cuaternión de orientación
   - Aceleración lineal libre (sin gravedad)
   - Velocidad angular

2. **Rate Quantities**
   - Solo velocidad angular + aceleración
   - Menor latencia

3. **Extended Modes**
   - Incluyen magnetómetro (no usado en este sistema)

---

## 🔧 Preparación del Hardware

### Materiales Necesarios

- ✅ **7 sensores Xsens DOT** con baterías cargadas
- ✅ **Banda elástica adhesiva** (Velcro o cinta médica)
- ✅ **Cable USB-C** para cargar sensores
- ✅ **Computador con Bluetooth 5.0** (Windows/Mac/Linux)
- ✅ **Alcohol isopropílico** (opcional, para limpiar piel)

### Carga de Baterías

1. Conectar cada sensor con cable USB-C
2. **LED indicador**:
   - 🔴 Rojo: Cargando
   - 🟢 Verde: Carga completa
3. Tiempo de carga: ~2 horas
4. **Verificar antes de cada sesión**: Mínimo 50% de batería

### Encendido de Sensores

1. **Presionar botón** en el sensor durante 2 segundos
2. **LED azul parpadeando**: Sensor encendido y listo para emparejar
3. **LED azul fijo**: Sensor conectado
4. **LED rojo parpadeando**: Batería baja (< 10%)

Para **apagar**: Presionar botón 5 segundos (LED rojo parpadeando → apagado)

---

## 📍 Colocación de Sensores

### Ubicaciones Anatómicas (7 Sensores)

```
        👤 Vista Frontal

    1. PELVIS (Sacro)
       └─ Centro de la pelvis

    2-3. FÉMUR DERECHO/IZQUIERDO
       └─ Tercio medio del muslo

    4-5. TIBIA DERECHA/IZQUIERDA
       └─ Tercio medio de la pantorrilla

    6-7. PIE DERECHO/IZQUIERDO
       └─ Dorso del pie (empeine)
```

### Instrucciones de Colocación

#### 1. **Pelvis** (1 sensor)
- **Ubicación**: Centro del sacro (parte baja de la espalda)
- **Orientación**:
  - Eje Y apuntando hacia arriba
  - Eje X apuntando hacia adelante
- **Fijación**: Banda elástica alrededor de la cintura
- **Nota**: Debe quedar firmemente sujeto, sin movimiento relativo

#### 2-3. **Fémur (Muslo)** (2 sensores)
- **Ubicación**: Cara anterior del muslo, tercio medio
- **Orientación**:
  - Eje Y apuntando hacia la rodilla
  - Eje X apuntando hacia adelante
- **Fijación**: Banda elástica o Velcro
- **Importante**: NO colocar sobre músculo muy prominente (evitar movimiento del sensor con contracción)

#### 4-5. **Tibia (Pantorrilla)** (2 sensores)
- **Ubicación**: Cara anterior de la tibia (hueso), tercio medio
- **Orientación**:
  - Eje Y apuntando hacia el tobillo
  - Eje X apuntando hacia adelante
- **Fijación**: Banda elástica o cinta médica
- **Nota**: Colocar directamente sobre hueso para minimizar artefactos de tejido blando

#### 6-7. **Pie** (2 sensores)
- **Ubicación**: Dorso del pie (empeine)
- **Orientación**:
  - Eje Y apuntando hacia los dedos
  - Eje X apuntando hacia arriba
- **Fijación**: Velcro o cinta sobre el zapato
- **Alternativa**: Puede fijarse en el talón del zapato si hay interferencia

### Diagrama de Ejes del Sensor

```
        Z (azul)
        ↑
        |
        |_____ X (rojo)
       /
      /
     Y (verde)
```

- **X (rojo)**: Hacia adelante del cuerpo
- **Y (verde)**: Hacia abajo (dirección distal)
- **Z (azul)**: Hacia la derecha (lateral)

### Checklist de Colocación

Antes de calibrar, verificar:

- [ ] Los 7 sensores están firmemente fijados
- [ ] No hay movimiento relativo entre sensor y segmento
- [ ] La orientación de cada sensor es consistente
- [ ] Los sensores están encendidos (LED azul parpadeando)
- [ ] Batería suficiente en todos los sensores (> 50%)
- [ ] No hay ropa suelta interfiriendo con los sensores

---

## 📶 Conexión Bluetooth

### Requisitos del Sistema

- **Windows**: Windows 10/11 con Bluetooth 5.0
- **macOS**: macOS 10.15+ con Bluetooth 5.0
- **Linux**: BlueZ 5.50+ con soporte BLE

### Instalación de Dependencias

```bash
# Activar entorno virtual
cd "c:\Dev\TESIS INGRID\knee_biomech_system"
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Instalar bleak para Bluetooth
pip install bleak
```

### Proceso de Conexión (desde la Aplicación)

1. **Abrir aplicación**:
   ```bash
   python main.py
   ```

2. **Ir a pestaña "🎯 Captura"**

3. **Escanear sensores**:
   - Clic en **"🔍 Escanear Sensores"**
   - Esperar 10 segundos
   - Se mostrarán todos los Xsens DOT encontrados con su dirección MAC

4. **Asignar sensores a ubicaciones**:
   ```
   Sensor encontrado: "Xsens DOT E4:5F:01:AB:CD:EF"
   Asignar a: [Dropdown: Pelvis / Fémur Derecho / ...]
   ```

5. **Conectar todos**:
   - Clic en **"🔌 Conectar Todos"**
   - Progreso individual por sensor
   - ✅ Verde: Conectado
   - 🔴 Rojo: Error

### Conexión Manual (Código Python)

```python
import asyncio
from core.data_acquisition.imu_handler import IMUHandler

async def connect_sensors():
    handler = IMUHandler()

    # Escanear
    sensors = await handler.scan_sensors(duration=10.0)
    print(f"Encontrados: {len(sensors)} sensores")

    # Mapeo manual (ajustar direcciones MAC)
    mapping = {
        "pelvis": "E4:5F:01:AB:CD:01",
        "femur_right": "E4:5F:01:AB:CD:02",
        "femur_left": "E4:5F:01:AB:CD:03",
        "tibia_right": "E4:5F:01:AB:CD:04",
        "tibia_left": "E4:5F:01:AB:CD:05",
        "foot_right": "E4:5F:01:AB:CD:06",
        "foot_left": "E4:5F:01:AB:CD:07"
    }

    # Conectar
    success = await handler.connect_all_sensors(mapping)
    print(f"Conexión exitosa: {success}")

    # Configurar (60 Hz, modo Complete Quaternion)
    await handler.configure_all_sensors(output_rate=60)

    return handler

# Ejecutar
handler = asyncio.run(connect_sensors())
```

---

## 🎯 Calibración en N-Pose

### ¿Qué es la N-Pose?

La **N-pose** (Neutral Pose) es una posición estática de referencia que permite al sistema establecer la orientación inicial de todos los segmentos corporales. Es **CRÍTICA** para obtener datos precisos.

### Instrucciones de N-Pose

```
        👤 Vista Frontal

        O   ← Cabeza mirando hacia adelante
       /|\  ← Brazos relajados a los lados
        |   ← Tronco recto
       / \  ← Pies separados al ancho de hombros
```

**Posición exacta**:
1. **De pie** sobre superficie plana
2. **Pies** separados al ancho de hombros, paralelos
3. **Rodillas** completamente extendidas (pero no hiperextendidas)
4. **Caderas** en posición neutra
5. **Tronco** erguido, mirando hacia adelante
6. **Brazos** relajados a los lados del cuerpo
7. **Manos** con palmas hacia los muslos
8. **Cabeza** mirando al frente (horizonte)

### Proceso de Calibración

#### Desde la Aplicación

1. **Colocar al sujeto en N-pose**
2. **Verificar que está inmóvil**
3. **Clic en "⚙️ Calibrar Sensores"**
4. **Aparecer instrucciones en pantalla**:
   ```
   ============================================================
   ⚠️  INSTRUCCIONES DE N-POSE:
      1. Estar de pie con pies separados al ancho de hombros
      2. Brazos relajados a los lados del cuerpo
      3. Mirar hacia adelante
      4. Permanecer COMPLETAMENTE INMÓVIL durante 5s
   ============================================================
   ```
5. **Contar 5 segundos** (barra de progreso visible)
6. **✅ "Calibración completada"**

#### Programáticamente

```python
import asyncio

async def calibrate():
    # handler ya conectado

    print("Preparar sujeto en N-pose...")
    input("Presionar ENTER cuando esté listo...")

    # Calibrar (5 segundos)
    success = await handler.calibrate_all_sensors(duration=5.0)

    if success:
        print("✅ Todos los sensores calibrados")
    else:
        print("❌ Error en calibración")

    return success

asyncio.run(calibrate())
```

### Verificación de Calibración

Después de calibrar, verificar:

- [ ] **Sin errores** en el log
- [ ] **Todos los sensores** muestran "✅ Calibrado"
- [ ] **Orientación** de sensores es consistente (verificar con movimientos simples)

### Cuándo Re-calibrar

**SIEMPRE re-calibrar** si:
- ❌ Un sensor se ha movido o aflojado
- ❌ Se ha reiniciado un sensor
- ❌ Han pasado más de 30 minutos
- ❌ Los datos de movimiento parecen incorrectos

---

## 📊 Captura de Datos

### Configuración de Captura

**Parámetros recomendados**:
- **Frecuencia**: 60 Hz (equilibrio entre resolución y batería)
- **Modo**: Complete Quaternion
- **Duración**: 10-30 segundos por ejercicio
- **Repeticiones**: 3-5 por condición

### Proceso de Captura

1. **Preparación**:
   - Sensores conectados ✅
   - Sensores calibrados ✅
   - Plataforma de fuerza calibrada ✅
   - Sujeto en posición inicial

2. **Iniciar captura**:
   - Clic en **"▶ Iniciar Grabación"**
   - LED de sensores cambia a azul fijo (streaming activo)

3. **Ejecutar movimiento**:
   - Sujeto realiza ejercicio (squat, salto, etc.)
   - Visualización en tiempo real de GRF y ángulos

4. **Detener captura**:
   - Clic en **"■ Detener Grabación"**
   - Datos guardados en buffer

5. **Analizar**:
   - Clic en **"🔬 Analizar Datos"**
   - Procesamiento automático (5-10s)
   - Resultados en pestaña "Análisis"

### Ejemplo de Sesión Completa

```python
import asyncio
from core.data_acquisition.imu_handler import IMUHandler

async def complete_session():
    handler = IMUHandler()

    # 1. Escanear y conectar
    print("1. Escaneando...")
    sensors = await handler.scan_sensors(10.0)

    mapping = {  # Ajustar con direcciones reales
        "pelvis": sensors[0]['address'],
        # ... resto de sensores
    }

    await handler.connect_all_sensors(mapping)

    # 2. Configurar (60 Hz)
    print("2. Configurando...")
    await handler.configure_all_sensors(output_rate=60)

    # 3. Calibrar
    print("3. Calibrando (posición N-pose)...")
    input("Presionar ENTER cuando esté en N-pose...")
    await handler.calibrate_all_sensors(duration=5.0)

    # 4. Grabar
    print("4. Grabando datos...")
    await handler.start_recording()

    print("Realizar movimiento...")
    await asyncio.sleep(10)  # 10 segundos de captura

    await handler.stop_recording()

    # 5. Obtener datos
    data = handler.get_all_data()
    print(f"Capturados {len(data['pelvis'])} muestras por sensor")

    # 6. Desconectar
    await handler.disconnect_all_sensors()

    return data

# Ejecutar
data = asyncio.run(complete_session())
```

---

## 🔧 Solución de Problemas

### Problema 1: No se encuentran sensores en escaneo

**Posibles causas**:
- ❌ Sensores apagados
- ❌ Bluetooth desactivado en PC
- ❌ Sensores ya conectados a otra aplicación
- ❌ Interferencia Bluetooth

**Soluciones**:
1. Verificar LED azul parpadeando en sensores
2. Activar Bluetooth en configuración del sistema
3. Cerrar Movella DOT app u otras aplicaciones
4. Alejar otros dispositivos Bluetooth
5. Reiniciar sensores (apagar/encender)

### Problema 2: Error al conectar sensores

**Síntoma**: `TimeoutError` o `BleakError`

**Soluciones**:
1. Acercar sensor al computador (< 2 metros)
2. Aumentar timeout de conexión:
   ```python
   await sensor.connect(address, timeout=20.0)  # 20s
   ```
3. Reiniciar Bluetooth del sistema
4. Reiniciar sensor específico

### Problema 3: Datos de calibración insuficientes

**Síntoma**: `"Muestras insuficientes para calibración"`

**Causas**:
- Sensor no está streaming
- Pérdida de conexión durante calibración
- Movimiento durante calibración

**Soluciones**:
1. Verificar conexión estable
2. Aumentar duración de calibración:
   ```python
   await handler.calibrate_all_sensors(duration=10.0)  # 10s
   ```
3. Asegurar inmovilidad completa del sujeto

### Problema 4: Batería baja durante sesión

**Síntoma**: LED rojo parpadeando, sensor se desconecta

**Prevención**:
- Cargar completamente antes de cada sesión
- Leer nivel de batería antes de calibrar:
  ```python
  battery = await sensor.read_battery_level()
  print(f"Batería: {battery}%")
  ```
- Tener sensores de repuesto cargados

### Problema 5: Datos ruidosos o incorrectos

**Causas**:
- Sensor mal colocado (movimiento relativo)
- Sin calibración o calibración incorrecta
- Interferencia electromagnética

**Soluciones**:
1. Re-colocar sensor firmemente
2. Re-calibrar en N-pose correcta
3. Alejar fuentes de interferencia (WiFi, motores)
4. Verificar orientación del sensor
5. Aumentar frecuencia de muestreo si es necesario

### Problema 6: Sincronización pobre con plataforma de fuerza

**Síntoma**: Calidad de sincronización < 0.7

**Soluciones**:
1. Usar marcador de evento manual (golpe en plataforma al inicio)
2. Verificar que IMU y fuerza capturan simultáneamente
3. Revisar timestamps en datos crudos
4. Ajustar método de sincronización en settings.py

---

## 📚 Referencias y Recursos

### Documentación Oficial
- [Xsens DOT User Manual](https://www.xsens.com/hubfs/Downloads/Manuals/Xsens%20DOT%20User%20Manual.pdf)
- [BLE Services Specification](https://www.xsens.com/hubfs/Downloads/Manuals/Xsens%20DOT%20BLE%20Services%20Specifications.pdf)
- [Movella DOT Website](https://www.movella.com/products/wearables/movella-dot)

### Archivos del Proyecto
- `core/data_acquisition/imu_handler.py` - Implementación Python
- `core/data_acquisition/xsens_dot_protocol.py` - Protocolo BLE
- `config/settings.py` - Configuración de sensores

### Soporte Técnico
- **Movella Support**: support@movella.com
- **Base de Conocimiento**: https://base.movella.com/

---

## ✅ Checklist Pre-Sesión

Antes de cada sesión de captura:

- [ ] **Hardware**
  - [ ] 7 sensores cargados (> 50%)
  - [ ] Bandas elásticas/Velcro disponibles
  - [ ] Plataforma de fuerza calibrada
  - [ ] Bluetooth activado en PC

- [ ] **Software**
  - [ ] Aplicación iniciada sin errores
  - [ ] Bleak instalado (`pip list | grep bleak`)
  - [ ] Logs accesibles (`logs/app.log`)

- [ ] **Sujeto**
  - [ ] Consentimiento informado firmado
  - [ ] Datos antropométricos registrados
  - [ ] Ropa apropiada (licra, shorts)
  - [ ] Instrucciones de movimiento entendidas

- [ ] **Colocación**
  - [ ] Sensores firmemente fijados
  - [ ] Orientación correcta verificada
  - [ ] Sin interferencias de ropa

- [ ] **Conexión y Calibración**
  - [ ] 7 sensores escaneados
  - [ ] 7 sensores conectados
  - [ ] 7 sensores configurados (60 Hz)
  - [ ] 7 sensores calibrados en N-pose

**¡Listo para capturar!** 🚀

---

**Última actualización**: Octubre 14, 2025
**Versión del documento**: 1.0
**Estado**: ✅ **COMPLETO Y VALIDADO**
