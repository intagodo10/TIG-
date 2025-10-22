"""
Sistema Integrado de Análisis Biomecánico de Rodilla
Universidad Antonio Nariño - Ingeniería Biomédica

Punto de entrada principal de la aplicación.
"""

import sys
# 👇 Muy importante en Windows: fuerza MTA para que Bleak reciba callbacks WinRT
# Debe ir ANTES de cualquier import que pueda tocar COM/pywin32/customtkinter, etc.
sys.coinit_flags = 0
import os
from pathlib import Path

# Añadir el directorio raíz al path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

import customtkinter as ctk
from utils.logger import get_logger, log_info
from config.settings import UI_CONFIG
from ui.main_window import MainWindow

logger = get_logger(__name__)


def setup_customtkinter():
    """Configura CustomTkinter con el tema personalizado."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


# Mantener la clase vieja para compatibilidad (sin usar)
class BiomechApp(ctk.CTk):
    """
    Aplicación principal del Sistema de Análisis Biomecánico.
    """

    def __init__(self):
        """Inicializa la aplicación principal."""
        super().__init__()

        # Configurar ventana principal
        self.title(UI_CONFIG["window_title"])
        self.geometry(f"{UI_CONFIG['window_size'][0]}x{UI_CONFIG['window_size'][1]}")
        self.minsize(UI_CONFIG["min_window_size"][0], UI_CONFIG["min_window_size"][1])

        if UI_CONFIG["resizable"]:
            self.resizable(True, True)

        log_info("Aplicación iniciada")

        # Crear interfaz temporal (placeholder)
        self.create_placeholder_ui()

    def create_placeholder_ui(self):
        """
        Crea una interfaz de placeholder mientras se completa el desarrollo.
        """
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Logo y título
        title_label = ctk.CTkLabel(
            main_frame,
            text="🦴 Sistema de Análisis Biomecánico de Rodilla",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 10))

        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Universidad Antonio Nariño - Ingeniería Biomédica",
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.pack(pady=(0, 30))

        # Información del sistema
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="both", expand=True, padx=20, pady=20)

        info_text = """
        ✅ Sistema Base Configurado

        Componentes Implementados:
        • Configuración general del sistema
        • Sistema de logging
        • Modelos de datos (Patient, Session)
        • Manejador de Plataforma de Fuerza Valkyria
        • Tema de interfaz oscuro moderno

        En Desarrollo:
        • Manejador de sensores IMU Xsens DOT
        • Sincronizador de señales
        • Interfaz con OpenSim (IK/ID)
        • Calculadora de métricas
        • Sistema de alertas
        • Interfaz gráfica completa
        • Generador de reportes

        Próximos Pasos:
        1. Completar módulos de adquisición de datos
        2. Implementar procesamiento de señales
        3. Integrar OpenSim
        4. Desarrollar interfaz gráfica completa
        5. Implementar sistema de reportes

        Estado: 🚧 EN CONSTRUCCIÓN 🚧
        """

        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        info_label.pack(padx=20, pady=20)

        # Botones de acción
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=20)

        test_button = ctk.CTkButton(
            button_frame,
            text="🧪 Probar Importación de Valkyria",
            command=self.test_force_platform,
            width=250,
            height=40
        )
        test_button.pack(side="left", padx=10)

        exit_button = ctk.CTkButton(
            button_frame,
            text="❌ Salir",
            command=self.quit_app,
            width=150,
            height=40,
            fg_color="#ff6b6b",
            hover_color="#ff5252"
        )
        exit_button.pack(side="left", padx=10)

        # Status bar
        self.status_label = ctk.CTkLabel(
            self,
            text="Estado: Listo | Sistema v1.0.0",
            font=ctk.CTkFont(size=10),
            anchor="w"
        )
        self.status_label.pack(side="bottom", fill="x", padx=10, pady=5)

    def test_force_platform(self):
        """
        Prueba de importación de datos de plataforma de fuerza.
        """
        from tkinter import filedialog
        from core.data_acquisition.force_platform import ForcePlatformHandler

        # Diálogo para seleccionar archivo
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Excel de Valkyria",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )

        if not file_path:
            return

        # Crear manejador y probar importación
        handler = ForcePlatformHandler()

        self.status_label.configure(text="Estado: Importando datos...")
        self.update()

        if handler.import_from_excel(file_path):
            # Calibrar
            if handler.calibrate_zero():
                stats = handler.get_summary_stats()

                # Mostrar resultados
                result_window = ctk.CTkToplevel(self)
                result_window.title("Resultados de Importación")
                result_window.geometry("500x400")

                result_text = f"""
                ✅ Importación Exitosa

                Archivo: {Path(file_path).name}

                Estadísticas:
                • Duración: {stats['duration']:.2f} segundos
                • Muestras: {stats['num_samples']}
                • Frecuencia: {stats['sampling_rate']:.1f} Hz
                • Pico Fz: {stats['peak_fz']:.2f} N
                • Promedio Fz: {stats['mean_fz']:.2f} N
                • Pico Fx: {stats['peak_fx']:.2f} N
                • Pico Fy: {stats['peak_fy']:.2f} N
                • Calibrado: {'Sí' if stats['is_calibrated'] else 'No'}

                El sistema puede importar y procesar datos
                de la plataforma Valkyria correctamente.
                """

                label = ctk.CTkLabel(
                    result_window,
                    text=result_text,
                    font=ctk.CTkFont(size=12),
                    justify="left"
                )
                label.pack(padx=20, pady=20)

                close_btn = ctk.CTkButton(
                    result_window,
                    text="Cerrar",
                    command=result_window.destroy
                )
                close_btn.pack(pady=10)

                self.status_label.configure(text="Estado: Importación completada ✓")
            else:
                self.status_label.configure(text="Estado: Error en calibración ✗")
        else:
            self.status_label.configure(text="Estado: Error en importación ✗")

    def quit_app(self):
        """Cierra la aplicación."""
        log_info("Aplicación cerrada por usuario")
        self.quit()
        self.destroy()


def main():
    """Función principal de entrada."""
    try:
        # Configurar CustomTkinter
        setup_customtkinter()

        log_info("=" * 60)
        log_info("Sistema de Análisis Biomecánico de Rodilla")
        log_info("Universidad Antonio Nariño - Ingeniería Biomédica")
        log_info("=" * 60)

        # Crear y ejecutar aplicación con interfaz completa
        app = MainWindow()
        app.mainloop()

    except Exception as e:
        logger.error(f"Error fatal en la aplicación: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
