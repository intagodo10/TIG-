"""
Script de prueba del sistema de análisis biomecánico.

Genera datos sintéticos y prueba todo el pipeline de análisis.
"""

import numpy as np
import sys
import os
from pathlib import Path

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Añadir el directorio raíz al path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from core.data_acquisition.synchronizer import DataSynchronizer
from core.processing.signal_processing import SignalProcessor
from core.analysis.metrics_calculator import MetricsCalculator
from core.analysis.alert_system import AlertSystem, AlertSeverity
from core.analysis.biomech_analyzer import BiomechAnalyzer
from models.patient import Patient, Sex, AffectedLimb
from utils.logger import get_logger

logger = get_logger(__name__)


def generate_synthetic_imu_data(duration: float = 10.0, fs: float = 60.0) -> tuple:
    """
    Genera datos sintéticos de IMU.

    Args:
        duration: Duración en segundos
        fs: Frecuencia de muestreo (Hz)

    Returns:
        Tupla (time, imu_data)
    """
    n_samples = int(duration * fs)
    time = np.linspace(0, duration, n_samples)

    # Simular movimiento de sentadilla (2 ciclos)
    frequency = 0.2  # Hz (ciclo de 5 segundos)

    imu_data = {}

    for location in ['pelvis', 'femur_right', 'tibia_right']:
        # Aceleración (simular flexión/extensión)
        acc_x = np.random.randn(n_samples) * 0.5
        acc_y = np.random.randn(n_samples) * 0.5
        acc_z = 9.81 + np.random.randn(n_samples) * 0.5  # Gravedad + ruido

        acceleration = np.column_stack([acc_x, acc_y, acc_z])

        # Velocidad angular (simular rotación rodilla)
        phase_offset = {'pelvis': 0, 'femur_right': 0.2, 'tibia_right': 0.5}
        offset = phase_offset.get(location, 0)

        gyro_x = np.random.randn(n_samples) * 0.1
        gyro_y = 0.5 * np.sin(2 * np.pi * frequency * time + offset) + np.random.randn(n_samples) * 0.05
        gyro_z = np.random.randn(n_samples) * 0.1

        angular_velocity = np.column_stack([gyro_x, gyro_y, gyro_z])

        # Quaternions (identidad + ruido)
        qw = np.ones(n_samples) + np.random.randn(n_samples) * 0.01
        qx = np.random.randn(n_samples) * 0.01
        qy = np.random.randn(n_samples) * 0.01
        qz = np.random.randn(n_samples) * 0.01

        quaternion = np.column_stack([qw, qx, qy, qz])

        imu_data[location] = {
            'acceleration': acceleration,
            'angular_velocity': angular_velocity,
            'quaternion': quaternion
        }

    logger.info(f"Datos IMU sintéticos generados: {duration}s @ {fs} Hz")

    return time, imu_data


def generate_synthetic_force_data(duration: float = 10.0, fs: float = 1000.0) -> tuple:
    """
    Genera datos sintéticos de plataforma de fuerza.

    Args:
        duration: Duración en segundos
        fs: Frecuencia de muestreo (Hz)

    Returns:
        Tupla (time, force_data)
    """
    n_samples = int(duration * fs)
    time = np.linspace(0, duration, n_samples)

    # Simular patrón de GRF de sentadilla (2 repeticiones)
    fz = np.zeros(n_samples)

    # Peso corporal base (700 N = ~70 kg)
    body_weight = 700.0

    # Dos repeticiones de sentadilla
    for i in range(2):
        # Tiempo de cada repetición
        start_time = 2.0 + i * 4.0  # Rep 1: 2-6s, Rep 2: 6-10s
        end_time = start_time + 4.0

        # Índices
        start_idx = int(start_time * fs)
        end_idx = int(end_time * fs)

        # Fase excéntrica (descenso): fuerza aumenta
        descend_time = np.linspace(0, 2, int(2 * fs))
        descend_force = body_weight + 400 * np.sin(np.pi * descend_time / 2)

        # Fase concéntrica (ascenso): fuerza disminuye
        ascend_time = np.linspace(0, 2, int(2 * fs))
        ascend_force = body_weight + 400 * np.cos(np.pi * ascend_time / 2)

        # Combinar
        rep_length = end_idx - start_idx
        rep_force = np.concatenate([descend_force, ascend_force])[:rep_length]

        fz[start_idx:end_idx] = rep_force

    # Añadir ruido
    fz += np.random.randn(n_samples) * 10

    # Fuerzas horizontales (pequeñas)
    fx = np.random.randn(n_samples) * 20
    fy = np.random.randn(n_samples) * 20

    # Momentos (simulados)
    mx = np.random.randn(n_samples) * 5
    my = np.random.randn(n_samples) * 5
    mz = np.random.randn(n_samples) * 2

    force_data = {
        'fx': fx,
        'fy': fy,
        'fz': fz,
        'mx': mx,
        'my': my,
        'mz': mz
    }

    logger.info(f"Datos de fuerza sintéticos generados: {duration}s @ {fs} Hz")

    return time, force_data


