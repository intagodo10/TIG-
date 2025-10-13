"""
Generador de datos de ejemplo para pruebas.

Crea archivos Excel de ejemplo que simulan datos
de la plataforma de fuerza Valkyria.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Añadir directorio raíz al path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from config.settings import RAW_DATA_DIR


def generate_squat_data(duration=10.0, sampling_rate=1000, body_weight=70.0):
    """
    Genera datos sintéticos de una sentadilla.

    Args:
        duration: Duración en segundos
        sampling_rate: Frecuencia de muestreo en Hz
        body_weight: Masa corporal en kg

    Returns:
        DataFrame con datos de fuerza
    """
    n_samples = int(duration * sampling_rate)
    time = np.linspace(0, duration, n_samples)

    # Peso corporal en Newtons
    bw_newtons = body_weight * 9.81

    # Simular 5 sentadillas
    num_squats = 5
    squat_duration = 2.0  # segundos por sentadilla
    squat_freq = 1 / squat_duration

    # Fz: Fuerza vertical (patrón de sentadilla)
    # Aumenta durante descenso, disminuye en el fondo, aumenta durante ascenso
    fz_pattern = np.zeros(n_samples)
    for i in range(num_squats):
        start_time = 1.0 + i * squat_duration
        squat_mask = (time >= start_time) & (time < start_time + squat_duration)

        # Patrón sinusoidal con offset
        squat_time = time[squat_mask] - start_time
        fz_pattern[squat_mask] = bw_newtons * (1.0 + 0.5 * np.sin(2 * np.pi * squat_freq * squat_time))

    # Agregar ruido realista
    fz = fz_pattern + np.random.normal(0, bw_newtons * 0.02, n_samples)

    # Fx y Fy: Fuerzas horizontales (pequeñas oscilaciones)
    fx = np.random.normal(0, bw_newtons * 0.05, n_samples)
    fy = np.random.normal(0, bw_newtons * 0.05, n_samples)

    # Momentos (calculados aproximadamente desde COP)
    # COP oscila ligeramente
    cop_x = np.sin(2 * np.pi * 0.5 * time) * 0.05  # ±5 cm
    cop_y = np.cos(2 * np.pi * 0.3 * time) * 0.05  # ±5 cm

    my = -fz * cop_x  # Momento alrededor Y debido a COP en X
    mx = fz * cop_y   # Momento alrededor X debido a COP en Y
    mz = np.random.normal(0, 5, n_samples)  # Momento vertical (pequeño)

    # Crear DataFrame
    df = pd.DataFrame({
        'Time (s)': time,
        'Fx (N)': fx,
        'Fy (N)': fy,
        'Fz (N)': fz,
        'Mx (Nm)': mx,
        'My (Nm)': my,
        'Mz (Nm)': mz
    })

    return df


def generate_jump_data(duration=5.0, sampling_rate=1000, body_weight=70.0, jump_type='cmj'):
    """
    Genera datos sintéticos de un salto.

    Args:
        duration: Duración en segundos
        sampling_rate: Frecuencia de muestreo en Hz
        body_weight: Masa corporal en kg
        jump_type: 'cmj' o 'squat_jump'

    Returns:
        DataFrame con datos de fuerza
    """
    n_samples = int(duration * sampling_rate)
    time = np.linspace(0, duration, n_samples)

    bw_newtons = body_weight * 9.81

    # Inicializar con peso corporal
    fz = np.full(n_samples, bw_newtons)

    # Simular 3 saltos
    num_jumps = 3
    for i in range(num_jumps):
        jump_start = 0.5 + i * 1.5

        # Fase de contra-movimiento (si es CMJ)
        if jump_type == 'cmj':
            cm_start_idx = int((jump_start - 0.15) * sampling_rate)
            cm_end_idx = int(jump_start * sampling_rate)
            cm_indices = np.arange(cm_start_idx, cm_end_idx)
            if len(cm_indices) > 0:
                fz[cm_indices] = bw_newtons * (1.0 - 0.3 * np.linspace(0, 1, len(cm_indices)))

        # Fase de propulsión
        prop_start_idx = int(jump_start * sampling_rate)
        prop_end_idx = int((jump_start + 0.3) * sampling_rate)
        prop_indices = np.arange(prop_start_idx, prop_end_idx)
        if len(prop_indices) > 0:
            # Pico de fuerza durante propulsión (2.5-3.5 × BW)
            peak_force = bw_newtons * np.random.uniform(2.5, 3.5)
            fz[prop_indices] = bw_newtons + (peak_force - bw_newtons) * np.sin(np.pi * np.linspace(0, 1, len(prop_indices)))

        # Fase de vuelo
        flight_start_idx = prop_end_idx
        flight_duration = 0.4  # ~40cm de altura
        flight_end_idx = int((jump_start + 0.3 + flight_duration) * sampling_rate)
        flight_indices = np.arange(flight_start_idx, min(flight_end_idx, n_samples))
        if len(flight_indices) > 0:
            fz[flight_indices] = np.random.normal(0, 5, len(flight_indices))  # Ruido durante vuelo

        # Fase de aterrizaje
        land_start_idx = flight_end_idx
        land_end_idx = int((jump_start + 0.3 + flight_duration + 0.2) * sampling_rate)
        land_indices = np.arange(land_start_idx, min(land_end_idx, n_samples))
        if len(land_indices) > 0:
            # Pico de impacto (3-5 × BW)
            impact_force = bw_newtons * np.random.uniform(3.0, 5.0)
            landing_curve = impact_force * np.exp(-5 * np.linspace(0, 1, len(land_indices)))
            fz[land_indices] = landing_curve

    # Fuerzas horizontales (más variación durante saltos)
    fx = np.random.normal(0, bw_newtons * 0.1, n_samples)
    fy = np.random.normal(0, bw_newtons * 0.1, n_samples)

    # Momentos
    cop_x = np.random.normal(0, 0.03, n_samples)
    cop_y = np.random.normal(0, 0.03, n_samples)

    my = -fz * cop_x
    mx = fz * cop_y
    mz = np.random.normal(0, 10, n_samples)

    # Crear DataFrame
    df = pd.DataFrame({
        'Time (s)': time,
        'Fx (N)': fx,
        'Fy (N)': fy,
        'Fz (N)': fz,
        'Mx (Nm)': mx,
        'My (Nm)': my,
        'Mz (Nm)': mz
    })

    return df


def main():
    """Genera archivos de ejemplo."""
    print("=" * 70)
    print(" GENERADOR DE DATOS DE EJEMPLO")
    print("=" * 70)
    print()

    output_dir = RAW_DATA_DIR / "ejemplos"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generar datos de sentadilla
    print("📊 Generando datos de sentadilla...")
    squat_data = generate_squat_data(duration=12.0, body_weight=70.0)
    squat_file = output_dir / "ejemplo_sentadilla_70kg.xlsx"
    squat_data.to_excel(squat_file, index=False)
    print(f"   ✓ Guardado: {squat_file}")
    print(f"      - Duración: {squat_data['Time (s)'].max():.1f}s")
    print(f"      - Muestras: {len(squat_data)}")
    print(f"      - Fz pico: {squat_data['Fz (N)'].max():.1f} N")
    print()

    # Generar datos de CMJ
    print("📊 Generando datos de CMJ...")
    cmj_data = generate_jump_data(duration=5.0, body_weight=70.0, jump_type='cmj')
    cmj_file = output_dir / "ejemplo_cmj_70kg.xlsx"
    cmj_data.to_excel(cmj_file, index=False)
    print(f"   ✓ Guardado: {cmj_file}")
    print(f"      - Duración: {cmj_data['Time (s)'].max():.1f}s")
    print(f"      - Muestras: {len(cmj_data)}")
    print(f"      - Fz pico: {cmj_data['Fz (N)'].max():.1f} N")
    print()

    # Generar datos de Squat Jump
    print("📊 Generando datos de Squat Jump...")
    sj_data = generate_jump_data(duration=5.0, body_weight=70.0, jump_type='squat_jump')
    sj_file = output_dir / "ejemplo_squat_jump_70kg.xlsx"
    sj_data.to_excel(sj_file, index=False)
    print(f"   ✓ Guardado: {sj_file}")
    print(f"      - Duración: {sj_data['Time (s)'].max():.1f}s")
    print(f"      - Muestras: {len(sj_data)}")
    print(f"      - Fz pico: {sj_data['Fz (N)'].max():.1f} N")
    print()

    # Generar datos con diferente peso corporal
    print("📊 Generando datos con peso de 85kg...")
    squat_heavy = generate_squat_data(duration=10.0, body_weight=85.0)
    squat_heavy_file = output_dir / "ejemplo_sentadilla_85kg.xlsx"
    squat_heavy.to_excel(squat_heavy_file, index=False)
    print(f"   ✓ Guardado: {squat_heavy_file}")
    print()

    print("=" * 70)
    print(" RESUMEN")
    print("=" * 70)
    print()
    print(f"✅ Se generaron 4 archivos de ejemplo en:")
    print(f"   {output_dir}")
    print()
    print("📁 Archivos creados:")
    print("   • ejemplo_sentadilla_70kg.xlsx")
    print("   • ejemplo_cmj_70kg.xlsx")
    print("   • ejemplo_squat_jump_70kg.xlsx")
    print("   • ejemplo_sentadilla_85kg.xlsx")
    print()
    print("🚀 Para probar la importación:")
    print("   1. Ejecutar: python main.py")
    print("   2. Clic en 'Probar Importación de Valkyria'")
    print("   3. Seleccionar uno de los archivos generados")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
