"""
Ventana principal del sistema.

Integra todas las vistas y componentes del sistema de análisis biomecánico.
"""

import customtkinter as ctk
from typing import Optional

from config.ui_theme import COLORS, FONTS
from config.settings import UI_CONFIG
from ui.components import AlertManager, MetricCard
from ui.views.patient_view import PatientView
from ui.views.capture_view import CaptureView
from ui.views.analysis_view import AnalysisView
from models.patient import Patient
from core.analysis.biomech_analyzer import AnalysisResult
from utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow(ctk.CTk):
    """
    Ventana principal de la aplicación.

    Contiene la navegación y todas las vistas del sistema.
    """

    def __init__(self):
        """Inicializa la ventana principal."""
        super().__init__()

        # Configurar ventana
        self.title(UI_CONFIG["window_title"])
        self.geometry(f"{UI_CONFIG['window_size'][0]}x{UI_CONFIG['window_size'][1]}")
        self.minsize(UI_CONFIG["min_window_size"][0], UI_CONFIG["min_window_size"][1])

        if UI_CONFIG["resizable"]:
            self.resizable(True, True)

        # Variables de estado
        self.current_patient: Optional[Patient] = None

        # Sistema de alertas
        self.alert_manager = AlertManager(self)

        # Crear interfaz
        self._create_widgets()

        logger.info("Ventana principal inicializada")

    def _create_widgets(self):
        """Crea los widgets de la ventana."""
        # Layout principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ===== HEADER =====
        self._create_header()

        # ===== CONTENIDO PRINCIPAL (TabView) =====
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=COLORS["bg_primary"],
            segmented_button_fg_color=COLORS["bg_tertiary"],
            segmented_button_selected_color=COLORS["accent_primary"],
            segmented_button_selected_hover_color="#00bd98",
            segmented_button_unselected_color=COLORS["bg_tertiary"],
            segmented_button_unselected_hover_color=COLORS["bg_hover"]
        )
        self.tabview.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")

        # Crear tabs
        self.tab_dashboard = self.tabview.add("📊 Dashboard")
        self.tab_patient = self.tabview.add("👤 Paciente")
        self.tab_capture = self.tabview.add("🎯 Captura")
        self.tab_analysis = self.tabview.add("📈 Análisis")
        self.tab_reports = self.tabview.add("📄 Reportes")

        # Inicializar vistas
        self._setup_views()

        # ===== FOOTER / STATUS BAR =====
        self._create_footer()

        # Seleccionar tab inicial
        self.tabview.set("👤 Paciente")

    def _create_header(self):
        """Crea el header de la aplicación."""
        header = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_secondary"],
            height=60,
            corner_radius=0
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        # Frame interno para contenido
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=20, pady=10)

        # Logo y título
        title_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        title_frame.pack(side="left", fill="y")

        title_label = ctk.CTkLabel(
            title_frame,
            text="🦴 Sistema de Análisis Biomecánico",
            font=ctk.CTkFont(size=FONTS["size_large"], weight=FONTS["weight_bold"]),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(side="left")

        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Universidad Antonio Nariño",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_tertiary"]
        )
        subtitle_label.pack(side="left", padx=(15, 0))

        # Información del paciente actual
        self.patient_info_label = ctk.CTkLabel(
            header_content,
            text="Sin paciente seleccionado",
            font=ctk.CTkFont(size=FONTS["size_normal"]),
            text_color=COLORS["text_secondary"]
        )
        self.patient_info_label.pack(side="right")

    def _create_footer(self):
        """Crea el footer / barra de estado."""
        footer = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_secondary"],
            height=35,
            corner_radius=0
        )
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_propagate(False)

        # Frame interno
        footer_content = ctk.CTkFrame(footer, fg_color="transparent")
        footer_content.pack(fill="both", expand=True, padx=20, pady=5)

        # Estado
        self.status_label = ctk.CTkLabel(
            footer_content,
            text="Estado: Listo",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_secondary"]
        )
        self.status_label.pack(side="left")

        # Separador
        separator = ctk.CTkLabel(
            footer_content,
            text="|",
            text_color=COLORS["text_tertiary"]
        )
        separator.pack(side="left", padx=10)

        # Versión
        version_label = ctk.CTkLabel(
            footer_content,
            text="v1.0.0",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_tertiary"]
        )
        version_label.pack(side="right")

    def _setup_views(self):
        """Configura todas las vistas."""
        # Dashboard (placeholder)
        self._setup_dashboard()

        # Vista de Paciente
        self.patient_view = PatientView(
            self.tab_patient,
            on_patient_saved=self._on_patient_saved
        )
        self.patient_view.pack(fill="both", expand=True)

        # Vista de Captura
        self.capture_view = CaptureView(
            self.tab_capture,
            on_analysis_complete=self._on_analysis_complete
        )
        self.capture_view.pack(fill="both", expand=True)

        # Vista de Análisis
        self.analysis_view = AnalysisView(
            self.tab_analysis,
            on_export_report=self._on_export_report
        )
        self.analysis_view.pack(fill="both", expand=True)

        # Reportes (placeholder)
        self._setup_reports_placeholder()

    def _setup_dashboard(self):
        """Configura el dashboard (placeholder mejorado)."""
        dashboard_frame = ctk.CTkFrame(self.tab_dashboard, fg_color=COLORS["bg_primary"])
        dashboard_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title = ctk.CTkLabel(
            dashboard_frame,
            text="Dashboard - Vista General",
            font=ctk.CTkFont(size=FONTS["size_xxlarge"], weight=FONTS["weight_bold"]),
            text_color=COLORS["text_primary"]
        )
        title.pack(pady=(0, 20), anchor="w")

        # Grid de métricas
        metrics_frame = ctk.CTkFrame(dashboard_frame, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, 20))

        metrics_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Tarjetas de métricas de ejemplo
        metric1 = MetricCard(metrics_frame, title="Pacientes Totales", value="0", status="normal")
        metric1.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        metric2 = MetricCard(metrics_frame, title="Sesiones Hoy", value="0", status="normal")
        metric2.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        metric3 = MetricCard(metrics_frame, title="Alertas Activas", value="0", status="normal")
        metric3.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        # Información
        info_frame = ctk.CTkFrame(dashboard_frame, fg_color=COLORS["bg_secondary"], corner_radius=12)
        info_frame.pack(fill="both", expand=True)

        info_text = ctk.CTkLabel(
            info_frame,
            text="""
            Bienvenido al Sistema de Análisis Biomecánico de Rodilla

            ✓ Componentes de UI implementados
            ✓ Vista de Paciente funcional
            ✓ Vista de Captura funcional
            ✓ Importación de datos Valkyria
            ✓ Gráficos en tiempo real

            Comenzar:
            1. Ir a la pestaña 'Paciente' e ingresar información
            2. Ir a 'Captura' e importar datos de Valkyria
            3. Configurar ejercicio y capturar datos

            Estado del Sistema: ✓ Operativo
            """,
            font=ctk.CTkFont(size=FONTS["size_normal"]),
            text_color=COLORS["text_primary"],
            justify="left"
        )
        info_text.pack(padx=30, pady=30)

    def _on_analysis_complete(self, result: AnalysisResult):
        """
        Callback cuando se completa un análisis.

        Args:
            result: Resultado del análisis
        """
        logger.info("Análisis completado, actualizando vista de análisis")

        # Actualizar vista de análisis
        self.analysis_view.update_results(result)

        # Cambiar a la pestaña de análisis
        self.tabview.set("📈 Análisis")

        # Mostrar alerta de éxito
        self.alert_manager.success(
            "Análisis completado exitosamente",
            duration=3000
        )

        # Actualizar estado
        self.update_status("Análisis completado")

    def _on_export_report(self, result: AnalysisResult):
        """
        Callback para exportar reporte.

        Args:
            result: Resultado del análisis
        """
        logger.info("Exportando reporte...")

        # TODO: Implementar exportación de reporte
        self.alert_manager.info(
            "Exportación de reportes en desarrollo",
            duration=3000
        )

        self.update_status("Reporte exportado")

    def _setup_reports_placeholder(self):
        """Configura placeholder de reportes."""
        reports_frame = ctk.CTkFrame(self.tab_reports, fg_color=COLORS["bg_primary"])
        reports_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(
            reports_frame,
            text="Generación de Reportes",
            font=ctk.CTkFont(size=FONTS["size_xxlarge"], weight=FONTS["weight_bold"]),
            text_color=COLORS["text_primary"]
        )
        title.pack(pady=(0, 20), anchor="w")

        info = ctk.CTkLabel(
            reports_frame,
            text="Vista de reportes en desarrollo\n\nAquí se podrán:\n• Exportar a PDF\n• Exportar a Excel\n• Exportar a CSV\n• Comparar sesiones",
            font=ctk.CTkFont(size=FONTS["size_normal"]),
            text_color=COLORS["text_secondary"],
            justify="center"
        )
        info.pack(expand=True)

    def _on_patient_saved(self, patient: Patient):
        """
        Callback cuando se guarda un paciente.

        Args:
            patient: Paciente guardado
        """
        self.current_patient = patient

        # Actualizar info en header
        self.patient_info_label.configure(
            text=f"Paciente: {patient.name} (ID: {patient.patient_id})"
        )

        # Mostrar alerta de éxito
        self.alert_manager.success(
            f"Paciente guardado: {patient.name}",
            duration=3000
        )

        # Actualizar estado
        self.status_label.configure(text=f"Estado: Paciente activo ({patient.patient_id})")

        logger.info(f"Paciente establecido como actual: {patient.patient_id}")

    def update_status(self, message: str):
        """
        Actualiza el mensaje de estado.

        Args:
            message: Mensaje a mostrar
        """
        self.status_label.configure(text=f"Estado: {message}")
        logger.debug(f"Estado actualizado: {message}")

    def show_alert(self, message: str, alert_type: str = "info"):
        """
        Muestra una alerta.

        Args:
            message: Mensaje
            alert_type: Tipo (info, success, warning, error)
        """
        self.alert_manager.show_alert(message, alert_type)
