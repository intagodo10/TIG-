"""
Componente de gráficos embebidos.

Integra matplotlib con CustomTkinter para visualizaciones.
"""

import customtkinter as ctk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

from config.ui_theme import COLORS, PLOT_STYLE, PLOT_COLORS


class PlotWidget(ctk.CTkFrame):
    """
    Widget de gráfico embebido con matplotlib.

    Proporciona gráficos interactivos con tema oscuro.
    """

    def __init__(self, master, title: str = "", **kwargs):
        """
        Inicializa el widget de gráfico.

        Args:
            master: Widget padre
            title: Título del gráfico
        """
        super().__init__(master, **kwargs)

        self.title = title

        self.configure(
            fg_color=COLORS["bg_secondary"],
            corner_radius=12
        )

        # Aplicar estilo matplotlib
        plt.style.use('dark_background')
        for key, value in PLOT_STYLE.items():
            matplotlib.rcParams[key] = value

        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets internos."""
        # Título del gráfico
        if self.title:
            title_label = ctk.CTkLabel(
                self,
                text=self.title,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["text_primary"]
            )
            title_label.pack(padx=15, pady=(15, 5), anchor="w")

        # Crear figura matplotlib
        self.figure = Figure(figsize=(6, 4), dpi=100, facecolor=COLORS["plot_bg"])
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(COLORS["plot_bg"])

        # Canvas para el gráfico
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.configure(bg=COLORS["bg_secondary"], highlightthickness=0)
        canvas_widget.pack(fill="both", expand=True, padx=10, pady=10)

        # Toolbar de navegación (opcional)
        # self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        # self.toolbar.update()

    def plot_line(self, x, y, label=None, color=None, linewidth=2, **kwargs):
        """
        Dibuja una línea en el gráfico.

        Args:
            x: Datos eje X
            y: Datos eje Y
            label: Etiqueta para leyenda
            color: Color de la línea
            linewidth: Grosor de línea
        """
        if color is None:
            # Usar colores del tema
            line_count = len(self.ax.lines)
            color = PLOT_COLORS[line_count % len(PLOT_COLORS)]

        self.ax.plot(x, y, label=label, color=color, linewidth=linewidth, **kwargs)

    def plot_scatter(self, x, y, label=None, color=None, **kwargs):
        """
        Dibuja puntos en el gráfico.

        Args:
            x: Datos eje X
            y: Datos eje Y
            label: Etiqueta para leyenda
            color: Color de los puntos
        """
        if color is None:
            line_count = len(self.ax.collections)
            color = PLOT_COLORS[line_count % len(PLOT_COLORS)]

        self.ax.scatter(x, y, label=label, color=color, **kwargs)

    def set_labels(self, xlabel=None, ylabel=None, title=None):
        """
        Establece etiquetas de ejes y título.

        Args:
            xlabel: Etiqueta eje X
            ylabel: Etiqueta eje Y
            title: Título del gráfico
        """
        if xlabel:
            self.ax.set_xlabel(xlabel, color=COLORS["text_primary"])
        if ylabel:
            self.ax.set_ylabel(ylabel, color=COLORS["text_primary"])
        if title:
            self.ax.set_title(title, color=COLORS["text_primary"], pad=10)

    def add_legend(self, loc='best', **kwargs):
        """
        Añade leyenda al gráfico.

        Args:
            loc: Ubicación de la leyenda
        """
        legend = self.ax.legend(loc=loc, **kwargs)
        legend.get_frame().set_facecolor(COLORS["bg_tertiary"])
        legend.get_frame().set_edgecolor(COLORS["border_primary"])
        for text in legend.get_texts():
            text.set_color(COLORS["text_primary"])

    def add_grid(self, visible=True, **kwargs):
        """
        Añade/quita cuadrícula.

        Args:
            visible: Mostrar cuadrícula
        """
        self.ax.grid(visible, color=COLORS["plot_grid"], alpha=0.3, linestyle='--', **kwargs)

    def clear(self):
        """Limpia el gráfico."""
        self.ax.clear()
        self.ax.set_facecolor(COLORS["plot_bg"])

    def refresh(self):
        """Actualiza la visualización."""
        self.figure.tight_layout()
        self.canvas.draw()

    def save_plot(self, filename):
        """
        Guarda el gráfico en un archivo.

        Args:
            filename: Ruta del archivo de salida
        """
        self.figure.savefig(filename, dpi=300, facecolor=COLORS["plot_bg"],
                          edgecolor='none', bbox_inches='tight')


class MultiPlotWidget(ctk.CTkFrame):
    """
    Widget con múltiples subgráficos.

    Permite crear layouts con varios gráficos organizados.
    """

    def __init__(self, master, rows=2, cols=1, title: str = "", **kwargs):
        """
        Inicializa el widget de múltiples gráficos.

        Args:
            master: Widget padre
            rows: Número de filas
            cols: Número de columnas
            title: Título general
        """
        super().__init__(master, **kwargs)

        self.rows = rows
        self.cols = cols
        self.title = title

        self.configure(
            fg_color=COLORS["bg_secondary"],
            corner_radius=12
        )

        # Aplicar estilo matplotlib
        plt.style.use('dark_background')
        for key, value in PLOT_STYLE.items():
            matplotlib.rcParams[key] = value

        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets internos."""
        # Título general
        if self.title:
            title_label = ctk.CTkLabel(
                self,
                text=self.title,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["text_primary"]
            )
            title_label.pack(padx=15, pady=(15, 5), anchor="w")

        # Crear figura con subplots
        self.figure = Figure(figsize=(8, 6), dpi=100, facecolor=COLORS["plot_bg"])
        self.axes = self.figure.subplots(self.rows, self.cols)

        # Asegurar que axes siempre sea array
        if self.rows == 1 and self.cols == 1:
            self.axes = np.array([[self.axes]])
        elif self.rows == 1 or self.cols == 1:
            self.axes = self.axes.reshape(self.rows, self.cols)

        # Configurar fondo de cada subplot
        for ax in self.axes.flat:
            ax.set_facecolor(COLORS["plot_bg"])

        # Canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.configure(bg=COLORS["bg_secondary"], highlightthickness=0)
        canvas_widget.pack(fill="both", expand=True, padx=10, pady=10)

    def get_subplot(self, row, col):
        """
        Obtiene un subplot específico.

        Args:
            row: Fila (0-indexed)
            col: Columna (0-indexed)

        Returns:
            Axes del subplot
        """
        return self.axes[row, col]

    def clear_all(self):
        """Limpia todos los subplots."""
        for ax in self.axes.flat:
            ax.clear()
            ax.set_facecolor(COLORS["plot_bg"])

    def refresh(self):
        """Actualiza la visualización."""
        self.figure.tight_layout()
        self.canvas.draw()
