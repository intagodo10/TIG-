"""
Vista de Análisis de Resultados.

Muestra los resultados del análisis biomecánico, incluyendo métricas,
gráficos comparativos y alertas generadas.
"""

import customtkinter as ctk
import numpy as np
from typing import Optional, Callable
from datetime import datetime

from config.ui_theme import COLORS, FONTS
from ui.components.plot_widget import PlotWidget
from ui.components.metric_card import MetricCard
from core.analysis.biomech_analyzer import AnalysisResult
from core.analysis.alert_system import Alert, AlertSeverity


class AlertPanel(ctk.CTkScrollableFrame):
    """
    Panel de alertas con categorización por severidad.
    """

    def __init__(self, master, **kwargs):
        """
        Inicializa el panel de alertas.

        Args:
            master: Widget padre
        """
        super().__init__(master, **kwargs)

        self.configure(fg_color=COLORS["bg_secondary"])

        # Título
        title_label = ctk.CTkLabel(
            self,
            text="⚠️ Alertas Biomecánicas",
            font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        )
        title_label.pack(pady=(0, 15), anchor="w")

        # Frame para contadores de alertas
        self.summary_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"])
        self.summary_frame.pack(fill="x", pady=(0, 15))

        # Contadores
        self.critical_count = self._create_counter(
            self.summary_frame, "Críticas", COLORS["error"], 0
        )
        self.error_count = self._create_counter(
            self.summary_frame, "Errores", COLORS["error_secondary"], 1
        )
        self.warning_count = self._create_counter(
            self.summary_frame, "Advertencias", COLORS["warning"], 2
        )

        # Frame para lista de alertas
        self.alerts_list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.alerts_list_frame.pack(fill="both", expand=True)

        self.alert_widgets = []

    def _create_counter(self, parent, label: str, color: str, column: int):
        """Crea un contador de alertas."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=column, padx=10, pady=5, sticky="ew")
        parent.grid_columnconfigure(column, weight=1)

        count_label = ctk.CTkLabel(
            frame,
            text="0",
            font=("Roboto", 24, "bold"),
            text_color=color
        )
        count_label.pack()

        text_label = ctk.CTkLabel(
            frame,
            text=label,
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        text_label.pack()

        return count_label

    def update_alerts(self, alerts: list[Alert]):
        """
        Actualiza el panel con nuevas alertas.

        Args:
            alerts: Lista de alertas
        """
        # Limpiar widgets anteriores
        for widget in self.alert_widgets:
            widget.destroy()
        self.alert_widgets.clear()

        # Contar por severidad
        critical = sum(1 for a in alerts if a.severity == AlertSeverity.CRITICAL)
        errors = sum(1 for a in alerts if a.severity == AlertSeverity.ERROR)
        warnings = sum(1 for a in alerts if a.severity == AlertSeverity.WARNING)

        # Actualizar contadores
        self.critical_count.configure(text=str(critical))
        self.error_count.configure(text=str(errors))
        self.warning_count.configure(text=str(warnings))

        # Mostrar alertas (ordenadas por severidad)
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.ERROR: 1,
            AlertSeverity.WARNING: 2,
            AlertSeverity.INFO: 3
        }
        sorted_alerts = sorted(alerts, key=lambda a: severity_order[a.severity])

        for alert in sorted_alerts:
            alert_widget = self._create_alert_widget(alert)
            self.alert_widgets.append(alert_widget)

        # Mensaje si no hay alertas
        if not alerts:
            no_alerts = ctk.CTkLabel(
                self.alerts_list_frame,
                text="✅ No hay alertas activas\nTodas las métricas dentro de rangos normales",
                font=FONTS["body"],
                text_color=COLORS["success"],
                justify="center"
            )
            no_alerts.pack(pady=20)
            self.alert_widgets.append(no_alerts)

    def _create_alert_widget(self, alert: Alert) -> ctk.CTkFrame:
        """
        Crea un widget para una alerta individual.

        Args:
            alert: Alerta a mostrar

        Returns:
            Frame con la alerta
        """
        # Color según severidad
        severity_colors = {
            AlertSeverity.CRITICAL: COLORS["error"],
            AlertSeverity.ERROR: COLORS["error_secondary"],
            AlertSeverity.WARNING: COLORS["warning"],
            AlertSeverity.INFO: COLORS["info"]
        }

        border_color = severity_colors.get(alert.severity, COLORS["text_secondary"])

        # Frame principal
        alert_frame = ctk.CTkFrame(
            self.alerts_list_frame,
            fg_color=COLORS["bg_primary"],
            border_color=border_color,
            border_width=2
        )
        alert_frame.pack(fill="x", pady=5, padx=5)

        # Header con título y severidad
        header_frame = ctk.CTkFrame(alert_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        severity_label = ctk.CTkLabel(
            header_frame,
            text=alert.severity.value.upper(),
            font=("Roboto", 10, "bold"),
            text_color=border_color,
            fg_color=COLORS["bg_secondary"],
            corner_radius=4,
            padx=8,
            pady=2
        )
        severity_label.pack(side="left")

        title_label = ctk.CTkLabel(
            header_frame,
            text=alert.title,
            font=("Roboto", 12, "bold"),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(side="left", padx=(10, 0))

        # Mensaje
        message_label = ctk.CTkLabel(
            alert_frame,
            text=alert.message,
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            wraplength=400,
            justify="left"
        )
        message_label.pack(fill="x", padx=10, pady=5, anchor="w")

        # Recomendación (si existe)
        if alert.recommendation:
            rec_frame = ctk.CTkFrame(alert_frame, fg_color=COLORS["bg_secondary"])
            rec_frame.pack(fill="x", padx=10, pady=(5, 10))

            rec_label = ctk.CTkLabel(
                rec_frame,
                text=f"💡 Recomendación: {alert.recommendation}",
                font=FONTS["small"],
                text_color=COLORS["accent_primary"],
                wraplength=380,
                justify="left"
            )
            rec_label.pack(padx=10, pady=8, anchor="w")

        return alert_frame


class MetricsTable(ctk.CTkScrollableFrame):
    """
    Tabla de métricas biomecánicas organizadas por categoría.
    """

    def __init__(self, master, **kwargs):
        """
        Inicializa la tabla de métricas.

        Args:
            master: Widget padre
        """
        super().__init__(master, **kwargs)

        self.configure(fg_color=COLORS["bg_secondary"])

        # Título
        title_label = ctk.CTkLabel(
            self,
            text="📊 Métricas Calculadas",
            font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        )
        title_label.pack(pady=(0, 15), anchor="w")

    def update_metrics(self, result: AnalysisResult):
        """
        Actualiza la tabla con nuevas métricas.

        Args:
            result: Resultado del análisis
        """
        # Limpiar widgets anteriores
        for widget in self.winfo_children()[1:]:  # Mantener título
            widget.destroy()

        # Métricas Cinemáticas
        if result.kinematic_metrics:
            self._add_category("🔄 Cinemática", result.kinematic_metrics)

        # Métricas Dinámicas
        if result.dynamic_metrics:
            self._add_category("⚡ Dinámica", result.dynamic_metrics)

        # Métricas de Fuerza
        if result.force_metrics:
            self._add_category("💪 Fuerza", result.force_metrics)

        # Métricas de Simetría
        if result.symmetry_metrics:
            self._add_symmetry_section(result.symmetry_metrics)

    def _add_category(self, title: str, metrics_dict: dict):
        """
        Añade una categoría de métricas.

        Args:
            title: Título de la categoría
            metrics_dict: Diccionario con métricas
        """
        # Frame de categoría
        category_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"])
        category_frame.pack(fill="x", pady=(0, 10))

        # Título de categoría
        cat_title = ctk.CTkLabel(
            category_frame,
            text=title,
            font=("Roboto", 14, "bold"),
            text_color=COLORS["accent_primary"]
        )
        cat_title.pack(pady=(10, 5), padx=10, anchor="w")

        # Tabla de métricas
        for joint_name, metrics in metrics_dict.items():
            joint_frame = ctk.CTkFrame(category_frame, fg_color=COLORS["bg_secondary"])
            joint_frame.pack(fill="x", padx=10, pady=5)

            # Nombre de articulación
            joint_label = ctk.CTkLabel(
                joint_frame,
                text=joint_name.replace("_", " ").upper(),
                font=("Roboto", 11, "bold"),
                text_color=COLORS["text_primary"]
            )
            joint_label.pack(pady=(8, 5), padx=10, anchor="w")

            # Métricas individuales
            metrics_frame = ctk.CTkFrame(joint_frame, fg_color="transparent")
            metrics_frame.pack(fill="x", padx=10, pady=(0, 8))

            # Convertir dataclass a dict
            if hasattr(metrics, '__dict__'):
                metrics_data = metrics.__dict__
            else:
                metrics_data = metrics

            row = 0
            col = 0
            for metric_name, value in metrics_data.items():
                if metric_name.startswith('_'):
                    continue

                self._add_metric_row(
                    metrics_frame,
                    metric_name,
                    value,
                    row,
                    col
                )

                col += 1
                if col >= 2:  # 2 columnas
                    col = 0
                    row += 1

    def _add_metric_row(self, parent, name: str, value: float, row: int, col: int):
        """Añade una fila de métrica."""
        # Formatear nombre
        display_name = name.replace("_", " ").title()

        # Unidades
        units = {
            "rom": "°",
            "peak_flexion": "°",
            "peak_extension": "°",
            "mean_angle": "°",
            "angular_velocity_peak": "deg/s",
            "angular_acceleration_peak": "deg/s²",
            "peak_moment": "Nm/kg",
            "mean_moment": "Nm/kg",
            "peak_power": "W/kg",
            "work": "J/kg",
            "moment_impulse": "Nm·s/kg",
            "peak_grf": "BW",
            "mean_grf": "BW",
            "loading_rate": "BW/s",
            "impulse": "N·s",
            "contact_time": "s",
            "time_to_peak": "s"
        }

        unit = units.get(name, "")

        # Frame de métrica
        metric_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_primary"])
        metric_frame.grid(row=row, column=col, padx=5, pady=3, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)

        # Nombre
        name_label = ctk.CTkLabel(
            metric_frame,
            text=display_name,
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        name_label.pack(side="left", padx=(8, 5))

        # Valor
        if isinstance(value, (int, float)):
            formatted_value = f"{value:.2f} {unit}".strip()
        else:
            formatted_value = str(value)

        value_label = ctk.CTkLabel(
            metric_frame,
            text=formatted_value,
            font=("Roboto", 11, "bold"),
            text_color=COLORS["accent_primary"],
            anchor="e"
        )
        value_label.pack(side="right", padx=(5, 8))

    def _add_symmetry_section(self, symmetry_metrics):
        """Añade sección de simetría."""
        # Frame de categoría
        category_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"])
        category_frame.pack(fill="x", pady=(0, 10))

        # Título
        cat_title = ctk.CTkLabel(
            category_frame,
            text="⚖️ Simetría Bilateral",
            font=("Roboto", 14, "bold"),
            text_color=COLORS["accent_primary"]
        )
        cat_title.pack(pady=(10, 5), padx=10, anchor="w")

        # Indicador visual de simetría
        si = symmetry_metrics.symmetry_index

        if si < 10:
            status = "Simétrico"
            color = COLORS["success"]
        elif si < 20:
            status = "Asimetría Moderada"
            color = COLORS["warning"]
        else:
            status = "Asimetría Severa"
            color = COLORS["error"]

        status_frame = ctk.CTkFrame(category_frame, fg_color=color, corner_radius=8)
        status_frame.pack(fill="x", padx=10, pady=5)

        status_label = ctk.CTkLabel(
            status_frame,
            text=f"{status} - {si:.1f}%",
            font=("Roboto", 12, "bold"),
            text_color=COLORS["bg_primary"]
        )
        status_label.pack(pady=8)

        # Métricas de simetría
        metrics_frame = ctk.CTkFrame(category_frame, fg_color=COLORS["bg_secondary"])
        metrics_frame.pack(fill="x", padx=10, pady=(0, 10))

        metrics_data = {
            "Índice de Simetría": f"{symmetry_metrics.symmetry_index:.1f}%",
            "Ratio de Asimetría": f"{symmetry_metrics.asymmetry_ratio:.2f}",
            "Diferencia Absoluta": f"{symmetry_metrics.difference:.2f}",
            "Déficit Bilateral": f"{symmetry_metrics.bilateral_deficit:.1f}%"
        }

        for i, (name, value) in enumerate(metrics_data.items()):
            row_frame = ctk.CTkFrame(metrics_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=10, pady=3)

            name_label = ctk.CTkLabel(
                row_frame,
                text=name,
                font=FONTS["small"],
                text_color=COLORS["text_secondary"],
                anchor="w"
            )
            name_label.pack(side="left")

            value_label = ctk.CTkLabel(
                row_frame,
                text=value,
                font=("Roboto", 11, "bold"),
                text_color=COLORS["accent_primary"],
                anchor="e"
            )
            value_label.pack(side="right")


class AnalysisView(ctk.CTkFrame):
    """
    Vista principal de análisis de resultados.

    Muestra métricas, gráficos y alertas del análisis biomecánico.
    """

    def __init__(self, master, on_export_report: Optional[Callable] = None, **kwargs):
        """
        Inicializa la vista de análisis.

        Args:
            master: Widget padre
            on_export_report: Callback para exportar reporte
        """
        super().__init__(master, **kwargs)

        self.on_export_report = on_export_report
        self.current_result: Optional[AnalysisResult] = None

        self.configure(fg_color=COLORS["bg_primary"])

        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets de la interfaz."""
        # Panel superior con título y botones
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text="📈 Análisis de Resultados",
            font=FONTS["title"],
            text_color=COLORS["text_primary"]
        )
        title_label.pack(side="left")

        # Botones de acción
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(side="right")

        self.export_button = ctk.CTkButton(
            button_frame,
            text="📄 Exportar Reporte",
            command=self._on_export_clicked,
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            font=FONTS["button"],
            height=35,
            state="disabled"
        )
        self.export_button.pack(side="right", padx=5)

        # Contenedor principal con 3 columnas
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Configurar grid
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=2)  # Gráficos
        main_container.grid_columnconfigure(1, weight=1)  # Métricas
        main_container.grid_columnconfigure(2, weight=1)  # Alertas

        # Columna 1: Gráficos
        graphs_frame = ctk.CTkFrame(main_container, fg_color=COLORS["bg_secondary"])
        graphs_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        graphs_label = ctk.CTkLabel(
            graphs_frame,
            text="📊 Visualización",
            font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        )
        graphs_label.pack(pady=(15, 10), padx=15, anchor="w")

        # 4 gráficos
        self.angle_plot = PlotWidget(graphs_frame, title="Ángulo de Rodilla")
        self.angle_plot.pack(fill="both", expand=True, padx=10, pady=5)

        self.grf_plot = PlotWidget(graphs_frame, title="Fuerza de Reacción al Suelo")
        self.grf_plot.pack(fill="both", expand=True, padx=10, pady=5)

        # Columna 2: Métricas
        self.metrics_table = MetricsTable(
            main_container,
            width=350
        )
        self.metrics_table.grid(row=0, column=1, sticky="nsew", padx=5)

        # Columna 3: Alertas
        self.alert_panel = AlertPanel(
            main_container,
            width=350
        )
        self.alert_panel.grid(row=0, column=2, sticky="nsew", padx=(10, 0))

        # Estado inicial: Mensaje de "Sin datos"
        self._show_no_data_message()

    def _show_no_data_message(self):
        """Muestra mensaje cuando no hay datos."""
        # Crear overlay
        self.no_data_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_secondary"],
            corner_radius=15
        )
        self.no_data_frame.place(relx=0.5, rely=0.5, anchor="center")

        message_label = ctk.CTkLabel(
            self.no_data_frame,
            text="📭 No hay resultados de análisis\n\n"
                 "Realiza una captura de datos y el análisis\n"
                 "se mostrará automáticamente aquí.",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            justify="center"
        )
        message_label.pack(padx=40, pady=40)

    def update_results(self, result: AnalysisResult):
        """
        Actualiza la vista con nuevos resultados.

        Args:
            result: Resultado del análisis
        """
        self.current_result = result

        # Ocultar mensaje de sin datos
        if hasattr(self, 'no_data_frame'):
            self.no_data_frame.destroy()

        # Habilitar botón de exportar
        self.export_button.configure(state="normal")

        # Actualizar métricas
        self.metrics_table.update_metrics(result)

        # Actualizar alertas
        self.alert_panel.update_alerts(result.alerts)

        # Actualizar gráficos
        self._update_graphs(result)

    def _update_graphs(self, result: AnalysisResult):
        """
        Actualiza los gráficos con datos del resultado.

        Args:
            result: Resultado del análisis
        """
        # Gráfico de ángulo de rodilla
        if result.processed_data and result.sync_result:
            time = result.sync_result.time_common

            # Intentar obtener datos de ángulo (aproximado desde gyro)
            if 'femur_right_gyro' in result.processed_data:
                # Este es un placeholder - en producción vendría de OpenSim IK
                # Por ahora mostramos velocidad angular sagital
                gyro_data = result.processed_data['femur_right_gyro']

                self.angle_plot.clear()
                ax = self.angle_plot.get_axes()

                if gyro_data.ndim > 1:
                    ax.plot(time, gyro_data[:, 1], color=COLORS["accent_primary"], linewidth=2)
                    ax.set_ylabel("Velocidad Angular (rad/s)", color=COLORS["text_primary"])
                else:
                    ax.plot(time, gyro_data, color=COLORS["accent_primary"], linewidth=2)
                    ax.set_ylabel("Ángulo (grados)", color=COLORS["text_primary"])

                ax.set_xlabel("Tiempo (s)", color=COLORS["text_primary"])
                ax.grid(True, alpha=0.3)
                self.angle_plot.draw()

            # Gráfico de GRF
            if 'fz' in result.processed_data:
                fz = result.processed_data['fz']

                self.grf_plot.clear()
                ax = self.grf_plot.get_axes()

                ax.plot(time, fz, color=COLORS["success"], linewidth=2, label="Fz")
                ax.set_xlabel("Tiempo (s)", color=COLORS["text_primary"])
                ax.set_ylabel("Fuerza (N)", color=COLORS["text_primary"])
                ax.axhline(y=0, color=COLORS["text_secondary"], linestyle='--', alpha=0.5)
                ax.grid(True, alpha=0.3)
                ax.legend()
                self.grf_plot.draw()

    def _on_export_clicked(self):
        """Maneja el clic en exportar reporte."""
        if self.on_export_report and self.current_result:
            self.on_export_report(self.current_result)
