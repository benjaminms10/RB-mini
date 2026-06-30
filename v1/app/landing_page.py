import webbrowser
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtGui import QColor, QFont, QCursor, QPainter
from PyQt6.QtCore import Qt
from .styles import DottedGridWidget, apply_neo_shadow, BG_CREAM, COLOR_WHITE, COLOR_BLACK, ACCENT_PURPLE, ACCENT_YELLOW, ACCENT_LIME, ACCENT_GREEN, ACCENT_RED

class LandingBackgroundWidget(DottedGridWidget):
    """Custom background that draws the dotted grid and large background texts."""
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw big text "SQL" near top-right
        painter.setFont(QFont("Arial Black", 130, QFont.Weight.Black))
        painter.setPen(QColor("#E4E4E7"))
        painter.drawText(self.width() - 360, 200, "SQL")
        
        # Draw big text "RB" near bottom-left
        painter.drawText(60, self.height() - 80, "RB")

class LandingPage(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        # Create background
        bg_layout = QVBoxLayout(self)
        bg_layout.setContentsMargins(0, 0, 0, 0)
        
        background = LandingBackgroundWidget(self)
        bg_layout.addWidget(background)

        # Content overlay layout
        content_layout = QHBoxLayout(background)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.setSpacing(40)
        content_layout.setContentsMargins(50, 50, 50, 50)

        # =====================================================================
        # LEFT COLUMN: Welcome Info Card
        # =====================================================================
        left_card = QFrame(background)
        left_card.setObjectName("LeftCard")
        left_card.setFixedSize(400, 380)
        apply_neo_shadow(left_card, 8, 8)

        left_card_layout = QVBoxLayout(left_card)
        left_card_layout.setContentsMargins(25, 25, 25, 25)
        left_card_layout.setSpacing(15)

        # Brand / Logo Header
        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(10)
        
        db_icon_label = QLabel("🗄️", left_card)
        db_icon_label.setStyleSheet("font-size: 24px;")
        
        brand_label = QLabel("RB", left_card)
        brand_label.setObjectName("BrandLabel")
        
        brand_layout.addWidget(db_icon_label)
        brand_layout.addWidget(brand_label)
        brand_layout.addStretch()
        left_card_layout.addLayout(brand_layout)

        # Welcome Text with Purple Highlight (Rich Text)
        welcome_title = QLabel(
            f'WELCOME TO <span style="color:{ACCENT_PURPLE};">MYSQL</span><br>MINI WORKBENCH', 
            left_card
        )
        welcome_title.setObjectName("WelcomeTitle")
        welcome_title.setWordWrap(True)
        left_card_layout.addWidget(welcome_title)

        # Description Subtext
        description_label = QLabel(
            "The raw, high-energy database manager built for speed. "
            "Query, manage, and scale your data with unapologetic power.", 
            left_card
        )
        description_label.setObjectName("DescriptionText")
        description_label.setWordWrap(True)
        left_card_layout.addWidget(description_label)
        left_card_layout.addStretch()

        # Connection Status Box
        status_box = QFrame(left_card)
        status_box.setObjectName("StatusBox")
        status_box_layout = QVBoxLayout(status_box)
        status_box_layout.setContentsMargins(15, 12, 15, 12)
        status_box_layout.setSpacing(6)

        # Status Header Row
        status_header_layout = QHBoxLayout()
        status_header_label = QLabel("CONNECTION STATUS", status_box)
        status_header_label.setObjectName("StatusHeaderLabel")
        
        status_dot = QLabel("●", status_box)
        status_dot.setObjectName("StatusDot")
        
        status_header_layout.addWidget(status_header_label)
        status_header_layout.addStretch()
        status_header_layout.addWidget(status_dot)
        status_box_layout.addLayout(status_header_layout)

        # Console Code Snippet
        code_line_1 = QLabel("> SELECT * FROM rb_users;", status_box)
        code_line_1.setObjectName("StatusConsoleLine")
        
        code_line_2 = QLabel("> Query executed in 0.002s", status_box)
        code_line_2.setObjectName("StatusConsoleLine")
        
        status_box_layout.addWidget(code_line_1)
        status_box_layout.addWidget(code_line_2)

        left_card_layout.addWidget(status_box)
        content_layout.addWidget(left_card)

        # =====================================================================
        # RIGHT COLUMN: Authentication Actions
        # =====================================================================
        right_column_layout = QVBoxLayout()
        right_column_layout.setSpacing(15)
        right_column_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Purple Header Panel: "READY TO CODE?"
        ready_card = QFrame(background)
        ready_card.setObjectName("ReadyCard")
        ready_card.setFixedSize(300, 110)
        apply_neo_shadow(ready_card, 6, 6)

        ready_layout = QVBoxLayout(ready_card)
        ready_layout.setContentsMargins(15, 15, 15, 15)
        ready_layout.setSpacing(8)
        ready_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        code_icon = QLabel("💻", ready_card)
        code_icon.setObjectName("CodeIcon")
        code_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        ready_title = QLabel("READY TO CODE?", ready_card)
        ready_title.setObjectName("ReadyTitle")
        ready_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        ready_layout.addWidget(code_icon)
        ready_layout.addWidget(ready_title)
        right_column_layout.addWidget(ready_card)

        # LOG IN Button
        self.login_btn = QPushButton("LOG IN →", background)
        self.login_btn.setObjectName("LandingLoginBtn")
        self.login_btn.setFixedSize(300, 50)
        self.login_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        apply_neo_shadow(self.login_btn, 4, 4)
        if self.controller:
            self.login_btn.clicked.connect(self.controller.show_login)
        right_column_layout.addWidget(self.login_btn)


        # Link: CREATE ONE
        signup_row = QHBoxLayout()
        signup_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        signup_desc = QLabel("Don't have an account?", background)
        signup_desc.setObjectName("SignupDescLabel")
        
        self.create_btn = QPushButton("CREATE ONE", background)
        self.create_btn.setObjectName("CreateBtn")
        self.create_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        if self.controller:
            self.create_btn.clicked.connect(self.controller.show_signup)
            
        signup_row.addWidget(signup_desc)
        signup_row.addWidget(self.create_btn)
        right_column_layout.addLayout(signup_row)
        right_column_layout.addSpacing(10)

        # Bottom row: DOCS / SUPPORT Buttons
        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.setSpacing(15)

        self.docs_btn = QPushButton("DOCS", background)
        self.docs_btn.setObjectName("DocsBtn")
        self.docs_btn.setFixedSize(142, 40)
        self.docs_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        apply_neo_shadow(self.docs_btn, 3, 3)
        self.docs_btn.clicked.connect(self.direct_to_readme)

        self.support_btn = QPushButton("SUPPORT", background)
        self.support_btn.setObjectName("SupportBtn")
        self.support_btn.setFixedSize(143, 40)
        self.support_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        apply_neo_shadow(self.support_btn, 3, 3)

        bottom_buttons_layout.addWidget(self.docs_btn)
        bottom_buttons_layout.addWidget(self.support_btn)
        right_column_layout.addLayout(bottom_buttons_layout)

        content_layout.addLayout(right_column_layout)

        # Apply Stylesheet
        self.setStyleSheet(f"""
            QFrame#LeftCard {{
                background-color: {COLOR_WHITE};
                border: 4px solid {COLOR_BLACK};
                border-radius: 0px;
            }}
            QLabel#BrandLabel {{
                font-family: 'Arial Black';
                font-size: 20px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            QLabel#WelcomeTitle {{
                font-family: 'Arial Black';
                font-size: 26px;
                font-weight: 900;
                line-height: 1.1;
                color: {COLOR_BLACK};
            }}
            QLabel#DescriptionText {{
                font-family: 'Arial';
                font-size: 13px;
                font-weight: bold;
                color: #555555;
            }}
            QFrame#StatusBox {{
                background-color: {BG_CREAM};
                border: 2px solid {COLOR_BLACK};
                border-radius: 0px;
            }}
            QLabel#StatusHeaderLabel {{
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                color: {COLOR_BLACK};
                letter-spacing: 0.5px;
            }}
            QLabel#StatusDot {{
                font-size: 14px;
                color: {ACCENT_GREEN};
            }}
            QLabel#StatusConsoleLine {{
                font-family: 'Courier New', monospace;
                font-size: 11px;
                font-weight: bold;
                color: #374151;
            }}
            QFrame#ReadyCard {{
                background-color: {ACCENT_PURPLE};
                border: 4px solid {COLOR_BLACK};
                border-radius: 0px;
            }}
            QLabel#CodeIcon {{
                font-size: 20px;
            }}
            QLabel#ReadyTitle {{
                font-family: 'Arial Black';
                font-size: 15px;
                font-weight: 900;
                color: {COLOR_WHITE};
                letter-spacing: 0.5px;
            }}
            QPushButton#LandingLoginBtn {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT_LIME}, stop:1 {ACCENT_YELLOW});
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                font-family: 'Arial Black';
                font-size: 15px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            QPushButton#LandingLoginBtn:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT_LIME}, stop:1 {ACCENT_PURPLE});
            }}
            QPushButton#LandingLoginBtn:pressed {{
                background: {ACCENT_PURPLE};
                color: {COLOR_WHITE};
            }}
            QLabel#SignupDescLabel {{
                font-family: 'Arial';
                font-size: 12px;
                font-weight: bold;
                color: {COLOR_BLACK};
            }}
            QPushButton#CreateBtn {{
                border: none;
                background: none;
                font-family: 'Arial Black';
                font-size: 12px;
                font-weight: 900;
                color: {ACCENT_PURPLE};
                text-decoration: underline;
                padding: 0px;
            }}
            QPushButton#CreateBtn:hover {{
                color: {COLOR_BLACK};
            }}
            QPushButton#DocsBtn, QPushButton#SupportBtn {{
                background-color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                font-family: 'Arial Black';
                font-size: 12px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            QPushButton#DocsBtn:hover, QPushButton#SupportBtn:hover {{
                background-color: {ACCENT_LIME};
            }}
            QPushButton#DocsBtn:pressed, QPushButton#SupportBtn:pressed {{
                background-color: {COLOR_BLACK};
                color: {COLOR_WHITE};
            }}
        """)
    def direct_to_readme(self):
        readme_url="https://github.com/benjaminms10/RB-mini/blob/main/README.md"
        webbrowser.open(readme_url)
