"""
Configuración del tema visual de la interfaz gráfica.

Define la paleta de colores, tipografía, estilos de componentes y
configuraciones visuales para el tema oscuro moderno del sistema.
"""

from typing import Dict, Tuple

# ==================== PALETA DE COLORES ====================

COLORS = {
    # Fondos
    "bg_primary": "#1e1e1e",
    "bg_secondary": "#2d2d2d",
    "bg_tertiary": "#3d3d3d",
    "bg_hover": "#404040",
    "bg_active": "#4a4a4a",
    "bg_input": "#2a2a2a",

    # Acentos
    "accent_primary": "#00d4aa",  # Verde azulado
    "accent_hover": "#00bd98",    # Verde azulado oscuro (hover)
    "accent_secondary": "#4a9eff",  # Azul
    "accent_tertiary": "#9d4edd",  # Púrpura

    # Estados
    "success": "#6bcf7f",
    "warning": "#ffd93d",
    "error": "#ff6b6b",
    "error_secondary": "#ff9a8a",  # Error más suave
    "info": "#4a9eff",

    # Texto
    "text_primary": "#e0e0e0",
    "text_secondary": "#b0b0b0",
    "text_tertiary": "#808080",
    "text_disabled": "#505050",
    "text_on_accent": "#ffffff",

    # Bordes
    "border_primary": "#404040",
    "border_secondary": "#505050",
    "border_focus": "#00d4aa",

    # Gráficos y visualización
    "plot_bg": "#2d2d2d",
    "plot_grid": "#404040",
    "plot_line_1": "#00d4aa",
    "plot_line_2": "#4a9eff",
    "plot_line_3": "#ffd93d",
    "plot_line_4": "#ff6b6b",
    "plot_line_5": "#9d4edd",
    "plot_line_6": "#6bcf7f",
    "plot_line_7": "#ff9a56",

    # Sensores (estado)
    "sensor_connected": "#6bcf7f",
    "sensor_connecting": "#ffd93d",
    "sensor_disconnected": "#ff6b6b",
    "sensor_error": "#ff6b6b",

    # Especiales
    "recording": "#ff4444",
    "recording_pulse": "#ff6b6b",
    "transparent": "transparent"
}

# ==================== TIPOGRAFÍA ====================

FONTS = {
    "family_primary": ("Segoe UI", "Roboto", "Arial"),
    "family_secondary": ("Segoe UI", "Helvetica", "Arial"),
    "family_mono": ("Consolas", "Courier New", "monospace"),

    # Tamaños
    "size_xxlarge": 24,
    "size_xlarge": 20,
    "size_large": 16,
    "size_medium": 14,
    "size_normal": 12,
    "size_small": 10,
    "size_xsmall": 8,

    # Pesos
    "weight_light": "normal",
    "weight_normal": "normal",
    "weight_bold": "bold",

    # Aliases para compatibilidad
    "title": ("Roboto", 24, "bold"),
    "heading": ("Roboto", 18, "bold"),
    "subheading": ("Roboto", 14, "bold"),
    "body": ("Roboto", 12, "normal"),
    "small": ("Roboto", 10, "normal"),
    "button": ("Roboto", 12, "bold"),
}

# ==================== ESPACIADO ====================

SPACING = {
    "xxsmall": 2,
    "xsmall": 4,
    "small": 8,
    "medium": 12,
    "large": 16,
    "xlarge": 24,
    "xxlarge": 32,
    "xxxlarge": 48
}

# ==================== BORDES Y ESQUINAS ====================

BORDERS = {
    "radius_small": 4,
    "radius_medium": 8,
    "radius_large": 12,
    "radius_xlarge": 16,
    "radius_round": 9999,

    "width_thin": 1,
    "width_normal": 2,
    "width_thick": 3
}

# ==================== SOMBRAS ====================

SHADOWS = {
    "small": "0 1px 3px rgba(0, 0, 0, 0.3)",
    "medium": "0 4px 6px rgba(0, 0, 0, 0.4)",
    "large": "0 10px 15px rgba(0, 0, 0, 0.5)",
    "xlarge": "0 20px 25px rgba(0, 0, 0, 0.6)"
}

