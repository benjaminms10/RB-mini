#----------------------------dashbord------------------------------------------------- 

import sys
import datetime
import mysql.connector
from mysql.connector import Error
import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame,
    QTreeWidget, QTreeWidgetItem, QPlainTextEdit, QStackedWidget, QSplitter, QDialog
)
from PyQt6.QtGui import QColor, QFont, QCursor
from PyQt6.QtCore import Qt, QEvent

from .styles import (
    apply_neo_shadow, BG_CREAM, COLOR_WHITE, COLOR_BLACK,
    ACCENT_PURPLE, ACCENT_YELLOW, ACCENT_LIME, ACCENT_CYAN,
    ACCENT_GREEN, ACCENT_RED, ACCENT_OLIVE, active_theme
)

# Tab components and managers
from .config_helper import load_connection_details
from .connection_settings_dialog import ConnectionSettingsDialog
from .table_viewer import TableViewer
from .queries_tab import QueriesTab
from .logs_tab import LogsTab, log_event
from . import user_manager


class DashboardPage(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.connection = None
        self.cursor = None
        self.logged_in_user = None
        self.init_ui()
        self.connect_to_mysql()

    def connect_to_mysql(self):
        """Connect to MySQL database using stored credentials"""
        config = load_connection_details()
        host = config.get('host', 'localhost')
        port = config.get('port', 3306)
        user = config.get('user', 'root')
        password = config.get('password', '')
        database = config.get('database', 'mysql')
        
        self.console_output.appendPlainText(f"[...] Attempting connection to {user}@{host}:{port}...")
        log_event(f"Attempting connection to {user}@{host}:{port}", "INFO")
        
        try:
            self.connection = mysql.connector.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                connect_timeout=3,
                auth_plugin='mysql_native_password'
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(buffered=True)
                self.console_output.appendPlainText(f"[✓] Connected to MySQL ({host}:{port})")
                self.console_output.appendPlainText(f"[✓] Server version: {self.connection.server_version}")
                self.console_output.appendPlainText("[✓] Interactive terminal ready. Type your SQL and press Enter.")
                self.console_output.appendPlainText("mysql> ")
                log_event(f"Successfully connected to MySQL ({host}:{port}). Server version: {self.connection.server_version}", "SYSTEM")
                
                # Update host label on sidebar dynamically
                if hasattr(self, 'host_lbl'):
                    self.host_lbl.setText(f"{host}:{port}")
                
                self.update_system_stats()
                self.refresh_tree()
            
        except Error as e:
            self.connection = None
            self.cursor = None
            self.console_output.appendPlainText(f"[✗] Connection failed: {e}")
            self.console_output.appendPlainText(f"[!] Click the ⚙️ SETTINGS button to configure your MySQL connection")
            self.console_output.appendPlainText("mysql> ")
            log_event(f"Connection failed to {host}:{port}: {e}", "ERROR")
            self.update_system_stats()

    def init_ui(self):
        # Overall main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===== SIDEBAR =====
        sidebar = QFrame(self)
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(15)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        self.admin_lbl = QLabel("RB Admin", sidebar)
        self.admin_lbl.setObjectName("SidebarAdminTitle")
        self.host_lbl = QLabel("Localhost:3306", sidebar)
        self.host_lbl.setObjectName("SidebarAdminSubtitle")
        title_layout.addWidget(self.admin_lbl)
        title_layout.addWidget(self.host_lbl)
        sidebar_layout.addLayout(title_layout)
        sidebar_layout.addSpacing(15)

        self.menu_buttons = []
        
        # ✅ Databases Button (Index 0)
        db_btn = QPushButton("🗄️  Databases", sidebar)
        db_btn.setObjectName("SidebarBtnSelected")
        db_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        apply_neo_shadow(db_btn, 3, 3)
        sidebar_layout.addWidget(db_btn)
        self.menu_buttons.append(db_btn)

        # ✅ Queries Button (Index 1)
        queries_btn = QPushButton("📋  Queries", sidebar)
        queries_btn.setObjectName("SidebarBtn")
        queries_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        apply_neo_shadow(queries_btn, 3, 3)
        sidebar_layout.addWidget(queries_btn)
        self.menu_buttons.append(queries_btn)

        # ✅ Users Button - Shows all users from JSON
        self.users_btn = QPushButton("👥  Users", sidebar)
        self.users_btn.setObjectName("SidebarBtn")
        self.users_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        apply_neo_shadow(self.users_btn, 3, 3)
        sidebar_layout.addWidget(self.users_btn)
        self.menu_buttons.append(self.users_btn)
        self.users_btn.clicked.connect(self.show_all_users)

        # ✅ Logs Button (Index 2)
        logs_btn = QPushButton("📜  Logs", sidebar)
        logs_btn.setObjectName("SidebarBtn")
        logs_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        apply_neo_shadow(logs_btn, 3, 3)
        sidebar_layout.addWidget(logs_btn)
        self.menu_buttons.append(logs_btn)

        # Connect sidebar clicks
        db_btn.clicked.connect(lambda: self.switch_tab(0))
        queries_btn.clicked.connect(lambda: self.switch_tab(1))
        logs_btn.clicked.connect(lambda: self.switch_tab(2))

        sidebar_layout.addStretch()
        exec_query_btn = QPushButton("🚪  LOGOUT", sidebar)
        exec_query_btn.setObjectName("ExecuteQueryBtn")
        exec_query_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        apply_neo_shadow(exec_query_btn, 4, 4)
        if self.controller:
            exec_query_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(exec_query_btn)

        main_layout.addWidget(sidebar)

        # ===== EXPLORER =====
        explorer = QFrame(self)
        explorer.setObjectName("Explorer")
        explorer.setFixedWidth(200)
        explorer_layout = QVBoxLayout(explorer)
        explorer_layout.setContentsMargins(15, 20, 15, 15)
        explorer_layout.setSpacing(12)

        exp_header_layout = QHBoxLayout()
        exp_title = QLabel("EXPLORER", explorer)
        exp_title.setObjectName("ExplorerHeaderTitle")
        refresh_btn = QPushButton("🔄", explorer)
        refresh_btn.setObjectName("ExplorerRefreshBtn")
        refresh_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        refresh_btn.setFixedSize(24, 24)
        refresh_btn.clicked.connect(self.refresh_tree)
        exp_header_layout.addWidget(exp_title)
        exp_header_layout.addStretch()
        exp_header_layout.addWidget(refresh_btn)
        explorer_layout.addLayout(exp_header_layout)

        self.tree_widget = QTreeWidget(explorer)
        self.tree_widget.setObjectName("ExplorerTree")
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setIndentation(15)
        
        # Connect double-click on explorer table node
        self.tree_widget.itemDoubleClicked.connect(self.on_tree_item_double_clicked)
        
        explorer_layout.addWidget(self.tree_widget)

        system_status = QFrame(explorer)
        system_status.setObjectName("SystemStatusPanel")
        system_status_layout = QVBoxLayout(system_status)
        system_status_layout.setContentsMargins(10, 12, 10, 12)
        system_status_layout.setSpacing(8)

        sys_active_badge = QFrame(system_status)
        sys_active_badge.setObjectName("SysActiveBadge")
        apply_neo_shadow(sys_active_badge, 2, 2)
        sys_badge_layout = QHBoxLayout(sys_active_badge)
        sys_badge_layout.setContentsMargins(8, 4, 8, 4)
        sys_badge_layout.setSpacing(5)
        sys_dot = QLabel("●", sys_active_badge)
        sys_dot.setStyleSheet("color: #DFFF00; font-size: 10px;")
        sys_lbl = QLabel("SYSTEM ACTIVE", sys_active_badge)
        sys_lbl.setStyleSheet("color: #FFFFFF; font-family: 'Arial Black'; font-size: 9px; font-weight: 900;")
        sys_badge_layout.addWidget(sys_dot)
        sys_badge_layout.addWidget(sys_lbl)
        system_status_layout.addWidget(sys_active_badge)

        self.cpu_lbl = QLabel("CPU Usage: --%", system_status)
        self.cpu_lbl.setObjectName("SysMetricsText")
        self.conn_lbl = QLabel("Active Conns: --", system_status)
        self.conn_lbl.setObjectName("SysMetricsText")
        system_status_layout.addWidget(self.cpu_lbl)
        system_status_layout.addWidget(self.conn_lbl)
        
        self.configure_btn = QPushButton("⚙️ CONFIGURE", system_status)
        self.configure_btn.setObjectName("ConfigureBtn")
        self.configure_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.configure_btn.clicked.connect(self.open_connection_settings)
        self.configure_btn.hide()
        system_status_layout.addWidget(self.configure_btn)
        
        explorer_layout.addWidget(system_status)
        main_layout.addWidget(explorer)

        # ===== RIGHT PANEL =====
        right_panel = QFrame(self)
        right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)

        # Header
        top_header_layout = QHBoxLayout()
        top_header_layout.setContentsMargins(0, 0, 0, 5)
        app_title = QLabel("RB MYSQL MINI WORKBENCH", right_panel)
        app_title.setObjectName("AppHeaderTitle")
        
        # Search input
        search_input = QLineEdit(right_panel)
        search_input.setPlaceholderText("🔎  Search databases...")
        search_input.setObjectName("SearchInput")
        search_input.setFixedWidth(280)
        apply_neo_shadow(search_input, 3, 3)
        search_input.textChanged.connect(self.filter_tree)

        top_header_layout.addWidget(app_title)
        top_header_layout.addStretch()
        top_header_layout.addWidget(search_input)
        top_header_layout.addSpacing(15)

        settings_btn = QPushButton("⚙️", right_panel)
        settings_btn.setObjectName("HeaderIconBtn")
        settings_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        settings_btn.clicked.connect(self.open_connection_settings)
        
        terminal_btn = QPushButton("💻", right_panel)
        terminal_btn.setObjectName("HeaderIconBtn")
        terminal_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        terminal_btn.clicked.connect(lambda: (self.switch_tab(0), self.terminal_input.setFocus()))
        
        self.profile_lbl = QLabel("U", right_panel)
        self.profile_lbl.setObjectName("ProfilePic")
        self.profile_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.profile_lbl.setFixedSize(30, 30)
        top_header_layout.addWidget(settings_btn)
        top_header_layout.addWidget(terminal_btn)
        top_header_layout.addWidget(self.profile_lbl)
        right_layout.addLayout(top_header_layout)

        # ===== STACKED WIDGET FOR TABS =====
        self.stacked_widget = QStackedWidget(right_panel)
        
        # --- TAB 0: DATABASES (Terminal & Table Viewer) ---
        db_tab_widget = QWidget()
        db_tab_layout = QVBoxLayout(db_tab_widget)
        db_tab_layout.setContentsMargins(0, 0, 0, 0)
        db_tab_layout.setSpacing(10)
        
        db_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Terminal Container
        terminal_container = QFrame(db_splitter)
        terminal_container.setObjectName("EditorContainer")
        apply_neo_shadow(terminal_container, 6, 6)
        
        terminal_layout = QVBoxLayout(terminal_container)
        terminal_layout.setContentsMargins(0, 0, 0, 0)
        terminal_layout.setSpacing(0)

        term_header = QFrame(terminal_container)
        term_header.setObjectName("ConsoleHeader")
        term_header.setFixedHeight(30)
        term_header_layout = QHBoxLayout(term_header)
        term_header_layout.setContentsMargins(15, 0, 15, 0)
        term_title = QLabel("INTERACTIVE MYSQL TERMINAL", term_header)
        term_title.setObjectName("ConsoleTitleText")
        term_header_layout.addWidget(term_title)
        term_header_layout.addStretch()
        terminal_layout.addWidget(term_header)

        # ✅ OUTPUT AREA - Increased size
        self.console_output = QPlainTextEdit(terminal_container)
        self.console_output.setObjectName("ConsoleOutputText")
        self.console_output.setReadOnly(True)
        self.console_output.setPlainText("[⏳] Connecting to MySQL...\n")
        self.console_output.setFixedHeight(400)  # Increased from 200
        terminal_layout.addWidget(self.console_output)

        self.terminal_input = QPlainTextEdit(terminal_container)
        self.terminal_input.setObjectName("TerminalInput")
        self.terminal_input.setPlaceholderText("Type SQL... Enter execute, Shift+Enter new line")
        self.terminal_input.setFixedHeight(80)
        self.terminal_input.installEventFilter(self)
        terminal_layout.addWidget(self.terminal_input)
        
        db_splitter.addWidget(terminal_container)
        
        # Table Viewer
        self.table_viewer = TableViewer(parent=self)
        self.table_viewer.hide()
        db_splitter.addWidget(self.table_viewer)
        
        db_splitter.setSizes([500, 150])  # More terminal space
        db_tab_layout.addWidget(db_splitter)
        
        self.stacked_widget.addWidget(db_tab_widget)  # Index 0
        
        # --- TAB 1: SAVED QUERIES ---
        self.queries_tab = QueriesTab(run_query_callback=self.run_query_from_tab, parent=self)
        self.stacked_widget.addWidget(self.queries_tab)  # Index 1

        # --- TAB 2: LOGS ---
        self.logs_tab = LogsTab(parent=self)
        self.stacked_widget.addWidget(self.logs_tab)  # Index 2
        
        right_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(right_panel)

        # ===== STYLES =====
        self.setStyleSheet(f"""
            QFrame#Sidebar {{
                background-color: {COLOR_WHITE};
                border-right: 3px solid {COLOR_BLACK};
            }}
            QLabel#SidebarAdminTitle {{
                font-family: 'Arial Black';
                font-size: 16px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            QLabel#SidebarAdminSubtitle {{
                font-family: 'Arial';
                font-size: 11px;
                font-weight: bold;
                color: {ACCENT_OLIVE};
            }}
            QPushButton#SidebarBtnSelected {{
                background-color: {ACCENT_LIME};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                font-family: 'Arial Black';
                font-size: 12px;
                font-weight: 900;
                color: {COLOR_BLACK};
                text-align: left;
                padding: 8px 10px;
            }}
            QPushButton#SidebarBtn {{
                background-color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                font-family: 'Arial Black';
                font-size: 12px;
                font-weight: 900;
                color: {COLOR_BLACK};
                text-align: left;
                padding: 8px 10px;
            }}
            QPushButton#SidebarBtn:hover {{
                background-color: {ACCENT_YELLOW};
            }}
            QPushButton#ExecuteQueryBtn {{
                background-color: {ACCENT_PURPLE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                color: {COLOR_WHITE};
                font-family: 'Arial Black';
                font-size: 12px;
                font-weight: 900;
                padding: 12px;
                text-align: center;
            }}
            QFrame#Explorer {{
                background-color: {COLOR_WHITE};
                border-right: 3px solid {COLOR_BLACK};
            }}
            QLabel#ExplorerHeaderTitle {{
                font-family: 'Arial Black';
                font-size: 12px;
                font-weight: 900;
                color: {COLOR_BLACK};
                letter-spacing: 0.5px;
            }}
            QTreeWidget#ExplorerTree {{
                background-color: {COLOR_WHITE};
                border: none;
                font-family: 'Arial';
                font-size: 12px;
                font-weight: bold;
                color: {COLOR_BLACK};
            }}
            QFrame#SystemStatusPanel {{
                background-color: {COLOR_WHITE};
                border: 2px solid {COLOR_BLACK};
                border-radius: 0px;
            }}
            QLabel#SysMetricsText {{
                font-family: 'Courier New', monospace;
                font-size: 10px;
                font-weight: bold;
                color: {COLOR_BLACK};
            }}
            QFrame#RightPanel {{
                background-color: {BG_CREAM};
            }}
            QLabel#AppHeaderTitle {{
                font-family: 'Arial Black';
                font-size: 18px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            QLineEdit#SearchInput {{
                background-color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                padding: 6px 12px;
                font-family: 'Arial';
                font-size: 12px;
                font-weight: bold;
                color: {COLOR_BLACK};
            }}
            QLabel#ProfilePic {{
                background-color: {ACCENT_PURPLE};
                border: 2px solid {COLOR_BLACK};
                border-radius: 15px;
                color: {COLOR_WHITE};
                font-family: 'Arial Black';
                font-size: 12px;
                font-weight: 900;
            }}
            QFrame#EditorContainer {{
                background-color: {"#FFFFFF" if active_theme == "lightmode" else "#111827"};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
            }}
            QFrame#ConsoleHeader {{
                background-color: {ACCENT_PURPLE};
                border-bottom: 3px solid {COLOR_BLACK};
            }}
            QLabel#ConsoleTitleText {{
                font-family: 'Arial Black';
                font-size: 10px;
                font-weight: 900;
                color: {COLOR_WHITE};
                letter-spacing: 0.5px;
            }}
            QPlainTextEdit#ConsoleOutputText {{
                background-color: {"#FFFFFF" if active_theme == "lightmode" else "#111827"};
                border: none;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                font-weight: bold;
                color: {COLOR_BLACK if active_theme == "lightmode" else "#10B981"};
            }}
            QPlainTextEdit#TerminalInput {{
                background-color: {BG_CREAM if active_theme == "lightmode" else "#1F2937"};
                border: none;
                border-top: 2px solid {COLOR_BLACK};
                color: {COLOR_BLACK if active_theme == "lightmode" else "#10B981"};
                font-family: 'Courier New', monospace;
                font-size: 12px;
                padding: 8px 12px;
            }}
            QPlainTextEdit#TerminalInput:focus {{
                background-color: {"#FFFFFF" if active_theme == "lightmode" else "#111827"};
                border-top: 2px solid {ACCENT_PURPLE};
            }}
            QPushButton#ConfigureBtn {{
                background-color: {ACCENT_PURPLE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                color: {COLOR_WHITE};
                font-family: 'Arial Black';
                font-size: 10px;
                font-weight: 900;
                padding: 6px;
            }}
            QPushButton#ConfigureBtn:hover {{
                background-color: #7C3AED;
            }}
        """)

    def execute_terminal_command(self):
        """Execute command typed in the terminal input (multi-line support)"""
        # Clear any unread results
        try:
            while self.cursor.nextset():
                self.cursor.fetchall()
            self.cursor.fetchall()
        except:
            pass

        # Get the full multi-line text
        command = self.terminal_input.toPlainText().strip()
        if not command:
            self.console_output.appendPlainText("mysql> ")
            self.terminal_input.clear()
            self.terminal_input.setFocus()
            return

        # Display the command in console
        self.console_output.appendPlainText(f"mysql> {command}")

        # Special commands
        if command.lower() in ["exit", "quit", r"\q"]:
            self.console_output.appendPlainText("Bye!")
            log_event("User exited terminal.", "INFO")
            if self.controller:
                self.controller.show_landing()
            return
        
        if command.lower() in ["clear", "cls", "clear;", "cls;"]:
            self.console_output.clear()
            self.console_output.appendPlainText("mysql> ")
            self.terminal_input.clear()
            self.terminal_input.setFocus()
            log_event("Terminal console output cleared.", "INFO")
            return
        
        if command.lower() in ["help", r"\h"]:
            self.console_output.appendPlainText(r"Commands: exit, quit, clear, help, \h, \q, cls or any SQL query")
            self.console_output.appendPlainText("  Use Enter to execute, Shift+Enter for new line")
            self.console_output.appendPlainText("mysql> ")
            self.terminal_input.clear()
            self.terminal_input.setFocus()
            return

        # Execute SQL
        if not self.connection or not self.connection.is_connected():
            self.console_output.appendPlainText("ERROR: Not connected to MySQL")
            self.console_output.appendPlainText("mysql> ")
            self.terminal_input.clear()
            self.terminal_input.setFocus()
            log_event("Failed to execute SQL: No active connection", "ERROR")
            return

        start_time = datetime.datetime.now()
        try:
            self.cursor.execute(command)
            end_time = datetime.datetime.now()
            execution_ms = int((end_time - start_time).total_seconds() * 1000)

            upper_cmd = command.strip().upper()
            if upper_cmd.startswith(("SELECT", "SHOW", "DESCRIBE", "DESC", "EXPLAIN")):
                rows = self.cursor.fetchall()
                col_names = [i[0] for i in self.cursor.description]
                
                col_widths = [len(name) for name in col_names]
                for row in rows:
                    for i, val in enumerate(row):
                        col_widths[i] = max(col_widths[i], len(str(val)))
                
                header = " | ".join(name.ljust(col_widths[i]) for i, name in enumerate(col_names))
                separator = "-" * len(header)
                
                self.console_output.appendPlainText(f"Query OK, {execution_ms}ms")
                self.console_output.appendPlainText(separator)
                self.console_output.appendPlainText(header)
                self.console_output.appendPlainText(separator)
                
                for row in rows:
                    row_str = " | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row))
                    self.console_output.appendPlainText(row_str)
                
                if len(rows) == 0:
                    self.console_output.appendPlainText("(0 rows returned)")
                else:
                    self.console_output.appendPlainText(separator)
                    self.console_output.appendPlainText(f"{len(rows)} row(s) returned")
                    
            else:
                self.connection.commit()
                row_count = self.cursor.rowcount
                self.console_output.appendPlainText(f"Query OK, {execution_ms}ms")
                self.console_output.appendPlainText(f"{row_count} row(s) affected")

            log_event(f"SQL Success ({execution_ms}ms): {command[:60]}...", "SQL")

            # Refresh the db tree if it modifies structural databases/tables
            if upper_cmd.startswith(("CREATE", "DROP", "ALTER", "USE", "RENAME")):
                self.refresh_tree()

            self.update_system_stats()

        except Error as e:
            end_time = datetime.datetime.now()
            execution_ms = int((end_time - start_time).total_seconds() * 1000)
            self.console_output.appendPlainText(f"ERROR: {e}")
            log_event(f"SQL Error ({execution_ms}ms): {e.msg} on query: {command[:60]}...", "ERROR")

        self.console_output.appendPlainText("mysql> ")
        self.terminal_input.clear()
        self.terminal_input.setFocus()

        # Auto-scroll
        scrollbar = self.console_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def switch_tab(self, index):
        """Switches stacked widget tab and updates button visuals."""
        self.stacked_widget.setCurrentIndex(index)
        
        # Update button styles
        for i, btn in enumerate(self.menu_buttons):
            if i == index:
                btn.setObjectName("SidebarBtnSelected")
            else:
                btn.setObjectName("SidebarBtn")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        # Refresh contents of dynamic tabs when switched to
        if index == 1:  # Saved Queries
            self.queries_tab.refresh_queries()
        elif index == 2:  # Logs
            if hasattr(self, 'logs_tab'):
                self.logs_tab.reload_logs()

    def open_connection_settings(self):
        """Displays connection configuration settings dialog."""
        dialog = ConnectionSettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.logout_requested:
                self.logout()
            else:
                log_event("Connection credentials updated. Reconnecting to MySQL...", "INFO")
                self.connect_to_mysql()

    def on_tree_item_double_clicked(self, item, column):
        """Visualizes database tables on tree double click."""
        if item.parent() is not None:
            db_name = item.parent().text(0)
            table_name = item.text(0)

            if not self.connection or not self.connection.is_connected():
                self.console_output.appendPlainText("ERROR: not connected to MYSQL")
                self.console_output.appendPlainText("mysql> ")
                return
            
            log_event(f"Visualizing table {db_name}.{table_name} in Table Viewer", "INFO")
            self.table_viewer.load_table(self.connection, table_name, db_name)
            self.table_viewer.show()
            self.switch_tab(0)

    def set_logged_in_user(self, username):
        """Sets the currently logged-in username and updates the sidebar."""
        self.logged_in_user = username
        
        # ✅ Update Users button text
        if hasattr(self, 'users_btn') and self.users_btn:
            self.users_btn.setText(f"👥  {username}")
        
        # ✅ Update admin label
        if hasattr(self, 'admin_lbl') and self.admin_lbl:
            self.admin_lbl.setText("RB Admin")
        
        # ✅ Update profile picture
        if hasattr(self, 'profile_lbl') and self.profile_lbl:
            initial = username[0].upper() if username else "U"
            self.profile_lbl.setText(initial)

    def logout(self):
        """Logs out the current user and returns to landing page."""
        if self.connection and self.connection.is_connected():
            try:
                self.connection.close()
            except:
                pass
        self.connection = None
        self.cursor = None
        log_event(f"User '{getattr(self, 'logged_in_user', 'unknown')}' logged out.", "INFO")
        if self.controller:
            self.controller.show_landing()

    def run_query_from_tab(self, sql_text, execute=True):
        """Runs query from saved queries tab directly into the terminal."""
        self.switch_tab(0)
        self.terminal_input.setPlainText(sql_text)
        if execute:
            self.execute_terminal_command()
        else:
            self.terminal_input.setFocus()

    def refresh_tree(self):
        """Refresh the database tree from MySQL"""
        self.tree_widget.clear()
        if not self.connection or not self.connection.is_connected():
            return
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            
            for db in databases:
                db_name = db[0]
                db_item = QTreeWidgetItem(self.tree_widget)
                db_item.setText(0, db_name)
                db_item.setForeground(0, QColor(ACCENT_PURPLE))
                db_item.setFont(0, QFont("Arial Black", 10, QFont.Weight.Bold))
                
                try:
                    cursor.execute(f"SHOW TABLES FROM `{db_name}`")
                    tables = cursor.fetchall()
                    for table in tables:
                        table_item = QTreeWidgetItem(db_item)
                        table_item.setText(0, table[0])
                except Error:
                    pass
                
                db_item.setExpanded(False)
            
            cursor.close()
        except Error:
            pass

    def update_system_stats(self):
        """Update system status indicators"""
        if self.connection and self.connection.is_connected():
            self.cpu_lbl.setText("CPU Usage: --%")
            self.conn_lbl.setText("Active Conns: 1")
            self.cpu_lbl.setStyleSheet("color: #10B981;")
            self.conn_lbl.setStyleSheet("color: #10B981;")
            self.configure_btn.hide()
        else:
            self.cpu_lbl.setText("CPU Usage: --%")
            self.conn_lbl.setText("Active Conns: 0")
            self.cpu_lbl.setStyleSheet("color: #EF4444;")
            self.conn_lbl.setStyleSheet("color: #EF4444;")
            self.configure_btn.show()

    def eventFilter(self, obj, event):
        """Handle key events for multi-line input"""
        if obj == self.terminal_input and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    return False  # Shift+Enter = new line
                else:
                    self.execute_terminal_command()  # Enter = execute
                    return True
        return super().eventFilter(obj, event)
    
    def filter_tree(self, search_text):
        """Filter the tree widget based on search text"""
        search_text = search_text.upper().strip()

        # If search is empty, show all items
        if not search_text:
            for i in range(self.tree_widget.topLevelItemCount()):
                db_item = self.tree_widget.topLevelItem(i)
                db_item.setHidden(False)
                for j in range(db_item.childCount()):
                    db_item.child(j).setHidden(False)
            return

        # Filter items based on search text
        for i in range(self.tree_widget.topLevelItemCount()):
            db_item = self.tree_widget.topLevelItem(i)
            db_name = db_item.text(0).upper()
            db_matches = search_text in db_name
            has_matching_child = False

            for j in range(db_item.childCount()):
                table_item = db_item.child(j)
                table_name = table_item.text(0).upper()

                if search_text in table_name:
                    has_matching_child = True
                    table_item.setHidden(False)
                else:
                    table_item.setHidden(True)

            if db_matches or has_matching_child:
                db_item.setHidden(False)
                if has_matching_child:
                    db_item.setExpanded(True)
            else:
                db_item.setHidden(True)

    def show_all_users(self):
        """Display all users from the JSON file in the console"""
        self.console_output.clear()
        self.console_output.appendPlainText("=" * 60)
        self.console_output.appendPlainText("👥 ALL REGISTERED USERS")
        self.console_output.appendPlainText("=" * 60)
        
        # ✅ Use user_manager to load users
        users = user_manager.load_users()
        
        if users:
            self.console_output.appendPlainText(f"\n📊 Total Users: {len(users)}")
            self.console_output.appendPlainText("")
            self.console_output.appendPlainText("-" * 60)
            
            for i, user in enumerate(users, 1):
                self.console_output.appendPlainText(f"  [{i}] 👤 Username:  {user.get('username', 'N/A')}")
                self.console_output.appendPlainText(f"      📛 Full Name: {user.get('fullname', 'N/A')}")
                self.console_output.appendPlainText(f"      📧 Email:     {user.get('email', 'N/A')}")
                self.console_output.appendPlainText(f"      🔒 Password:  ********")
                
                if user.get('username') == self.logged_in_user:
                    self.console_output.appendPlainText(f"      ⭐ LOGGED IN")
                
                self.console_output.appendPlainText("-" * 60)
            
            self.console_output.appendPlainText(f"\n⭐ Logged in as: {self.logged_in_user}")
        else:
            self.console_output.appendPlainText("❌ No users found in JSON database")
        
        self.console_output.appendPlainText("")
        self.console_output.appendPlainText("=" * 60)
        self.console_output.appendPlainText("mysql> ")