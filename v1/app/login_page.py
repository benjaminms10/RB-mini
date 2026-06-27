from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
)
from PyQt6.QtGui import QCursor
from PyQt6.QtCore import Qt
from .styles import DottedGridWidget, apply_neo_shadow, COLOR_WHITE, COLOR_BLACK, ACCENT_PURPLE, ACCENT_YELLOW, ACCENT_LIME, ACCENT_RED
from . import user_manager

class LoginPage(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.password_visible = False
        self.init_ui()

    def init_ui(self):
        # Create background
        bg_layout = QVBoxLayout(self)
        bg_layout.setContentsMargins(0, 0, 0, 0)
        
        background = DottedGridWidget(self)
        bg_layout.addWidget(background)

        # Center layout
        center_layout = QVBoxLayout(background)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.setContentsMargins(40, 40, 40, 40)

        # --- LOGIN CARD ---
        login_card = QFrame(background)
        login_card.setObjectName("LoginCard")
        login_card.setFixedSize(400, 400)
        apply_neo_shadow(login_card, 10, 10)

        card_layout = QVBoxLayout(login_card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # --- CARD HEADER ---
        header_frame = QFrame(login_card)
        header_frame.setObjectName("CardHeader")
        header_frame.setFixedHeight(80)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        header_layout.setSpacing(12)

        header_icon = QLabel("🗄️", header_frame)
        header_icon.setStyleSheet(f"font-size: 28px; color: {COLOR_WHITE};")
        
        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(2)
        header_text_layout.setContentsMargins(0, 0, 0, 0)
        
        header_title = QLabel("RB WORKBENCH", header_frame)
        header_title.setObjectName("HeaderTitle")
        
        header_subtitle = QLabel("Secure MySQL Access Portal", header_frame)
        header_subtitle.setObjectName("HeaderSubtitle")
        
        header_text_layout.addWidget(header_title)
        header_text_layout.addWidget(header_subtitle)
        
        header_layout.addWidget(header_icon)
        header_layout.addLayout(header_text_layout)
        header_layout.addStretch()
        
        card_layout.addWidget(header_frame)

        # --- CARD BODY (FORM) ---
        body_widget = QWidget(login_card)
        body_widget.setObjectName("CardBody")
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(25, 25, 25, 25)
        body_layout.setSpacing(15)

        # Username Input Section
        user_label_layout = QHBoxLayout()
        user_icon = QLabel("👤", body_widget)
        user_icon.setStyleSheet("font-size: 14px;")
        user_label = QLabel("USERNAME", body_widget)
        user_label.setObjectName("FieldLabel")
        user_label_layout.addWidget(user_icon)
        user_label_layout.addWidget(user_label)
        user_label_layout.addStretch()
        
        self.username_input = QLineEdit(body_widget)
        self.username_input.setPlaceholderText("admin_user")
        self.username_input.setObjectName("FormInput")
        
        body_layout.addLayout(user_label_layout)
        body_layout.addWidget(self.username_input)

        # Password Input Section
        pass_label_layout = QHBoxLayout()
        pass_icon = QLabel("🔒", body_widget)
        pass_icon.setStyleSheet("font-size: 14px;")
        pass_label = QLabel("PASSWORD", body_widget)
        pass_label.setObjectName("FieldLabel")
        pass_label_layout.addWidget(pass_icon)
        pass_label_layout.addWidget(pass_label)
        pass_label_layout.addStretch()
        
        self.password_input = QLineEdit(body_widget)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setObjectName("FormInput")
        
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
        
        self.password_input.setTextMargins(0, 0, 35, 0)
        self.password_input.resizeEvent = self.resize_password_input

        body_layout.addLayout(pass_label_layout)
        body_layout.addWidget(self.password_input)

        body_layout.addSpacing(5)

        # Login button
        self.login_btn = QPushButton("LOGIN", body_widget)
        self.login_btn.setObjectName("LoginBtn")
        self.login_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        apply_neo_shadow(self.login_btn, 4, 4)
        if self.controller:
            self.login_btn.clicked.connect(self.handle_login)
        body_layout.addWidget(self.login_btn)

        card_layout.addWidget(body_widget)
        center_layout.addWidget(login_card)

        # Create Account link under card
        signup_layout = QHBoxLayout()
        signup_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        signup_lbl = QLabel("Need administrative access?", background)
        signup_lbl.setStyleSheet(f"font-family: 'Arial'; font-size: 12px; font-weight: bold; color: {COLOR_BLACK};")
        
        signup_link = QPushButton("Create Account", background)
        signup_link.setObjectName("BottomLink")
        signup_link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        if self.controller:
            signup_link.clicked.connect(self.controller.show_signup)
            
        signup_layout.addWidget(signup_lbl)
        signup_layout.addWidget(signup_link)
        
        center_layout.addSpacing(15)
        center_layout.addLayout(signup_layout)

        # Stylesheet styling
        self.setStyleSheet(f"""
            QFrame#LoginCard {{
                background-color: {COLOR_WHITE};
                border: 4px solid {COLOR_BLACK};
                border-radius: 0px;
            }}
            QFrame#CardHeader {{
                background-color: {ACCENT_PURPLE};
                border-bottom: 4px solid {COLOR_BLACK};
            }}
            QLabel#HeaderTitle {{
                font-family: 'Arial Black';
                font-size: 18px;
                font-weight: 900;
                color: {COLOR_WHITE};
            }}
            QLabel#HeaderSubtitle {{
                font-family: 'Arial';
                font-size: 11px;
                font-weight: bold;
                color: {ACCENT_LIME};
            }}
            QWidget#CardBody {{
                background-color: {COLOR_WHITE};
            }}
            QLabel#FieldLabel {{
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                color: {COLOR_BLACK};
                letter-spacing: 0.5px;
            }}
            QLineEdit#FormInput {{
                background-color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                padding: 10px;
                font-family: 'Arial';
                font-size: 13px;
                font-weight: bold;
                color: {COLOR_BLACK};
            }}
            QLineEdit#FormInput:focus {{
                background-color: {ACCENT_LIME};
            }}
            QPushButton#LoginBtn {{
                background-color: {ACCENT_PURPLE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                color: {COLOR_WHITE};
                font-family: 'Arial Black';
                font-size: 14px;
                font-weight: 900;
                padding: 12px;
            }}
            QPushButton#LoginBtn:hover {{
                background-color: {ACCENT_YELLOW};
            }}
            QPushButton#LoginBtn:pressed {{
                background-color: {COLOR_BLACK};
                color: {COLOR_WHITE};
            }}
            QPushButton#BottomLink {{
                border: none;
                background: none;
                font-family: 'Arial Black';
                font-size: 12px;
                font-weight: 900;
                color: {ACCENT_PURPLE};
                text-decoration: underline;
                padding: 0px;
                margin-left: 5px;
            }}
            QPushButton#BottomLink:hover {{
                color: {COLOR_BLACK};
            }}
        """)

    def resize_password_input(self, event):
        # Resize/reposition the eye button inside the QLineEdit
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

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if user_manager.authenticate(username, password):
            if hasattr(self, "error_label"):
                self.error_label.hide()
            if self.controller:
                self.controller.show_dashboard(username)
        else:
            if not hasattr(self, "error_label"):
                self.error_label = QLabel("INVALID ACCESS CODES", self)
                self.error_label.setObjectName("ErrorLabel")
                self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.error_label.setStyleSheet(f"""
                    QLabel#ErrorLabel {{
                        color: {ACCENT_RED};
                        font-family: 'Arial Black';
                        font-size: 11px;
                        font-weight: 900;
                        border: 3px solid {COLOR_BLACK};
                        background-color: #FEE2E2;
                        padding: 8px;
                    }}
                """)
                layout = self.login_btn.parent().layout()
                layout.insertWidget(layout.indexOf(self.login_btn), self.error_label)
            self.error_label.show()
