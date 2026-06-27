import os
import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QApplication, QComboBox
)
from PyQt6.QtGui import QColor, QFont, QCursor, QIntValidator
from PyQt6.QtCore import Qt, QPoint
import mysql.connector

from .styles import apply_neo_shadow, BG_CREAM, COLOR_WHITE, COLOR_BLACK, ACCENT_PURPLE, ACCENT_YELLOW, ACCENT_LIME, ACCENT_CYAN, ACCENT_GREEN, ACCENT_RED
from .config_helper import load_connection_details, save_connection_details

class ConnectionSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MySQL Connection Settings")
        self.setFixedSize(450, 640) # Increased height from 580 to 640 to fit theme selector
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        
        self.drag_position = QPoint()
        self.password_visible = False
        self.initial_theme = load_connection_details().get("theme", "lightmode")
        self.logout_requested = False
        
        self.init_ui()
        self.load_settings()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def init_ui(self):
        # Main layout with zero margins and spacing
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- HEADER ---
        self.header_frame = QFrame(self)
        self.header_frame.setObjectName("DialogHeader")
        self.header_frame.setFixedHeight(60)
        
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        header_title = QLabel("CONNECTION CONFIG", self.header_frame)
        header_title.setObjectName("HeaderTitle")
        
        self.close_btn = QPushButton("✕", self.header_frame)
        self.close_btn.setObjectName("CloseBtn")
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.close_btn.clicked.connect(self.reject)
        
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addWidget(self.close_btn)
        
        main_layout.addWidget(self.header_frame)

        # --- BODY ---
        body_widget = QFrame(self)
        body_widget.setObjectName("DialogBody")
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(25, 20, 25, 25)
        body_layout.setSpacing(12)

        # Host & Port row
        host_port_layout = QHBoxLayout()
        host_port_layout.setSpacing(15)

        # Host input
        host_v_layout = QVBoxLayout()
        host_v_layout.setSpacing(4)
        host_label = QLabel("HOST / IP ADDRESS", body_widget)
        host_label.setObjectName("FieldLabel")
        self.host_input = QLineEdit(body_widget)
        self.host_input.setObjectName("FormInput")
        self.host_input.setPlaceholderText("localhost")
        host_v_layout.addWidget(host_label)
        host_v_layout.addWidget(self.host_input)
        host_port_layout.addLayout(host_v_layout, 7) # 70% width

        # Port input
        port_v_layout = QVBoxLayout()
        port_v_layout.setSpacing(4)
        port_label = QLabel("PORT", body_widget)
        port_label.setObjectName("FieldLabel")
        self.port_input = QLineEdit(body_widget)
        self.port_input.setObjectName("FormInput")
        self.port_input.setPlaceholderText("3306")
        self.port_input.setValidator(QIntValidator(1, 65535, self))
        port_v_layout.addWidget(port_label)
        port_v_layout.addWidget(self.port_input)
        host_port_layout.addLayout(port_v_layout, 3) # 30% width

        body_layout.addLayout(host_port_layout)

        # Database input
        db_label = QLabel("DEFAULT DATABASE", body_widget)
        db_label.setObjectName("FieldLabel")
        self.db_input = QLineEdit(body_widget)
        self.db_input.setObjectName("FormInput")
        self.db_input.setPlaceholderText("mysql")
        body_layout.addWidget(db_label)
        body_layout.addWidget(self.db_input)

        # User input
        user_label = QLabel("USERNAME", body_widget)
        user_label.setObjectName("FieldLabel")
        self.user_input = QLineEdit(body_widget)
        self.user_input.setObjectName("FormInput")
        self.user_input.setPlaceholderText("root")
        body_layout.addWidget(user_label)
        body_layout.addWidget(self.user_input)

        # Password input
        pass_label = QLabel("PASSWORD", body_widget)
        pass_label.setObjectName("FieldLabel")
        self.password_input = QLineEdit(body_widget)
        self.password_input.setObjectName("FormInput")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("••••••••")
        
        # Add password visibility toggle inside the line edit
        self.eye_btn = QPushButton("👁️", self.password_input)
        self.eye_btn.setObjectName("EyeBtn")
        self.eye_btn.setFixedSize(30, 30)
        self.eye_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.eye_btn.setStyleSheet("""
            QPushButton#EyeBtn {
                border: none;
                background: none;
                font-size: 16px;
            }
        """)
        self.eye_btn.clicked.connect(self.toggle_password_visibility)
        
        # Position eye button inside line edit
        self.password_input.setTextMargins(0, 0, 35, 0)
        self.password_input.resizeEvent = self.resize_password_input

        body_layout.addWidget(pass_label)
        body_layout.addWidget(self.password_input)

        # Theme selection
        theme_label = QLabel("APPLICATION THEME", body_widget)
        theme_label.setObjectName("FieldLabel")
        self.theme_combo = QComboBox(body_widget)
        self.theme_combo.setObjectName("FormCombo")
        self.theme_combo.addItems(["lightmode", "purple-haze"])
        body_layout.addWidget(theme_label)
        body_layout.addWidget(self.theme_combo)

        # Status badge for Test Connection feedback
        self.status_badge = QFrame(body_widget)
        self.status_badge.setObjectName("StatusBadge")
        self.status_badge.setFixedHeight(38)
        self.status_badge.hide()
        
        status_badge_layout = QHBoxLayout(self.status_badge)
        status_badge_layout.setContentsMargins(12, 4, 12, 4)
        self.status_lbl = QLabel("", self.status_badge)
        self.status_lbl.setObjectName("StatusText")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_badge_layout.addWidget(self.status_lbl)
        body_layout.addWidget(self.status_badge)

        body_layout.addSpacing(5)

        # Actions Layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        self.test_btn = QPushButton("TEST CONNECTION", body_widget)
        self.test_btn.setObjectName("TestBtn")
        self.test_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.test_btn.clicked.connect(self.test_connection)
        apply_neo_shadow(self.test_btn, 3, 3)

        self.save_btn = QPushButton("SAVE SETTINGS", body_widget)
        self.save_btn.setObjectName("SaveBtn")
        self.save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.save_btn.clicked.connect(self.save_settings)
        apply_neo_shadow(self.save_btn, 3, 3)

        self.cancel_btn = QPushButton("CANCEL", body_widget)
        self.cancel_btn.setObjectName("CancelBtn")
        self.cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.cancel_btn.clicked.connect(self.reject)
        apply_neo_shadow(self.cancel_btn, 3, 3)

        self.logout_btn = QPushButton("LOGOUT", body_widget)
        self.logout_btn.setObjectName("LogoutBtn")
        self.logout_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.logout_btn.clicked.connect(self.handle_logout)
        apply_neo_shadow(self.logout_btn, 3, 3)

        buttons_layout.addWidget(self.test_btn, 3)
        buttons_layout.addWidget(self.save_btn, 3)
        buttons_layout.addWidget(self.logout_btn, 2)
        buttons_layout.addWidget(self.cancel_btn, 2)
        
        body_layout.addLayout(buttons_layout)
        main_layout.addWidget(body_widget)

        # Custom stylesheets mapping to style guide colors
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BG_CREAM};
                border: 4px solid {COLOR_BLACK};
            }}
            QFrame#DialogHeader {{
                background-color: {ACCENT_YELLOW};
                border-bottom: 4px solid {COLOR_BLACK};
            }}
            QLabel#HeaderTitle {{
                font-family: 'Arial Black';
                font-size: 13px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            QPushButton#CloseBtn {{
                border: 2px solid {COLOR_BLACK};
                background-color: {COLOR_WHITE};
                font-family: 'Arial';
                font-size: 12px;
                font-weight: bold;
                color: {COLOR_BLACK};
            }}
            QPushButton#CloseBtn:hover {{
                background-color: {ACCENT_RED};
            }}
            QFrame#DialogBody {{
                background-color: {BG_CREAM};
            }}
            QLabel#FieldLabel {{
                font-family: 'Arial Black';
                font-size: 10px;
                font-weight: 900;
                color: {COLOR_BLACK};
                letter-spacing: 0.5px;
            }}
            QLineEdit#FormInput {{
                background-color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                padding: 8px;
                font-family: 'Arial';
                font-size: 12px;
                font-weight: bold;
                color: {COLOR_BLACK};
            }}
            QLineEdit#FormInput:focus {{
                background-color: {ACCENT_LIME};
            }}
            QComboBox#FormCombo {{
                background-color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                padding: 6px;
                font-family: 'Arial';
                font-size: 12px;
                font-weight: bold;
                color: {COLOR_BLACK};
            }}
            QComboBox#FormCombo:focus {{
                background-color: {ACCENT_LIME};
            }}
            QComboBox#FormCombo QAbstractItemView {{
                background-color: {COLOR_WHITE};
                color: {COLOR_BLACK};
                selection-background-color: {ACCENT_PURPLE};
                selection-color: {COLOR_WHITE};
                border: 2px solid {COLOR_BLACK};
                outline: none;
            }}
            QFrame#StatusBadge {{
                border: 2px solid {COLOR_BLACK};
                border-radius: 0px;
            }}
            QLabel#StatusText {{
                font-family: 'Arial Black';
                font-size: 10px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            QPushButton#TestBtn {{
                background-color: {ACCENT_CYAN};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                color: {COLOR_BLACK};
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                padding: 10px 5px;
            }}
            QPushButton#TestBtn:hover {{
                background-color: #06B6D4;
            }}
            QPushButton#TestBtn:pressed {{
                background-color: {COLOR_BLACK};
                color: {COLOR_WHITE};
            }}
            QPushButton#SaveBtn {{
                background-color: {ACCENT_PURPLE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                color: {COLOR_WHITE};
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                padding: 10px 5px;
            }}
            QPushButton#SaveBtn:hover {{
                background-color: #7C3AED;
            }}
            QPushButton#SaveBtn:pressed {{
                background-color: {COLOR_BLACK};
                color: {COLOR_WHITE};
            }}
            QPushButton#CancelBtn {{
                background-color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                color: {COLOR_BLACK};
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                padding: 10px 5px;
            }}
            QPushButton#CancelBtn:hover {{
                background-color: #E5E7EB;
            }}
            QPushButton#CancelBtn:pressed {{
                background-color: {COLOR_BLACK};
                color: {COLOR_WHITE};
            }}
            QPushButton#LogoutBtn {{
                background-color: {ACCENT_RED};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                color: {COLOR_BLACK};
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                padding: 10px 5px;
            }}
            QPushButton#LogoutBtn:hover {{
                background-color: #EF4444;
                color: {COLOR_WHITE};
            }}
            QPushButton#LogoutBtn:pressed {{
                background-color: {COLOR_BLACK};
                color: {COLOR_WHITE};
            }}
        """)

    def resize_password_input(self, event):
        self.eye_btn.move(self.password_input.width() - 32, (self.password_input.height() - 30) // 2)

    def toggle_password_visibility(self):
        if self.password_visible:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.eye_btn.setText("👁️")
            self.password_visible = False
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.eye_btn.setText("🙈")
            self.password_visible = True

    def load_settings(self):
        config = load_connection_details()
        self.host_input.setText(config.get("host", "localhost"))
        self.port_input.setText(str(config.get("port", 3306)))
        self.db_input.setText(config.get("database", "mysql"))
        self.user_input.setText(config.get("user", "root"))
        self.password_input.setText(config.get("password", ""))
        self.theme_combo.setCurrentText(config.get("theme", "lightmode"))

    def show_status(self, text, is_error=False, is_pending=False):
        self.status_lbl.setText(text)
        if is_pending:
            self.status_badge.setStyleSheet(f"background-color: {ACCENT_YELLOW}; border: 2px solid {COLOR_BLACK};")
        elif is_error:
            self.status_badge.setStyleSheet(f"background-color: {ACCENT_RED}; border: 2px solid {COLOR_BLACK};")
        else:
            self.status_badge.setStyleSheet(f"background-color: {ACCENT_GREEN}; border: 2px solid {COLOR_BLACK};")
        self.status_badge.show()

    def test_connection(self):
        host = self.host_input.text().strip()
        port_str = self.port_input.text().strip()
        database = self.db_input.text().strip()
        user = self.user_input.text().strip()
        password = self.password_input.text()
        
        try:
            port = int(port_str)
        except ValueError:
            self.show_status("Invalid Port Number", is_error=True)
            return

        self.show_status("Testing connection...", is_error=False, is_pending=True)
        # Process events so the UI updates to show the pending status
        QApplication.processEvents()

        try:
            conn = mysql.connector.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                connect_timeout=3,
                auth_plugin='mysql_native_password'
            )
            if conn.is_connected():
                conn.close()
                self.show_status("Connection Successful! ⚡", is_error=False)
            else:
                self.show_status("Connection Failed", is_error=True)
        except Exception as e:
            # Shorten message if too long
            err_msg = str(e)
            if len(err_msg) > 60:
                err_msg = err_msg[:57] + "..."
            self.show_status(f"Failed: {err_msg}", is_error=True)

    def save_settings(self):
        host = self.host_input.text().strip()
        port_str = self.port_input.text().strip()
        database = self.db_input.text().strip()
        user = self.user_input.text().strip()
        password = self.password_input.text()
        theme = self.theme_combo.currentText()
        
        try:
            port = int(port_str)
        except ValueError:
            self.show_status("Invalid Port Number", is_error=True)
            return
            
        details = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
            "theme": theme
        }
        
        if save_connection_details(details):
            if theme != self.initial_theme:
                # Trigger clean in-place app restart
                import os
                import sys
                os.execv(sys.executable, [sys.executable] + sys.argv)
            self.accept()
        else:
            self.show_status("Failed to save config.json", is_error=True)

    def handle_logout(self):
        self.logout_requested = True
        self.accept()
