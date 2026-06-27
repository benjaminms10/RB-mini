import os
import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QPlainTextEdit, QFrame
)
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt, QTimer

from .styles import (
    apply_neo_shadow, BG_CREAM, COLOR_WHITE, COLOR_BLACK, 
    ACCENT_PURPLE, ACCENT_YELLOW, ACCENT_LIME, ACCENT_RED, ACCENT_CYAN
)

# Define central log file path in the application directory
LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app_session.log")

def log_event(message, level="INFO"):
    """Utility function to log an event to the session log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level.upper()}] {message}\n"
    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except OSError:
        pass

def ensure_log_file():
    """Ensure the log file exists and contains initial setup events if empty."""
    if not os.path.exists(LOG_FILE_PATH) or os.path.getsize(LOG_FILE_PATH) == 0:
        log_event("Application session initialized.", "SYSTEM")
        log_event(f"Session log file created at: {LOG_FILE_PATH}", "SYSTEM")


class LogsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        ensure_log_file()
        
        self._last_file_size = 0
        self.init_ui()
        
        # Poll the log file for updates every 1 second
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.reload_logs_if_changed)
        self.poll_timer.start(1000)
        
        # Initial load
        self.reload_logs()

    def init_ui(self):
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(12)
        
        # 1. Header Panel
        self.header_panel = QFrame(self)
        self.header_panel.setObjectName("HeaderPanel")
        self.header_layout = QHBoxLayout(self.header_panel)
        self.header_layout.setContentsMargins(15, 12, 15, 12)
        
        self.title_label = QLabel("📋 SESSION LOGS", self.header_panel)
        self.title_label.setObjectName("TitleLabel")
        self.header_layout.addWidget(self.title_label)
        
        self.header_layout.addStretch()
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh", self.header_panel)
        self.refresh_btn.setObjectName("RefreshBtn")
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.reload_logs)
        self.header_layout.addWidget(self.refresh_btn)
        
        # Clear Logs button
        self.clear_btn = QPushButton("🗑️ Clear Logs", self.header_panel)
        self.clear_btn.setObjectName("ClearLogsBtn")
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_logs)
        self.header_layout.addWidget(self.clear_btn)
        
        self.main_layout.addWidget(self.header_panel)
        
        # 2. Monospace Console Area
        self.console_area = QPlainTextEdit(self)
        self.console_area.setObjectName("ConsoleArea")
        self.console_area.setReadOnly(True)
        self.main_layout.addWidget(self.console_area)
        
        # Apply shadow to the header panel
        apply_neo_shadow(self.header_panel, 4, 4)
        
        # Apply theme-compliant styles
        self.apply_styles()

    def apply_styles(self):
        title_font = QFont("Arial Black", 12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
            }}
            
            QFrame#HeaderPanel {{
                background-color: {ACCENT_CYAN};
                border: 3px solid #000000;
                border-radius: 0px;
            }}
            
            QLabel#TitleLabel {{
                font-family: 'Arial Black';
                font-size: 13px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            
            QPushButton#RefreshBtn {{
                background-color: {COLOR_WHITE};
                border: 3px solid #000000;
                border-radius: 0px;
                padding: 5px 12px;
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            
            QPushButton#RefreshBtn:hover {{
                background-color: {ACCENT_YELLOW};
            }}
            
            QPushButton#ClearLogsBtn {{
                background-color: {COLOR_WHITE};
                border: 3px solid #000000;
                border-radius: 0px;
                padding: 5px 12px;
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            
            QPushButton#ClearLogsBtn:hover {{
                background-color: {ACCENT_RED};
                color: {COLOR_WHITE};
            }}
            
            /* Monospace Console Styling */
            QPlainTextEdit#ConsoleArea {{
                background-color: #111827;
                color: #34D399; /* Mint/Emerald Green color */
                border: 3px solid #000000;
                border-radius: 0px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                font-weight: bold;
            }}
            
            /* Neo-brutalist ScrollBar Styling */
            QScrollBar:vertical {{
                border: 2px solid #000000;
                background: {BG_CREAM};
                width: 16px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {ACCENT_PURPLE};
                border: 2px solid #000000;
                min-height: 20px;
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: 2px solid #000000;
                background: {ACCENT_YELLOW};
                height: 16px;
                subcontrol-origin: margin;
            }}
            
            QScrollBar::add-line:vertical {{
                subcontrol-position: bottom;
            }}
            
            QScrollBar::sub-line:vertical {{
                subcontrol-position: top;
            }}
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}

            QScrollBar:horizontal {{
                border: 2px solid #000000;
                background: {BG_CREAM};
                height: 16px;
                margin: 0px;
            }}
            
            QScrollBar::handle:horizontal {{
                background: {ACCENT_PURPLE};
                border: 2px solid #000000;
                min-width: 20px;
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: 2px solid #000000;
                background: {ACCENT_YELLOW};
                width: 16px;
                subcontrol-origin: margin;
            }}
            
            QScrollBar::add-line:horizontal {{
                subcontrol-position: right;
            }}
            
            QScrollBar::sub-line:horizontal {{
                subcontrol-position: left;
            }}
            
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
        """)

    def reload_logs_if_changed(self):
        """Polls log file to check if it has grown, then reloads to update view."""
        try:
            if os.path.exists(LOG_FILE_PATH):
                current_size = os.path.getsize(LOG_FILE_PATH)
                if current_size != self._last_file_size:
                    self.reload_logs()
            else:
                if self._last_file_size != 0:
                    self.console_area.setPlainText("")
                    self._last_file_size = 0
        except OSError:
            pass

    def reload_logs(self):
        """Reads log file contents and appends them to the read-only console."""
        try:
            if os.path.exists(LOG_FILE_PATH):
                self._last_file_size = os.path.getsize(LOG_FILE_PATH)
                with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
                    log_data = f.read()
                
                scrollbar = self.console_area.verticalScrollBar()
                was_at_bottom = scrollbar.value() == scrollbar.maximum()
                
                self.console_area.setPlainText(log_data)
                
                # Auto-scroll if user was already at the bottom
                if was_at_bottom:
                    scrollbar.setValue(scrollbar.maximum())
            else:
                self.console_area.setPlainText("[ No logs recorded yet. ]")
                self._last_file_size = 0
        except OSError as e:
            self.console_area.setPlainText(f"Error reading session logs: {str(e)}")

    def clear_logs(self):
        """Truncates the log file and refreshes the console view."""
        try:
            with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
                f.write("")
            log_event("Logs cleared by user.", "SYSTEM")
            self.reload_logs()
        except OSError as e:
            self.console_area.appendPlainText(f"\n[ERROR] Failed to clear logs: {str(e)}")


# Standalone Demo / Test mode
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Write some initial mock log messages to showcase design
    log_event("Demo mode started.", "DEBUG")
    log_event("LogsTab UI initialized standalone.", "INFO")
    log_event("Rendered with Accent Cyan theme header and Dark monospace console.", "INFO")
    log_event("Click 'Clear Logs' or write code to log events.", "WARN")
    
    widget = LogsTab()
    widget.setWindowTitle("Neo-Brutalist Session Logs Demo")
    widget.resize(800, 500)
    widget.show()
    
    sys.exit(app.exec())
