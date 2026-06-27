import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QFrame,
    QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QColor, QFont, QCursor
from PyQt6.QtCore import Qt, QEvent

class NeoBrutalistWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEO-PORTAL // LOGIN")
        self.setMinimumSize(500, 650)
        self.init_ui()

    def init_ui(self):
        # Main central widget
        central_widget = QWidget(self)
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)

        # Main layout to center the login card
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Neo-Brutalist Login Card Container
        self.login_card = QFrame(self)
        self.login_card.setObjectName("LoginCard")
        self.login_card.setFixedWidth(400)
        self.login_card.setFixedHeight(520)

        # Shadow effect for the card (flat, black, offset)
        card_shadow = QGraphicsDropShadowEffect(self)
        card_shadow.setBlurRadius(0)
        card_shadow.setOffset(10, 10)
        card_shadow.setColor(QColor(0, 0, 0))
        self.login_card.setGraphicsEffect(card_shadow)

        # Card layout (holds header and body)
        card_layout = QVBoxLayout(self.login_card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # --- CARD HEADER ---
        header_frame = QFrame(self.login_card)
        header_frame.setObjectName("CardHeader")
        header_frame.setFixedHeight(50)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 0, 15, 0)
        
        header_title = QLabel("⚡ AUTHENTICATION REQUIRED", header_frame)
        header_title.setObjectName("HeaderTitle")
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        
        card_layout.addWidget(header_frame)

        # --- CARD BODY ---
        body_widget = QWidget(self.login_card)
        body_widget.setObjectName("CardBody")
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(25, 25, 25, 25)
        body_layout.setSpacing(15)

        # Welcome Text
        welcome_title = QLabel("WELCOME BACK", body_widget)
        welcome_title.setObjectName("WelcomeTitle")
        
        welcome_subtitle = QLabel("Please enter your access codes.", body_widget)
        welcome_subtitle.setObjectName("WelcomeSubtitle")
        
        body_layout.addWidget(welcome_title)
        body_layout.addWidget(welcome_subtitle)
        body_layout.addSpacing(10)

        # Form - Username/Email Field
        email_label = QLabel("EMAIL / USERNAME", body_widget)
        email_label.setObjectName("FieldLabel")
        self.email_input = QLineEdit(body_widget)
        self.email_input.setPlaceholderText("e.g. user@domain.com")
        
        body_layout.addWidget(email_label)
        body_layout.addWidget(self.email_input)

        # Form - Password Field
        password_label = QLabel("PASSWORD", body_widget)
        password_label.setObjectName("FieldLabel")
        self.password_input = QLineEdit(body_widget)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("••••••••")
        
        body_layout.addWidget(password_label)
        body_layout.addWidget(self.password_input)

        # Form - Remember & Forgot Row
        options_layout = QHBoxLayout()
        self.remember_cb = QCheckBox("REMEMBER ME", body_widget)
        self.remember_cb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        forgot_btn = QPushButton("FORGOT PASSWORD?", body_widget)
        forgot_btn.setObjectName("ForgotBtn")
        forgot_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        options_layout.addWidget(self.remember_cb)
        options_layout.addStretch()
        options_layout.addWidget(forgot_btn)
        body_layout.addLayout(options_layout)
        body_layout.addSpacing(10)

        # Form - Login Button
        self.login_btn = QPushButton("ACCESS SYSTEM →", body_widget)
        self.login_btn.setObjectName("LoginBtn")
        self.login_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Shadow effect for the button
        btn_shadow = QGraphicsDropShadowEffect(self)
        btn_shadow.setBlurRadius(0)
        btn_shadow.setOffset(4, 4)
        btn_shadow.setColor(QColor(0, 0, 0))
        self.login_btn.setGraphicsEffect(btn_shadow)
        
        # Dynamic press effect for button shadow
        self.login_btn.installEventFilter(self)
        
        body_layout.addWidget(self.login_btn)
        body_layout.addSpacing(5)

        # Sign Up Row
        signup_layout = QHBoxLayout()
        signup_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        signup_text = QLabel("NEW USER?", body_widget)
        signup_text.setObjectName("SignUpText")
        
        signup_btn = QPushButton("CREATE AN ACCOUNT", body_widget)
        signup_btn.setObjectName("SignUpBtn")
        signup_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        signup_layout.addWidget(signup_text)
        signup_layout.addWidget(signup_btn)
        body_layout.addLayout(signup_layout)

        card_layout.addWidget(body_widget)
        main_layout.addWidget(self.login_card)

        # Apply Global Stylesheet (QSS)
        self.setStyleSheet("""
            QWidget#CentralWidget {
                background-color: #FFF9E6; /* Warm neo-brutalist pastel yellow background */
            }
            
            QFrame#LoginCard {
                background-color: #FFFFFF;
                border: 4px solid #000000;
            }
            
            QFrame#CardHeader {
                background-color: #22D3EE; /* Vibrant Neo-brutalist Cyan */
                border-bottom: 4px solid #000000;
            }
            
            QLabel#HeaderTitle {
                font-family: 'Courier New', monospace;
                font-size: 13px;
                font-weight: 900;
                color: #000000;
                letter-spacing: 1px;
            }
            
            QWidget#CardBody {
                background-color: #FFFFFF;
            }
            
            QLabel#WelcomeTitle {
                font-family: 'Arial Black';
                font-size: 32px;
                font-weight: 900;
                color: #000000;
                margin-bottom: 0px;
            }
            
            QLabel#WelcomeSubtitle {
                font-family: 'Arial';
                font-size: 13px;
                font-weight: bold;
                color: #000000;
            }
            
            QLabel#FieldLabel {
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                color: #000000;
                letter-spacing: 0.5px;
            }
            
            QLineEdit {
                background-color: #FFFFFF;
                border: 3px solid #000000;
                border-radius: 0px;
                padding: 12px;
                font-family: 'Arial';
                font-size: 14px;
                font-weight: bold;
                color: #000000;
            }
            
            QLineEdit:focus {
                background-color: #A7F3D0; /* Vibrant mint green on focus */
            }
            
            QCheckBox {
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                color: #000000;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 3px solid #000000;
                background-color: #FFFFFF;
            }
            
            QCheckBox::indicator:checked {
                background-color: #F87171; /* Neo-brutalist warm red */
            }
            
            QPushButton#ForgotBtn {
                border: none;
                background: none;
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                color: #000000;
                text-decoration: underline;
            }
            
            QPushButton#ForgotBtn:hover {
                color: #FF5F5F;
            }
            
            QPushButton#LoginBtn {
                background-color: #FFDE4D; /* Signature vibrant yellow */
                border: 3px solid #000000;
                border-radius: 0px;
                color: #000000;
                font-family: 'Arial Black';
                font-size: 15px;
                font-weight: 900;
                padding: 14px;
                margin-right: 4px; /* leave room for offset shadow */
                margin-bottom: 4px;
            }
            
            QPushButton#LoginBtn:hover {
                background-color: #FACC15;
            }
            
            QLabel#SignUpText {
                font-family: 'Arial';
                font-size: 12px;
                font-weight: bold;
                color: #000000;
            }
            
            QPushButton#SignUpBtn {
                border: none;
                background: none;
                font-family: 'Arial Black';
                font-size: 12px;
                font-weight: 900;
                color: #000000;
                text-decoration: underline;
            }
            
            QPushButton#SignUpBtn:hover {
                color: #22D3EE;
            }
        """)

    def eventFilter(self, obj, event):
        # Enhance interaction feedback by modifying the shadow offset on press to simulate a real button push.
        if obj == self.login_btn:
            if event.type() == QEvent.Type.MouseButtonPress:
                effect = self.login_btn.graphicsEffect()
                if effect:
                    effect.setOffset(1, 1)  # Depress the button visual shadow
            elif event.type() == QEvent.Type.MouseButtonRelease:
                effect = self.login_btn.graphicsEffect()
                if effect:
                    effect.setOffset(4, 4)  # Restore the button visual shadow
        return super().eventFilter(obj, event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NeoBrutalistWindow()
    window.show()
    sys.exit(app.exec())
