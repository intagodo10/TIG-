# Guía de Uso: Captura de Datos con Sensores IMU Xsens DOT

## 📋 Tabla de Contenidos

1. [Preparación Inicial](#preparación-inicial)
2. [Workflow Completo de Captura](#workflow-completo-de-captura)
3. [Uso de la Interfaz](#uso-de-la-interfaz)
4. [Solución de Problemas](#solución-de-problemas)
5. [Consejos para Mejores Resultados](#consejos-para-mejores-resultados)

---

## 🔧 Preparación Inicial

### Requisitos Previos

- ✅ Python 3.10.11 instalado
- ✅ Todas las dependencias instaladas (`pip install -r requirements.txt`)
- ✅ Bluetooth activado en el computador
- ✅ 7 sensores Xsens DOT cargados completamente
- ✅ Aplicación iniciada (`python main.py`)

### Encender los Sensores

1. **Presionar y mantener** el botón en cada sensor durante ~3 segundos
2. **LED debe parpadear en AZUL** (modo emparejamiento BLE)
3. Si el LED es rojo/naranja, el sensor está en modo USB (presionar botón de nuevo)
4. **Verificar batería**: LED verde sólido = >70%, naranja = 30-70%, rojo = <30%

### Colocación de Sensores

Los sensores deben colocarse en las siguientes **7 ubicaciones anatómicas**:

| # | Ubicación | Posición Exacta | Orientación |
|---|-----------|----------------|-------------|
| 1 | **Pelvis** | Sacro (S2), parte baja de la espalda | Logo Xsens hacia arriba |
| 2 | **Fémur Derecho** | Cara lateral externa del muslo (1/3 superior) | Logo hacia arriba y adelante |
| 3 | **Fémur Izquierdo** | Cara lateral externa del muslo (1/3 superior) | Logo hacia arriba y adelante |
| 4 | **Tibia Derecha** | Cara lateral externa de la pierna (1/3 superior) | Logo hacia arriba y adelante |
| 5 | **Tibia Izquierda** | Cara lateral externa de la pierna (1/3 superior) | Logo hacia arriba y adelante |
| 6 | **Pie Derecho** | Empeine, sobre cordones del zapato | Logo hacia arriba y adelante |
| 7 | **Pie Izquierdo** | Empeine, sobre cordones del zapato | Logo hacia arriba y adelante |

**Método de fijación**:
- Usar bandas elásticas Velcro (incluidas con Xsens DOT)
- Ajustar firmemente pero sin cortar circulación
- Verificar que no se deslicen al moverse
- **NO usar cinta adhesiva** directamente en la piel

---

## 🎯 Workflow Completo de Captura

### Paso 1: Escanear y Conectar Sensores

1. En la vista **"Captura de Datos"**, hacer clic en **"🔍 Escanear y Conectar"**
2. Se abrirá el **Diálogo de Asignación de Sensores**:
   - Se escanearán automáticamente por **10 segundos**
   - Verás una lista de sensores encontrados con:
     - Nombre (ej: "Xsens DOT-D4-12345")
     - Dirección MAC (últimos 8 caracteres)
     - Señal RSSI (calidad de conexión)

3. **Asignar cada sensor a su ubicación**:
   - En el panel derecho, verás las 7 ubicaciones anatómicas
   - Para cada ubicación, selecciona el sensor correspondiente del dropdown
   - **IMPORTANTE**: Anota qué sensor va en cada ubicación (puedes usar las etiquetas adhesivas incluidas)

4. Hacer clic en **"Confirmar Asignaciones"**

5. El sistema conectará todos los sensores (toma ~10-15 segundos)

6. **Resultado exitoso**:
   - Mensaje: "Todos los sensores se conectaron exitosamente"
   - Botón cambia a: "✓ Sensores Conectados" (verde)
   - Se habilita el botón **"📐 Calibrar (N-pose)"**

### Paso 2: Calibrar Sensores (N-Pose)

**¿Por qué calibrar?**
La calibración establece una referencia neutral para todos los sensores. Sin calibración, los ángulos articulares serán incorrectos.

**Procedimiento**:

1. Hacer clic en **"📐 Calibrar (N-pose)"**

2. Leer las **instrucciones** que aparecen:
   ```
   INSTRUCCIONES DE CALIBRACIÓN:

   1. Párate con pies separados al ancho de hombros
   2. Brazos relajados a los lados del cuerpo
   3. Mirada hacia adelante
   4. Permanece COMPLETAMENTE INMÓVIL durante 5 segundos
   ```

3. **Posicionarse correctamente** (N-Pose):
   - Postura erguida, natural
   - Pies paralelos, separados al ancho de hombros
   - Rodillas extendidas (NO hiperextendidas)
   - Brazos a los lados, palmas mirando hacia el cuerpo
   - Cabeza neutra, mirada al horizonte
   - **Respiración normal pero controlada**

4. Presionar **OK** cuando estés listo

5. **Countdown** de 3 segundos (prepárate)

6. **Permanecer INMÓVIL por 5 segundos** mientras se calibra

7. **Resultado exitoso**:
   - Mensaje: "Los sensores se calibraron correctamente"
   - Botón cambia a: "✓ Calibración Completa" (verde)
   - Estado: "Sensores calibrados - Listo para grabar"

**⚠️ IMPORTANTE**:
- Si te mueves durante la calibración, repetir el proceso
- NO recalibrar entre repeticiones del mismo ejercicio
- SÍ recalibrar si se desconecta algún sensor
- SÍ recalibrar si se mueve algún sensor de su posición

### Paso 3: Importar Datos de Plataforma de Fuerza

1. Hacer clic en **"📥 Importar Datos de Valkyria"**

2. Seleccionar el archivo Excel de la plataforma Valkyria

3. **Verificar importación exitosa**:
   - Estado: "✓ Datos importados (XX.Xs, XXXX muestras)"
   - Se mostrará el gráfico de fuerza vertical (Fz)

### Paso 4: Configurar Ejercicio

En el panel izquierdo, configurar:

- **Tipo de Ejercicio**: Seleccionar del dropdown
  - Sentadilla
  - Salto
  - Marcha
  - Carrera
  - Lunge
  - Step-up/down

- **Duración**: Tiempo estimado en segundos (referencia)

- **Repeticiones**: Número de repeticiones esperadas

### Paso 5: Grabar Datos IMU

1. **Verificar que todo esté listo**:
   - ✅ Sensores conectados (verde)
   - ✅ Sensores calibrados (verde)
   - ✅ Datos de plataforma importados

2. **Posicionar al sujeto** en la posición inicial del ejercicio

3. Hacer clic en **"▶ Iniciar Grabación"**
   - Botón cambia a: "■ Detener Grabación" (rojo)
   - Estado: "Grabando datos IMU..."

4. **El sujeto ejecuta el ejercicio** (según configuración)

5. Hacer clic en **"■ Detener Grabación"** al finalizar
   - Estado: "Procesando datos capturados..."
   - Se habilita el botón **"🔬 Analizar Datos"**

### Paso 6: Analizar Datos

1. Hacer clic en **"🔬 Analizar Datos"**

2. El sistema ejecutará automáticamente:
   - ✅ Sincronización temporal (IMU ↔ Plataforma)
   - ✅ Filtrado de señales
   - ✅ Detección de eventos (contacto inicial, despegue)
   - ✅ Cálculo de cinemática (ángulos, velocidades)
   - ✅ Cálculo de cinética (momentos, potencia)
   - ✅ Generación de alertas biomecánicas

3. **Ver resultados** en la vista de Análisis:
   - Gráficos de cinemática y cinética
   - Tabla de métricas (25+ métricas)
   - Panel de alertas (biomecánicas y técnicas)

---

## 🖥️ Uso de la Interfaz

### Panel de Sensores IMU

**Estados de los sensores**:

| Color | Estado | Significado |
|-------|--------|-------------|
| 🔴 Rojo | Disconnected | Sensor no conectado |
| 🟡 Amarillo | Connecting | Conectando al sensor |
| 🟢 Verde | Connected | Sensor conectado y funcionando |
| ⚫ Gris | Error | Error de conexión |

### Botones Principales

| Botón | Función | Cuándo usar |
|-------|---------|-------------|
| **🔍 Escanear y Conectar** | Busca sensores BLE y los conecta | Al inicio de sesión |
| **📐 Calibrar (N-pose)** | Calibra sensores en posición neutral | Después de conectar sensores |
| **📥 Importar Datos de Valkyria** | Importa datos de plataforma de fuerza | Cuando tengas el archivo Excel |
| **▶ Iniciar Grabación** | Comienza captura de datos IMU | Cuando todo esté configurado |
| **■ Detener Grabación** | Detiene captura | Al finalizar el ejercicio |
| **🔬 Analizar Datos** | Ejecuta análisis completo | Después de grabar |

---

## 🔧 Solución de Problemas

### Problema: No se encuentran sensores en escaneo

**Posibles causas y soluciones**:

1. **Sensores apagados**
   - ✅ Verificar LED azul parpadeando
   - ✅ Presionar botón por 3s para encender

2. **Bluetooth desactivado**
   - ✅ Verificar en configuración del sistema
   - ✅ Reiniciar adaptador Bluetooth

3. **Interferencia BLE**
   - ✅ Alejar de otros dispositivos Bluetooth
   - ✅ Cerrar otros programas que usen Bluetooth

4. **Sensores en modo USB**
   - ✅ Presionar botón para cambiar a modo BLE

5. **Batería baja**
   - ✅ Cargar sensores (LED verde sólido = cargado)

### Problema: Sensor se desconecta durante grabación

**Soluciones**:

1. **Distancia excesiva**
   - ✅ Mantener sujeto a <5 metros del computador
   - ✅ Asegurar línea de vista directa

2. **Batería baja**
   - ✅ Verificar nivel de batería antes de empezar
   - ✅ Sensores con <30% pueden desconectarse

3. **Interferencia electromagnética**
   - ✅ Alejar de motores, transformadores, WiFi potente

### Problema: Calibración falla

**Soluciones**:

1. **Movimiento durante calibración**
   - ✅ Permanecer COMPLETAMENTE inmóvil por 5s
   - ✅ Controlar respiración (suave)

2. **Postura incorrecta**
   - ✅ Revisar instrucciones de N-pose
   - ✅ Pies paralelos, rodillas extendidas

3. **Superficie inestable**
   - ✅ Calibrar en piso firme y nivelado
   - ✅ NO calibrar sobre alfombras gruesas

### Problema: Datos de mala calidad

**Soluciones**:

1. **Sensores mal fijados**
   - ✅ Ajustar bandas elásticas (firmes pero cómodas)
   - ✅ Verificar que no se deslicen

2. **Orientación incorrecta**
   - ✅ Logo Xsens hacia arriba en todos los sensores
   - ✅ Revisar tabla de colocación

3. **No calibrado antes de grabar**
   - ✅ SIEMPRE calibrar después de conectar
   - ✅ Recalibrar si se mueve algún sensor

### Problema: Error "Librería 'bleak' no instalada"

**Solución**:
```bash
pip install bleak>=0.19.0
```

### Problema: Análisis falla con datos reales

**Verificar**:

1. **Duración suficiente**
   - ✅ Mínimo 2-3 segundos de grabación
   - ✅ Al menos 1 repetición completa del ejercicio

2. **Sincronización temporal**
   - ✅ Datos de plataforma y IMU deben sobrelapar temporalmente
   - ✅ Iniciar plataforma antes que sensores (o viceversa)

3. **Datos completos**
   - ✅ Verificar que todos los sensores grabaron datos
   - ✅ Revisar logs para sensores sin muestras

---

## ✨ Consejos para Mejores Resultados

### Antes de Iniciar la Sesión

1. **Cargar todos los sensores** al 100% (LED verde sólido)
2. **Etiquetar sensores** con su ubicación anatómica
3. **Preparar al sujeto**: ropa ajustada, sin objetos metálicos
4. **Verificar espacio de trabajo**: piso nivelado, buena iluminación

### Durante la Colocación

1. **Colocar sensores en orden**:
   - Primero: Pelvis (referencia central)
   - Segundo: Fémures (muslos)
   - Tercero: Tibias (piernas)
   - Cuarto: Pies

2. **Verificar orientación**:
   - Logo Xsens siempre hacia arriba
   - Eje Y del sensor apunta hacia proximal (hacia el cuerpo)

3. **Ajustar firmeza**:
   - Debe poder pasar 1-2 dedos bajo la banda
   - No debe deslizarse al mover la extremidad

### Durante la Calibración

1. **Ambiente silencioso**: Minimizar distracciones
2. **Respiración controlada**: Inspirar antes, exhalar despacio durante
3. **Mirada fija**: Fijar vista en punto del horizonte
4. **Postura natural**: NO forzar rodillas o espalda

### Durante la Captura

1. **Instrucciones claras** al sujeto antes de empezar
2. **Countdown verbal**: "3, 2, 1, ¡Ya!" para sincronizar
3. **Observar ejecución**: Verificar técnica del ejercicio
4. **Múltiples repeticiones**: Capturar 3-5 repeticiones para confiabilidad

### Después de la Captura

1. **Verificar calidad de datos** inmediatamente
2. **Repetir si es necesario** (mejor prevenir que corregir)
3. **Guardar datos crudos**: Útil para re-análisis posterior
4. **Documentar anomalías**: Notar si hubo movimientos atípicos

---

## 📊 Flujo de Trabajo Recomendado

### Sesión Tipo (Duración: ~30 minutos)

1. **Preparación (5 min)**:
   - Encender sensores
   - Colocar sensores en sujeto
   - Iniciar aplicación

2. **Conexión y Calibración (5 min)**:
   - Escanear y conectar sensores
   - Calibrar en N-pose
   - Importar datos de plataforma (si disponible)

3. **Captura (15 min)**:
   - Ejercicio 1: Sentadillas (3 repeticiones)
   - Ejercicio 2: Saltos (3 repeticiones)
   - Ejercicio 3: Marcha (3 pasadas)

4. **Análisis (5 min)**:
   - Analizar cada captura
   - Revisar alertas biomecánicas
   - Exportar reportes

---

## 🔬 Verificación de Calidad

### Checklist Pre-Captura

- [ ] Todos los sensores encendidos (LED azul)
- [ ] Bluetooth activado en computador
- [ ] Sensores colocados correctamente (orientación)
- [ ] Bandas elásticas ajustadas (no se deslizan)
- [ ] Calibración N-pose completada exitosamente
- [ ] Datos de plataforma importados
- [ ] Ejercicio configurado en la interfaz

### Checklist Post-Captura

- [ ] Todos los sensores grabaron datos (ver logs)
- [ ] Duración de captura coincide con esperado
- [ ] No hay desconexiones en los logs
- [ ] Gráficos de IMU muestran patrones esperados
- [ ] Análisis completó sin errores

---

## 📞 Soporte y Referencias

### Logs del Sistema

Los logs se guardan en: `logs/knee_biomech_YYYYMMDD_HHMMSS.log`

**Nivel de detalle**:
- `INFO`: Eventos normales de operación
- `WARNING`: Situaciones anómalas pero recuperables
- `ERROR`: Errores que impiden operación
- `DEBUG`: Información técnica detallada

### Documentación Adicional

- **Guía de Setup Completa**: `XSENS_DOT_SETUP_GUIDE.md`
- **Protocolo BLE**: `core/data_acquisition/xsens_dot_protocol.py`
- **Especificaciones Xsens DOT**: [Documentación oficial Movella](https://www.movella.com/support/xsens-dot)

### Contacto Técnico

Para problemas técnicos o dudas:
1. Revisar logs del sistema
2. Consultar `XSENS_DOT_SETUP_GUIDE.md`
3. Verificar documentación del código
4. Reportar issue con logs adjuntos

---

## 🎓 Notas Finales

### Aspectos Importantes

1. **La calibración es CRÍTICA**:
   - Determina la referencia neutral de todos los ángulos
   - Una mala calibración invalida TODOS los resultados
   - Tomarse el tiempo necesario para hacerlo bien

2. **La colocación de sensores afecta la precisión**:
   - Sensores mal orientados → ángulos incorrectos
   - Sensores que se deslizan → artefactos en señales
   - Revisar colocación antes de cada captura

3. **La sincronización es automática pero requiere solapamiento**:
   - Datos de IMU y plataforma deben coincidir temporalmente
   - Iniciar plataforma y sensores con pocos segundos de diferencia

4. **Múltiples repeticiones mejoran confiabilidad**:
   - Capturar 3-5 repeticiones por ejercicio
   - Permite análisis estadístico (media ± SD)
   - Detecta inconsistencias técnicas

### Mejora Continua

Este sistema está en desarrollo continuo. Tus comentarios y sugerencias son valiosos para:
- Mejorar la usabilidad de la interfaz
- Añadir nuevas funcionalidades
- Optimizar el procesamiento de datos
- Corregir errores y bugs

**¡Buena suerte con tus capturas!** 🚀

---

*Última actualización: Octubre 2025*
*Versión del sistema: 1.0*