# ==================== ANIMACIONES ====================

ANIMATIONS = {
    "duration_fast": 150,  # ms
    "duration_normal": 300,  # ms
    "duration_slow": 500,  # ms

    "easing_standard": "ease-in-out",
    "easing_enter": "ease-out",
    "easing_exit": "ease-in"
}

# ==================== ICONOS ====================

ICONS = {
    "size_small": 16,
    "size_medium": 20,
    "size_large": 24,
    "size_xlarge": 32,

    # Unicode icons (fallback)
    "dashboard": "📊",
    "patient": "👤",
    "sensors": "📡",
    "capture": "🎯",
    "analysis": "📈",
    "reports": "📄",
    "settings": "⚙",
    "help": "❓",
    "connect": "🔌",
    "disconnect": "⚡",
    "play": "▶",
    "pause": "⏸",
    "stop": "■",
    "record": "⏺",
    "save": "💾",
    "export": "📤",
    "import": "📥",
    "delete": "🗑",
    "edit": "✏",
    "check": "✓",
    "cross": "✗",
    "warning": "⚠",
    "error": "⛔",
    "info": "ℹ",
    "success": "✓",
    "arrow_right": "→",
    "arrow_left": "←",
    "arrow_up": "↑",
    "arrow_down": "↓"
}

# ==================== COMPONENTES ESPECÍFICOS ====================

COMPONENTS = {
    # Botones
    "button_primary": {
        "fg_color": COLORS["accent_primary"],
        "hover_color": "#00bd98",
        "text_color": COLORS["text_on_accent"],
        "border_color": COLORS["accent_primary"],
        "corner_radius": BORDERS["radius_medium"],
        "height": 36,
        "font_size": FONTS["size_normal"],
        "font_weight": FONTS["weight_bold"]
    },

    "button_secondary": {
        "fg_color": COLORS["bg_tertiary"],
        "hover_color": COLORS["bg_hover"],
        "text_color": COLORS["text_primary"],
        "border_color": COLORS["border_primary"],
        "corner_radius": BORDERS["radius_medium"],
        "height": 36,
        "font_size": FONTS["size_normal"],
        "font_weight": FONTS["weight_normal"]
    },

    "button_danger": {
        "fg_color": COLORS["error"],
        "hover_color": "#ff5252",
        "text_color": COLORS["text_on_accent"],
        "border_color": COLORS["error"],
        "corner_radius": BORDERS["radius_medium"],
        "height": 36,
        "font_size": FONTS["size_normal"],
        "font_weight": FONTS["weight_bold"]
    },

    # Tarjetas
    "card": {
        "fg_color": COLORS["bg_secondary"],
        "border_color": COLORS["border_primary"],
        "border_width": BORDERS["width_thin"],
        "corner_radius": BORDERS["radius_large"],
        "padding": SPACING["large"]
    },

    # Inputs
    "entry": {
        "fg_color": COLORS["bg_input"],
        "border_color": COLORS["border_primary"],
        "text_color": COLORS["text_primary"],
        "placeholder_text_color": COLORS["text_tertiary"],
        "corner_radius": BORDERS["radius_small"],
        "height": 32,
        "border_width": BORDERS["width_thin"]
    },

    # Frames
    "frame": {
        "fg_color": COLORS["bg_secondary"],
        "corner_radius": BORDERS["radius_medium"],
        "border_width": 0
    },

    # Labels
    "label": {
        "text_color": COLORS["text_primary"],
        "font_size": FONTS["size_normal"]
    },

    # Tabs
    "tabview": {
        "fg_color": COLORS["bg_secondary"],
        "segmented_button_fg_color": COLORS["bg_tertiary"],
        "segmented_button_selected_color": COLORS["accent_primary"],
        "segmented_button_selected_hover_color": "#00bd98",
        "segmented_button_unselected_color": COLORS["bg_tertiary"],
        "segmented_button_unselected_hover_color": COLORS["bg_hover"],
        "text_color": COLORS["text_primary"],
        "text_color_disabled": COLORS["text_disabled"]
    },

    # Progress bars
    "progressbar": {
        "fg_color": COLORS["bg_tertiary"],
        "progress_color": COLORS["accent_primary"],
        "border_color": COLORS["border_primary"],
        "height": 20,
        "corner_radius": BORDERS["radius_large"],
        "border_width": BORDERS["width_thin"]
    },

    # Switch/Toggle
    "switch": {
        "fg_color": COLORS["bg_tertiary"],
        "progress_color": COLORS["accent_primary"],
        "button_color": COLORS["text_on_accent"],
        "button_hover_color": COLORS["bg_hover"]
    },

    # Scrollbar
    "scrollbar": {
        "fg_color": COLORS["bg_secondary"],
        "button_color": COLORS["bg_tertiary"],
        "button_hover_color": COLORS["bg_hover"]
    }
}

