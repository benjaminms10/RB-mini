import os
import json
from PyQt6.QtWidgets import QWidget, QGraphicsDropShadowEffect, QApplication, QStyle
from PyQt6.QtGui import QColor, QPainter, QFont, QIcon
from PyQt6.QtCore import Qt

def standard_icon(pixmap):
    app = QApplication.instance()
    if app:
        return app.style().standardIcon(pixmap)
    return QIcon()

# Define themes
THEME_PALETTES = {
    "lightmode": {
        "BG_CREAM": "#F9F5F6",
        "COLOR_WHITE": "#FFFFFF",
        "COLOR_BLACK": "#000000",
        "ACCENT_PURPLE": "#F2BED1",
        "ACCENT_YELLOW": "#FDCEDF",
        "ACCENT_LIME": "#F8E8EE",
        "ACCENT_CYAN": "#FDCEDF",
        "ACCENT_GREEN": "#A7F3D0",
        "ACCENT_RED": "#F87171",
        "ACCENT_OLIVE": "#F8E8EE"
    },
    "purple-haze": {
        "BG_CREAM": "#F4EEFF",
        "COLOR_WHITE": "#FFFFFF",
        "COLOR_BLACK": "#000000",
        "ACCENT_PURPLE": "#424874",
        "ACCENT_YELLOW": "#A6B1E1",
        "ACCENT_LIME": "#DCD6F7",
        "ACCENT_CYAN": "#A6B1E1",
        "ACCENT_GREEN": "#A7F3D0",
        "ACCENT_RED": "#F87171",
        "ACCENT_OLIVE": "#424874"
    }
}

# Load theme from config.json
active_theme = "lightmode"
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
if os.path.exists(config_path):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            if "theme" in cfg and cfg["theme"] in THEME_PALETTES:
                active_theme = cfg["theme"]
    except:
        pass

palette = THEME_PALETTES[active_theme]

# Color Palette Variables
BG_CREAM = palette["BG_CREAM"]
COLOR_WHITE = palette["COLOR_WHITE"]
COLOR_BLACK = palette["COLOR_BLACK"]
ACCENT_PURPLE = palette["ACCENT_PURPLE"]
ACCENT_YELLOW = palette["ACCENT_YELLOW"]
ACCENT_LIME = palette["ACCENT_LIME"]
ACCENT_CYAN = palette["ACCENT_CYAN"]
ACCENT_GREEN = palette["ACCENT_GREEN"]
ACCENT_RED = palette["ACCENT_RED"]
ACCENT_OLIVE = palette["ACCENT_OLIVE"]

class DottedGridWidget(QWidget):
    """A custom widget that renders a dotted grid paper background."""
    def __init__(self, parent=None, dot_color="#D4D4D8", bg_color=None):
        super().__init__(parent)
        self.dot_color = QColor(dot_color)
        self.bg_color = QColor(bg_color if bg_color else BG_CREAM)
        self.dot_spacing = 30
        self.dot_size = 2

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), self.bg_color)
        
        # Draw dots (only in lightmode, in darkmode grid is very faint or hidden for full blackness)
        if active_theme == "lightmode":
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self.dot_color)
            
            width = self.width()
            height = self.height()
            
            for x in range(15, width, self.dot_spacing):
                for y in range(15, height, self.dot_spacing):
                    painter.drawEllipse(x, y, self.dot_size, self.dot_size)

def apply_neo_shadow(widget, offset_x=4, offset_y=4, color=None):
    """Applies a flat, zero-blur neo-brutalist shadow to a widget."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(0)
    shadow.setOffset(offset_x, offset_y)
    shadow.setColor(QColor(color if color else COLOR_BLACK))
    widget.setGraphicsEffect(shadow)
    return shadow
