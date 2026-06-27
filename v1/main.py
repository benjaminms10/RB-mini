import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from app.landing_page import LandingPage
from app.login_page import LoginPage
from app.signup_page import SignUpPage
from app.dashboard_page import DashboardPage

class WorkbenchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RB MySQL Mini Workbench Suite")
        self.setMinimumSize(1000, 700)
        self.init_ui()

    def init_ui(self):
        # Initialize the stack container
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        # Initialize screens with self as controller
        self.landing_screen = LandingPage(self, self)
        self.login_screen = LoginPage(self, self)
        self.signup_screen = SignUpPage(self, self)
        self.dashboard_screen = DashboardPage(self, self)

        # Add screens to stacked widget
        self.stack.addWidget(self.landing_screen)       # Index 0
        self.stack.addWidget(self.login_screen)         # Index 1
        self.stack.addWidget(self.signup_screen)        # Index 2
        self.stack.addWidget(self.dashboard_screen)     # Index 3

        # Start with the Landing Page
        self.show_landing()

    def show_landing(self):
        self.stack.setCurrentWidget(self.landing_screen)
        self.setWindowTitle("WELCOME // RB WORKBENCH")

    def show_login(self):
        self.stack.setCurrentWidget(self.login_screen)
        self.setWindowTitle("SECURE ACCESS // LOGIN")

    def show_signup(self):
        self.stack.setCurrentWidget(self.signup_screen)
        self.setWindowTitle("REGISTER SYSTEM USER // SIGN UP")

    def show_dashboard(self, username="admin"):
        self.dashboard_screen.set_logged_in_user(username)
        self.stack.setCurrentWidget(self.dashboard_screen)
        self.setWindowTitle(f"RB MYSQL WORKBENCH // USER: {username.upper()}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WorkbenchApp()
    window.show()
    sys.exit(app.exec())