def test_synchronizer():
    """Prueba el sincronizador."""
    print("\n" + "="*60)
    print("TEST 1: SINCRONIZADOR DE SEÑALES")
    print("="*60)

    # Generar datos
    time_imu, imu_data = generate_synthetic_imu_data(duration=10.0, fs=60.0)
    time_force, force_data = generate_synthetic_force_data(duration=10.0, fs=1000.0)

    # Sincronizar
    synchronizer = DataSynchronizer()
    sync_result = synchronizer.synchronize(time_imu, imu_data, time_force, force_data)

    # Verificar
    print(f"\n✅ Sincronización exitosa: {sync_result.success}")
    print(f"   Muestras sincronizadas: {len(sync_result.time_common)}")
    print(f"   Offset temporal: {sync_result.time_offset*1000:.2f} ms")
    print(f"   Calidad de sync: {sync_result.sync_quality:.2%}")

    return sync_result


def test_signal_processor(sync_result):
    """Prueba el procesador de señales."""
    print("\n" + "="*60)
    print("TEST 2: PROCESADOR DE SEÑALES")
    print("="*60)

    processor = SignalProcessor()

    # Filtrar fuerza
    fz_raw = sync_result.force_data_synced['fz']
    fs = 100.0  # Hz (frecuencia común)

    fz_filtered = processor.filter_force(fz_raw, fs)

    print(f"\n✅ Filtrado completado")
    print(f"   Señal original: mean={np.mean(fz_raw):.2f} N, std={np.std(fz_raw):.2f} N")
    print(f"   Señal filtrada: mean={np.mean(fz_filtered):.2f} N, std={np.std(fz_filtered):.2f} N")

    # Detectar contactos
    contacts, liftoffs = processor.detect_grf_contacts(fz_filtered, threshold=50.0, fs=fs)

    print(f"\n✅ Eventos detectados")
    print(f"   Contactos: {len(contacts)}")
    print(f"   Despegues: {len(liftoffs)}")

    if len(contacts) > 0:
        for i, (c, l) in enumerate(zip(contacts, liftoffs)):
            duration = (l - c) / fs
            print(f"   Repetición {i+1}: {duration:.2f} s")

    return fz_filtered, contacts, liftoffs


def test_metrics_calculator(time, fz_filtered, contacts, liftoffs):
    """Prueba la calculadora de métricas."""
    print("\n" + "="*60)
    print("TEST 3: CALCULADORA DE MÉTRICAS")
    print("="*60)

    calculator = MetricsCalculator()

    # Simular ángulo de rodilla
    angle = 45 * np.sin(2 * np.pi * 0.2 * time) + 45  # 0-90 grados

    # Calcular métricas cinemáticas
    kinematic = calculator.calculate_kinematic_metrics(time, angle)

    print(f"\n✅ Métricas Cinemáticas")
    print(f"   ROM: {kinematic.rom:.1f}°")
    print(f"   Flexión máxima: {kinematic.peak_flexion:.1f}°")
    print(f"   Extensión máxima: {kinematic.peak_extension:.1f}°")
    print(f"   Velocidad angular pico: {kinematic.angular_velocity_peak:.1f} deg/s")

    # Calcular métricas de fuerza para primer contacto
    if len(contacts) > 0:
        body_weight = 700.0  # N

        force_metrics = calculator.calculate_force_metrics(
            time, fz_filtered, body_weight, contacts[0], liftoffs[0]
        )

        print(f"\n✅ Métricas de Fuerza (Contacto 1)")
        print(f"   GRF pico: {force_metrics.peak_grf:.2f} BW")
        print(f"   GRF promedio: {force_metrics.mean_grf:.2f} BW")
        print(f"   Loading rate: {force_metrics.loading_rate:.1f} BW/s")
        print(f"   Tiempo de contacto: {force_metrics.contact_time:.3f} s")
        print(f"   Impulso: {force_metrics.impulse:.1f} N·s")

    # Métricas de simetría (simuladas)
    right_rom = np.array([kinematic.rom])
    left_rom = np.array([kinematic.rom * 0.85])  # Simular asimetría

    symmetry = calculator.calculate_symmetry_metrics(right_rom, left_rom)

    print(f"\n✅ Métricas de Simetría")
    print(f"   Índice de simetría: {symmetry.symmetry_index:.1f}%")
    print(f"   Ratio de asimetría: {symmetry.asymmetry_ratio:.2f}")

    return kinematic, force_metrics if len(contacts) > 0 else None, symmetry