# ==================== LAYOUTS ====================

LAYOUTS = {
    "sidebar_width": 300,
    "header_height": 60,
    "footer_height": 40,
    "panel_padding": SPACING["large"],
    "card_gap": SPACING["medium"],
    "form_field_gap": SPACING["small"],
    "section_gap": SPACING["xlarge"]
}

# ==================== GRÁFICOS (Matplotlib style) ====================

PLOT_STYLE = {
    "figure.facecolor": COLORS["plot_bg"],
    "axes.facecolor": COLORS["plot_bg"],
    "axes.edgecolor": COLORS["border_primary"],
    "axes.labelcolor": COLORS["text_primary"],
    "axes.grid": True,
    "grid.color": COLORS["plot_grid"],
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
    "xtick.color": COLORS["text_secondary"],
    "ytick.color": COLORS["text_secondary"],
    "text.color": COLORS["text_primary"],
    "lines.linewidth": 2,
    "font.size": FONTS["size_normal"],
    "legend.facecolor": COLORS["bg_tertiary"],
    "legend.edgecolor": COLORS["border_primary"],
    "legend.framealpha": 0.9
}

PLOT_COLORS = [
    COLORS["plot_line_1"],
    COLORS["plot_line_2"],
    COLORS["plot_line_3"],
    COLORS["plot_line_4"],
    COLORS["plot_line_5"],
    COLORS["plot_line_6"],
    COLORS["plot_line_7"]
]

# ==================== CUSTOMTKINTER THEME ====================

