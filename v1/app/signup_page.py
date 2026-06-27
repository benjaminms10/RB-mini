from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QCursor
from .styles import DottedGridWidget, apply_neo_shadow, BG_CREAM, COLOR_WHITE, COLOR_BLACK, ACCENT_PURPLE, ACCENT_YELLOW, ACCENT_LIME
from . import user_manager

class SignUpPage(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        # Create background
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        background = DottedGridWidget(self)
        layout.addWidget(background)

        # Content layout
        content = QVBoxLayout(background)
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content.setContentsMargins(40, 20, 40, 20)

        # Title
        title = QLabel("SIGN UP")
        title.setFont(QFont("Arial Black", 20))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content.addWidget(title)

        subtitle = QLabel("Create your administrator account")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content.addWidget(subtitle)
        content.addSpacing(20)

        # Card
        card = QFrame(background)
        card.setFixedSize(400, 580)
        card.setObjectName("SignUpCard")
        card.setStyleSheet(f"""
            QFrame#SignUpCard {{
                background-color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
            }}
            QLabel {{
                border: none;
                background: transparent;
                font-family: 'Arial Black';
                font-size: 10px;
                font-weight: 900;
                color: {COLOR_BLACK};
                letter-spacing: 0.5px;
            }}
            QLineEdit {{
                background-color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                padding: 8px 10px;
                font-family: 'Arial';
                font-size: 12px;
                font-weight: bold;
                color: {COLOR_BLACK};
            }}
            QLineEdit:focus {{
                background-color: {ACCENT_LIME};
            }}
        """)
        apply_neo_shadow(card, 8, 8)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(12)

        # Full Name
        card_layout.addWidget(QLabel("FULL NAME"))
        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText("Admin User")
        card_layout.addWidget(self.fullname_input)

        # Username
        card_layout.addWidget(QLabel("USERNAME"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("root_v2")
        card_layout.addWidget(self.username_input)

        # Email
        card_layout.addWidget(QLabel("EMAIL"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("admin@localhost")
        card_layout.addWidget(self.email_input)

        # Password
        card_layout.addWidget(QLabel("PASSWORD"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("••••••••")
        card_layout.addWidget(self.password_input)

        # Confirm Password
        card_layout.addWidget(QLabel("CONFIRM PASSWORD"))
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("••••••••")
        card_layout.addWidget(self.confirm_password_input)

        card_layout.addSpacing(10)

        # CREATE ACCOUNT BUTTON
        self.create_btn = QPushButton("CREATE ACCOUNT")
        self.create_btn.setFont(QFont("Arial Black", 12))
        self.create_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.create_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_PURPLE};
                color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
                padding: 10px;
            }}
            QPushButton:hover {{ background: {ACCENT_YELLOW}; }}
            QPushButton:pressed {{ background: {COLOR_BLACK}; }}
        """)
        apply_neo_shadow(self.create_btn, 4, 4)
        
        # ✅ Connect to handle_signup
        self.create_btn.clicked.connect(self.handle_signup)
        card_layout.addWidget(self.create_btn)

        # Login link
        login_link = QPushButton("Already have an account? Log In")
        login_link.setStyleSheet("border: none; background: none; font-weight: bold; text-decoration: underline;")
        login_link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        login_link.clicked.connect(self.go_to_login)
        card_layout.addWidget(login_link, alignment=Qt.AlignmentFlag.AlignCenter)

        content.addWidget(card)

    # ✅ ADD THIS METHOD
    def handle_signup(self):
        """Handle sign-up button click"""
        if not self.controller:
            return
            
        # Get form data
        fullname = self.fullname_input.text().strip()
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        confirm = self.confirm_password_input.text().strip()
        
        # Validate 1
        if not fullname or not username or not email or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields!")
            return
        #validate 2
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match!")
            return
        #validation 3
        if self.username_exists(username):
            QMessageBox.warning(self,"ERROR","username already exist.so please choose another")
            return
        #save users data
        self.save_user(fullname,username,email,password)
        
        #show success
        QMessageBox.information(self,
                                "ACCOUNT CREATED",f"WELCOME!,{fullname}!\n\nyour account has been  created successfully!")
        # Navigate to dashboard
        if self.controller:
            self.controller.show_dashboard(username)

    def username_exists(self, username):
        """Check if username already exists in storage"""
        return user_manager.username_exists(username)

    def save_user(self, fullname, username, email, password):
        """Save new user via user_manager"""
        user_manager.add_user(fullname, username, email, password)

    def go_to_login(self):
        if self.controller:
            self.controller.show_login()