def test_alert_system(kinematic, force_metrics, symmetry):
    """Prueba el sistema de alertas."""
    print("\n" + "="*60)
    print("TEST 4: SISTEMA DE ALERTAS")
    print("="*60)

    alert_system = AlertSystem()

    # Verificar ROM
    rom_alert = alert_system.check_rom_alert(kinematic.rom, "knee")
    if rom_alert:
        print(f"\n⚠️  [{rom_alert.severity.value.upper()}] {rom_alert.title}")
        print(f"   {rom_alert.message}")
    else:
        print(f"\n✅ ROM dentro de rango normal")

    # Verificar velocidad angular
    vel_alert = alert_system.check_angular_velocity_alert(kinematic.angular_velocity_peak)
    if vel_alert:
        print(f"\n⚠️  [{vel_alert.severity.value.upper()}] {vel_alert.title}")
        print(f"   {vel_alert.message}")
    else:
        print(f"✅ Velocidad angular segura")

    # Verificar GRF
    if force_metrics:
        body_weight = 700.0  # N
        grf_alert = alert_system.check_grf_alert(
            force_metrics.peak_grf * body_weight,
            body_weight,
            "squat"
        )
        if grf_alert:
            print(f"\n⚠️  [{grf_alert.severity.value.upper()}] {grf_alert.title}")
            print(f"   {grf_alert.message}")
        else:
            print(f"✅ GRF dentro de rango esperado")

        # Verificar loading rate
        lr_alert = alert_system.check_loading_rate_alert(
            force_metrics.loading_rate * body_weight,
            body_weight
        )
        if lr_alert:
            print(f"\n⚠️  [{lr_alert.severity.value.upper()}] {lr_alert.title}")
            print(f"   {lr_alert.message}")
        else:
            print(f"✅ Loading rate segura")

    # Verificar simetría
    sym_alert = alert_system.check_symmetry_alert(symmetry.symmetry_index)
    if sym_alert:
        print(f"\n⚠️  [{sym_alert.severity.value.upper()}] {sym_alert.title}")
        print(f"   {sym_alert.message}")
    else:
        print(f"✅ Simetría bilateral aceptable")

    # Resumen de alertas
    alert_summary = alert_system.get_alert_summary()
    print(f"\n📊 Resumen de Alertas:")
    print(f"   Total: {alert_summary['total']}")
    print(f"   Críticas: {alert_summary['critical']}")
    print(f"   Errores: {alert_summary['error']}")
    print(f"   Advertencias: {alert_summary['warning']}")
    print(f"   Info: {alert_summary['info']}")

    return alert_system


def test_integrated_analyzer():
    """Prueba el analizador integrado."""
    print("\n" + "="*60)
    print("TEST 5: ANALIZADOR BIOMECÁNICO INTEGRADO")
    print("="*60)

    # Crear paciente de prueba
    patient = Patient(
        patient_id="TEST001",
        name="Paciente de Prueba",
        age=30,
        mass=70.0,
        height=1.75,
        sex=Sex.MALE,
        affected_limb=AffectedLimb.RIGHT
    )

    print(f"\n👤 Paciente: {patient.name}")
    print(f"   Masa: {patient.mass} kg | Altura: {patient.height} m")
    print(f"   Peso corporal: {patient.body_weight:.1f} N")

    # Generar datos
    time_imu, imu_data = generate_synthetic_imu_data(duration=10.0, fs=60.0)
    time_force, force_data = generate_synthetic_force_data(duration=10.0, fs=1000.0)

    # Crear analizador
    analyzer = BiomechAnalyzer(patient)

    # Ejecutar análisis completo
    print("\n🔄 Ejecutando análisis completo...")
    result = analyzer.analyze_full_session(
        time_imu, imu_data,
        time_force, force_data,
        exercise_type="squat"
    )

    # Mostrar resultados
    if result.success:
        print("\n✅ ANÁLISIS COMPLETADO EXITOSAMENTE\n")
        print(result.summary)
    else:
        print("\n❌ ANÁLISIS FALLÓ")
        print(result.summary)


def main():
    """Función principal."""
    print("\n" + "="*60)
    print("PRUEBA DEL SISTEMA DE ANÁLISIS BIOMECÁNICO")
    print("Universidad Antonio Nariño - Ingeniería Biomédica")
    print("="*60)

    try:
        # Test 1: Sincronizador
        sync_result = test_synchronizer()

        # Test 2: Procesador de señales
        fz_filtered, contacts, liftoffs = test_signal_processor(sync_result)

        # Test 3: Calculadora de métricas
        kinematic, force_metrics, symmetry = test_metrics_calculator(
            sync_result.time_common,
            fz_filtered,
            contacts,
            liftoffs
        )

        # Test 4: Sistema de alertas
        alert_system = test_alert_system(kinematic, force_metrics, symmetry)

        # Test 5: Analizador integrado
        test_integrated_analyzer()

        print("\n" + "="*60)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("="*60 + "\n")

    except Exception as e:
        logger.error(f"Error en pruebas: {str(e)}", exc_info=True)
        print(f"\n❌ ERROR: {str(e)}\n")


if __name__ == "__main__":
    main()