CTK_THEME = {
    "CTk": {
        "fg_color": [COLORS["bg_primary"], COLORS["bg_primary"]]
    },
    "CTkToplevel": {
        "fg_color": [COLORS["bg_primary"], COLORS["bg_primary"]]
    },
    "CTkFrame": {
        "corner_radius": BORDERS["radius_medium"],
        "border_width": 0,
        "fg_color": [COLORS["bg_secondary"], COLORS["bg_secondary"]],
        "top_fg_color": [COLORS["bg_tertiary"], COLORS["bg_tertiary"]],
        "border_color": [COLORS["border_primary"], COLORS["border_primary"]]
    },
    "CTkButton": {
        "corner_radius": BORDERS["radius_medium"],
        "border_width": 0,
        "fg_color": [COLORS["accent_primary"], COLORS["accent_primary"]],
        "hover_color": ["#00bd98", "#00bd98"],
        "border_color": [COLORS["border_primary"], COLORS["border_primary"]],
        "text_color": [COLORS["text_on_accent"], COLORS["text_on_accent"]],
        "text_color_disabled": [COLORS["text_disabled"], COLORS["text_disabled"]]
    },
    "CTkLabel": {
        "corner_radius": 0,
        "fg_color": "transparent",
        "text_color": [COLORS["text_primary"], COLORS["text_primary"]]
    },
    "CTkEntry": {
        "corner_radius": BORDERS["radius_small"],
        "border_width": BORDERS["width_thin"],
        "fg_color": [COLORS["bg_input"], COLORS["bg_input"]],
        "border_color": [COLORS["border_primary"], COLORS["border_primary"]],
        "text_color": [COLORS["text_primary"], COLORS["text_primary"]],
        "placeholder_text_color": [COLORS["text_tertiary"], COLORS["text_tertiary"]]
    },
    "CTkTextbox": {
        "corner_radius": BORDERS["radius_small"],
        "border_width": BORDERS["width_thin"],
        "fg_color": [COLORS["bg_input"], COLORS["bg_input"]],
        "border_color": [COLORS["border_primary"], COLORS["border_primary"]],
        "text_color": [COLORS["text_primary"], COLORS["text_primary"]],
        "scrollbar_button_color": [COLORS["bg_tertiary"], COLORS["bg_tertiary"]],
        "scrollbar_button_hover_color": [COLORS["bg_hover"], COLORS["bg_hover"]]
    },
    "CTkScrollbar": {
        "corner_radius": BORDERS["radius_large"],
        "border_spacing": 4,
        "fg_color": "transparent",
        "button_color": [COLORS["bg_tertiary"], COLORS["bg_tertiary"]],
        "button_hover_color": [COLORS["bg_hover"], COLORS["bg_hover"]]
    },
    "CTkCheckBox": {
        "corner_radius": BORDERS["radius_small"],
        "border_width": BORDERS["width_normal"],
        "fg_color": [COLORS["accent_primary"], COLORS["accent_primary"]],
        "border_color": [COLORS["border_primary"], COLORS["border_primary"]],
        "hover_color": ["#00bd98", "#00bd98"],
        "checkmark_color": [COLORS["text_on_accent"], COLORS["text_on_accent"]],
        "text_color": [COLORS["text_primary"], COLORS["text_primary"]],
        "text_color_disabled": [COLORS["text_disabled"], COLORS["text_disabled"]]
    },
    "CTkSwitch": {
        "corner_radius": BORDERS["radius_round"],
        "border_width": BORDERS["width_thick"],
        "button_length": 0,
        "fg_color": [COLORS["bg_tertiary"], COLORS["bg_tertiary"]],
        "progress_color": [COLORS["accent_primary"], COLORS["accent_primary"]],
        "button_color": [COLORS["text_on_accent"], COLORS["text_on_accent"]],
        "button_hover_color": [COLORS["bg_hover"], COLORS["bg_hover"]],
        "text_color": [COLORS["text_primary"], COLORS["text_primary"]],
        "text_color_disabled": [COLORS["text_disabled"], COLORS["text_disabled"]]
    },
    "CTkRadioButton": {
        "corner_radius": BORDERS["radius_round"],
        "border_width_checked": 6,
        "border_width_unchecked": BORDERS["width_thick"],
        "fg_color": [COLORS["accent_primary"], COLORS["accent_primary"]],
        "border_color": [COLORS["border_primary"], COLORS["border_primary"]],
        "hover_color": ["#00bd98", "#00bd98"],
        "text_color": [COLORS["text_primary"], COLORS["text_primary"]],
        "text_color_disabled": [COLORS["text_disabled"], COLORS["text_disabled"]]
    },
    "CTkProgressBar": {
        "corner_radius": BORDERS["radius_large"],
        "border_width": 0,
        "fg_color": [COLORS["bg_tertiary"], COLORS["bg_tertiary"]],
        "progress_color": [COLORS["accent_primary"], COLORS["accent_primary"]],
        "border_color": [COLORS["border_primary"], COLORS["border_primary"]]
    },
    "CTkSlider": {
        "corner_radius": BORDERS["radius_large"],
        "button_corner_radius": BORDERS["radius_round"],
        "border_width": 0,
        "button_length": 24,
        "fg_color": [COLORS["bg_tertiary"], COLORS["bg_tertiary"]],
        "progress_color": [COLORS["accent_primary"], COLORS["accent_primary"]],
        "button_color": [COLORS["text_on_accent"], COLORS["text_on_accent"]],
        "button_hover_color": ["#00bd98", "#00bd98"]
    },
    "CTkOptionMenu": {
        "corner_radius": BORDERS["radius_small"],
        "fg_color": [COLORS["bg_tertiary"], COLORS["bg_tertiary"]],
        "button_color": [COLORS["bg_hover"], COLORS["bg_hover"]],
        "button_hover_color": [COLORS["accent_primary"], COLORS["accent_primary"]],
        "text_color": [COLORS["text_primary"], COLORS["text_primary"]],
        "text_color_disabled": [COLORS["text_disabled"], COLORS["text_disabled"]]
    },
    "CTkComboBox": {
        "corner_radius": BORDERS["radius_small"],
        "border_width": BORDERS["width_thin"],
        "fg_color": [COLORS["bg_input"], COLORS["bg_input"]],
        "border_color": [COLORS["border_primary"], COLORS["border_primary"]],
        "button_color": [COLORS["bg_tertiary"], COLORS["bg_tertiary"]],
        "button_hover_color": [COLORS["bg_hover"], COLORS["bg_hover"]],
        "text_color": [COLORS["text_primary"], COLORS["text_primary"]],
        "text_color_disabled": [COLORS["text_disabled"], COLORS["text_disabled"]]
    },
    "CTkScrollableFrame": {
        "label_fg_color": [COLORS["bg_secondary"], COLORS["bg_secondary"]]
    },
    "CTkSegmentedButton": {
        "corner_radius": BORDERS["radius_small"],
        "border_width": 0,
        "fg_color": [COLORS["bg_tertiary"], COLORS["bg_tertiary"]],
        "selected_color": [COLORS["accent_primary"], COLORS["accent_primary"]],
        "selected_hover_color": ["#00bd98", "#00bd98"],
        "unselected_color": [COLORS["bg_tertiary"], COLORS["bg_tertiary"]],
        "unselected_hover_color": [COLORS["bg_hover"], COLORS["bg_hover"]],
        "text_color": [COLORS["text_primary"], COLORS["text_primary"]],
        "text_color_disabled": [COLORS["text_disabled"], COLORS["text_disabled"]]
    },
    "CTkTabview": {
        "corner_radius": BORDERS["radius_medium"],
        "border_width": 0,
        "fg_color": [COLORS["bg_secondary"], COLORS["bg_secondary"]],
        "segmented_button_fg_color": [COLORS["bg_tertiary"], COLORS["bg_tertiary"]],
        "segmented_button_selected_color": [COLORS["accent_primary"], COLORS["accent_primary"]],
        "segmented_button_selected_hover_color": ["#00bd98", "#00bd98"],
        "segmented_button_unselected_color": [COLORS["bg_tertiary"], COLORS["bg_tertiary"]],
        "segmented_button_unselected_hover_color": [COLORS["bg_hover"], COLORS["bg_hover"]],
        "text_color": [COLORS["text_primary"], COLORS["text_primary"]],
        "text_color_disabled": [COLORS["text_disabled"], COLORS["text_disabled"]]
    },
    "DropdownMenu": {
        "fg_color": [COLORS["bg_tertiary"], COLORS["bg_tertiary"]],
        "hover_color": [COLORS["bg_hover"], COLORS["bg_hover"]],
        "text_color": [COLORS["text_primary"], COLORS["text_primary"]]
    },
    "CTkFont": {
        "family": FONTS["family_primary"][0],
        "size": FONTS["size_normal"],
        "weight": FONTS["weight_normal"]
    }
}


# ==================== FUNCIONES AUXILIARES ====================

def get_color(color_name: str) -> str:
    """Obtiene un color de la paleta por nombre."""
    return COLORS.get(color_name, COLORS["text_primary"])


def get_component_style(component_name: str) -> Dict:
    """Obtiene el estilo de un componente específico."""
    return COMPONENTS.get(component_name, {})


def get_plot_color(index: int) -> str:
    """Obtiene un color para gráficos basado en índice (cíclico)."""
    return PLOT_COLORS[index % len(PLOT_COLORS)]


def apply_matplotlib_style():
    """Aplica el estilo personalizado a matplotlib."""
    import matplotlib.pyplot as plt
    plt.style.use('dark_background')
    plt.rcParams.update(PLOT_STYLE)
