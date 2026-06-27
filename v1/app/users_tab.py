import mysql.connector
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame,
    QTreeWidget, QTreeWidgetItem, QComboBox, QMessageBox, QListWidget, QSplitter
)
from PyQt6.QtGui import QColor, QFont, QCursor
from PyQt6.QtCore import Qt

from .styles import apply_neo_shadow, BG_CREAM, COLOR_WHITE, COLOR_BLACK, ACCENT_PURPLE, ACCENT_YELLOW, ACCENT_LIME, ACCENT_CYAN, ACCENT_GREEN, ACCENT_RED

class UsersTab(QWidget):
    def __init__(self, parent=None, connection=None):
        super().__init__(parent)
        self.connection = connection
        self.selected_user = None
        self.selected_host = None
        
        self.init_ui()
        if self.connection:
            self.refresh_users()
        else:
            self.show_not_connected()

    def set_connection(self, connection):
        """Sets or updates the active database connection."""
        self.connection = connection
        self.selected_user = None
        self.selected_host = None
        self.clear_details()
        if self.connection and self.connection.is_connected():
            self.show_connected()
            self.refresh_users()
        else:
            self.show_not_connected()

    def init_ui(self):
        # Main layout of the tab
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        # --- LEFT PANEL: USER LIST ---
        left_panel = QFrame(self)
        left_panel.setObjectName("UserListPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(10)

        left_title = QLabel("👤 SYSTEM USERS", left_panel)
        left_title.setObjectName("SectionTitle")
        left_layout.addWidget(left_title)

        # Users list tree
        self.users_tree = QTreeWidget(left_panel)
        self.users_tree.setObjectName("UsersTree")
        self.users_tree.setHeaderLabels(["User", "Host"])
        self.users_tree.setHeaderHidden(False)
        self.users_tree.setIndentation(0)
        self.users_tree.itemClicked.connect(self.on_user_selected)
        left_layout.addWidget(self.users_tree)

        # Refresh button
        self.refresh_btn = QPushButton("🔄 REFRESH LIST", left_panel)
        self.refresh_btn.setObjectName("RefreshBtn")
        self.refresh_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.refresh_btn.clicked.connect(self.refresh_users)
        apply_neo_shadow(self.refresh_btn, 3, 3)
        left_layout.addWidget(self.refresh_btn)

        # --- RIGHT PANEL: DETAILS & ACTIONS ---
        right_panel = QFrame(self)
        right_panel.setObjectName("UserDetailPanel")
        self.right_layout = QVBoxLayout(right_panel)
        self.right_layout.setContentsMargins(15, 15, 15, 15)
        self.right_layout.setSpacing(15)

        # User Badge Header
        self.user_badge = QFrame(right_panel)
        self.user_badge.setObjectName("UserBadge")
        self.user_badge.setFixedHeight(50)
        badge_layout = QHBoxLayout(self.user_badge)
        badge_layout.setContentsMargins(15, 5, 15, 5)
        self.badge_lbl = QLabel("NO USER SELECTED", self.user_badge)
        self.badge_lbl.setObjectName("BadgeText")
        badge_layout.addWidget(self.badge_lbl)
        self.right_layout.addWidget(self.user_badge)

        # Split details into active user management & create user section
        self.detail_area = QFrame(right_panel)
        self.detail_area.setObjectName("DetailArea")
        detail_layout = QVBoxLayout(self.detail_area)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        detail_layout.setSpacing(12)

        # Grants Section
        grants_lbl = QLabel("CURRENT GRANTS / PRIVILEGES", self.detail_area)
        grants_lbl.setObjectName("SubsectionTitle")
        detail_layout.addWidget(grants_lbl)

        self.grants_list = QListWidget(self.detail_area)
        self.grants_list.setObjectName("GrantsList")
        detail_layout.addWidget(self.grants_list)

        # Privilege controls row
        priv_controls_layout = QHBoxLayout()
        priv_controls_layout.setSpacing(10)

        # DB Scope input
        scope_v = QVBoxLayout()
        scope_v.setSpacing(3)
        scope_lbl = QLabel("DB SCOPE", self.detail_area)
        scope_lbl.setObjectName("FieldLabel")
        self.scope_input = QLineEdit(self.detail_area)
        self.scope_input.setObjectName("FormInput")
        self.scope_input.setPlaceholderText("*.*")
        self.scope_input.setText("*.*")
        scope_v.addWidget(scope_lbl)
        scope_v.addWidget(self.scope_input)
        priv_controls_layout.addLayout(scope_v, 3)

        # Privilege selector dropdown
        priv_v = QVBoxLayout()
        priv_v.setSpacing(3)
        priv_lbl = QLabel("PRIVILEGE", self.detail_area)
        priv_lbl.setObjectName("FieldLabel")
        self.priv_combo = QComboBox(self.detail_area)
        self.priv_combo.setObjectName("FormCombo")
        self.priv_combo.addItems([
            "ALL PRIVILEGES", "SELECT", "INSERT", "UPDATE", "DELETE", 
            "CREATE", "DROP", "ALTER", "INDEX", "CREATE USER"
        ])
        priv_v.addWidget(priv_lbl)
        priv_v.addWidget(self.priv_combo)
        priv_controls_layout.addLayout(priv_v, 4)

        detail_layout.addLayout(priv_controls_layout)

        # Grant / Revoke buttons
        grant_revoke_layout = QHBoxLayout()
        grant_revoke_layout.setSpacing(12)

        self.grant_btn = QPushButton("GRANT PRIVILEGE 🟢", self.detail_area)
        self.grant_btn.setObjectName("GrantBtn")
        self.grant_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.grant_btn.clicked.connect(self.grant_privilege)
        apply_neo_shadow(self.grant_btn, 3, 3)

        self.revoke_btn = QPushButton("REVOKE PRIVILEGE 🔴", self.detail_area)
        self.revoke_btn.setObjectName("RevokeBtn")
        self.revoke_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.revoke_btn.clicked.connect(self.revoke_privilege)
        apply_neo_shadow(self.revoke_btn, 3, 3)

        grant_revoke_layout.addWidget(self.grant_btn)
        grant_revoke_layout.addWidget(self.revoke_btn)
        detail_layout.addLayout(grant_revoke_layout)

        # Delete User Button
        self.delete_btn = QPushButton("🗑️ DROP USER", self.detail_area)
        self.delete_btn.setObjectName("DeleteBtn")
        self.delete_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.delete_btn.clicked.connect(self.drop_user)
        apply_neo_shadow(self.delete_btn, 3, 3)
        detail_layout.addWidget(self.delete_btn)

        self.right_layout.addWidget(self.detail_area)

        # --- CREATE USER BOX (INLINE FRAME) ---
        self.create_box = QFrame(right_panel)
        self.create_box.setObjectName("CreateBox")
        create_layout = QVBoxLayout(self.create_box)
        create_layout.setContentsMargins(12, 12, 12, 12)
        create_layout.setSpacing(8)

        create_title = QLabel("➕ CREATE NEW USER", self.create_box)
        create_title.setObjectName("SubsectionTitle")
        create_layout.addWidget(create_title)

        inputs_layout = QHBoxLayout()
        inputs_layout.setSpacing(8)

        # New user name
        new_user_v = QVBoxLayout()
        new_user_v.setSpacing(2)
        new_user_lbl = QLabel("USERNAME", self.create_box)
        new_user_lbl.setObjectName("FieldLabel")
        self.new_user_input = QLineEdit(self.create_box)
        self.new_user_input.setObjectName("FormInput")
        self.new_user_input.setPlaceholderText("new_mysql_user")
        new_user_v.addWidget(new_user_lbl)
        new_user_v.addWidget(self.new_user_input)
        inputs_layout.addLayout(new_user_v, 4)

        # New user host
        new_host_v = QVBoxLayout()
        new_host_v.setSpacing(2)
        new_host_lbl = QLabel("HOST", self.create_box)
        new_host_lbl.setObjectName("FieldLabel")
        self.new_host_input = QLineEdit(self.create_box)
        self.new_host_input.setObjectName("FormInput")
        self.new_host_input.setPlaceholderText("%")
        self.new_host_input.setText("localhost")
        new_host_v.addWidget(new_host_lbl)
        new_host_v.addWidget(self.new_host_input)
        inputs_layout.addLayout(new_host_v, 3)

        # New user pass
        new_pass_v = QVBoxLayout()
        new_pass_v.setSpacing(2)
        new_pass_lbl = QLabel("PASSWORD", self.create_box)
        new_pass_lbl.setObjectName("FieldLabel")
        self.new_pass_input = QLineEdit(self.create_box)
        self.new_pass_input.setObjectName("FormInput")
        self.new_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pass_input.setPlaceholderText("password")
        new_pass_v.addWidget(new_pass_lbl)
        new_pass_v.addWidget(self.new_pass_input)
        inputs_layout.addLayout(new_pass_v, 3)

        create_layout.addLayout(inputs_layout)

        # Create Button
        self.create_btn = QPushButton("CREATE USER →", self.create_box)
        self.create_btn.setObjectName("CreateBtn")
        self.create_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.create_btn.clicked.connect(self.create_user)
        apply_neo_shadow(self.create_btn, 3, 3)
        create_layout.addWidget(self.create_btn)

        self.right_layout.addWidget(self.create_box)

        # Split panels in layouts
        self.main_layout.addWidget(left_panel, 3)
        self.main_layout.addWidget(right_panel, 5)

        # Apply Neo-Brutalist stylesheet
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_CREAM};
            }}
            QFrame#UserListPanel {{
                background-color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
            }}
            QFrame#UserDetailPanel {{
                background-color: {BG_CREAM};
            }}
            QLabel#SectionTitle {{
                font-family: 'Arial Black';
                font-size: 13px;
                font-weight: 900;
                color: {COLOR_BLACK};
                letter-spacing: 0.5px;
            }}
            QLabel#SubsectionTitle {{
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                color: {COLOR_BLACK};
                letter-spacing: 0.3px;
            }}
            QTreeWidget#UsersTree {{
                background-color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
                font-family: 'Arial';
                font-size: 11px;
                font-weight: bold;
                color: {COLOR_BLACK};
            }}
            QTreeWidget#UsersTree::item {{
                padding: 6px;
                border-bottom: 1px solid #E5E7EB;
            }}
            QTreeWidget#UsersTree::item:selected {{
                background-color: {ACCENT_PURPLE};
                color: {COLOR_WHITE};
            }}
            QHeaderView::section {{
                background-color: {ACCENT_YELLOW};
                color: {COLOR_BLACK};
                font-family: 'Arial Black';
                font-size: 9px;
                font-weight: 900;
                border: 1px solid {COLOR_BLACK};
                padding: 4px;
            }}
            QPushButton#RefreshBtn {{
                background-color: {ACCENT_CYAN};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                color: {COLOR_BLACK};
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                padding: 8px;
            }}
            QPushButton#RefreshBtn:hover {{
                background-color: #06B6D4;
            }}
            QFrame#UserBadge {{
                background-color: {ACCENT_LIME};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
            }}
            QLabel#BadgeText {{
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            QListWidget#GrantsList {{
                background-color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
                font-family: 'Courier New';
                font-size: 10px;
                font-weight: bold;
                color: {COLOR_BLACK};
                padding: 5px;
            }}
            QLabel#FieldLabel {{
                font-family: 'Arial Black';
                font-size: 9px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            QLineEdit#FormInput {{
                background-color: {COLOR_WHITE};
                border: 2px solid {COLOR_BLACK};
                border-radius: 0px;
                padding: 6px;
                font-family: 'Arial';
                font-size: 11px;
                font-weight: bold;
                color: {COLOR_BLACK};
            }}
            QLineEdit#FormInput:focus {{
                background-color: {ACCENT_LIME};
            }}
            QComboBox#FormCombo {{
                background-color: {COLOR_WHITE};
                border: 2px solid {COLOR_BLACK};
                border-radius: 0px;
                padding: 5px;
                font-family: 'Arial';
                font-size: 11px;
                font-weight: bold;
                color: {COLOR_BLACK};
            }}
            QComboBox#FormCombo QAbstractItemView {{
                background-color: {COLOR_WHITE};
                color: {COLOR_BLACK};
                selection-background-color: {ACCENT_PURPLE};
                selection-color: {COLOR_WHITE};
                border: 2px solid {COLOR_BLACK};
                outline: none;
            }}
            QPushButton#GrantBtn {{
                background-color: {ACCENT_GREEN};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                color: {COLOR_BLACK};
                font-family: 'Arial Black';
                font-size: 10px;
                font-weight: 900;
                padding: 8px;
            }}
            QPushButton#GrantBtn:hover {{
                background-color: #6EE7B7;
            }}
            QPushButton#RevokeBtn {{
                background-color: {ACCENT_RED};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                color: {COLOR_BLACK};
                font-family: 'Arial Black';
                font-size: 10px;
                font-weight: 900;
                padding: 8px;
            }}
            QPushButton#RevokeBtn:hover {{
                background-color: #F87171;
            }}
            QPushButton#DeleteBtn {{
                background-color: #EF4444;
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                color: {COLOR_WHITE};
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                padding: 8px;
            }}
            QPushButton#DeleteBtn:hover {{
                background-color: #DC2626;
            }}
            QFrame#CreateBox {{
                background-color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
            }}
            QPushButton#CreateBtn {{
                background-color: {ACCENT_PURPLE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                color: {COLOR_WHITE};
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                padding: 8px;
            }}
            QPushButton#CreateBtn:hover {{
                background-color: #7C3AED;
            }}
        """)

    def show_not_connected(self):
        self.users_tree.clear()
        self.clear_details()
        self.badge_lbl.setText("⚠️ DATABASE NOT CONNECTED")
        self.user_badge.setStyleSheet(f"background-color: {ACCENT_RED}; border: 3px solid {COLOR_BLACK};")
        self.detail_area.setEnabled(False)
        self.create_box.setEnabled(False)

    def show_connected(self):
        self.user_badge.setStyleSheet(f"background-color: {ACCENT_LIME}; border: 3px solid {COLOR_BLACK};")
        self.detail_area.setEnabled(True)
        self.create_box.setEnabled(True)
        if not self.selected_user:
            self.badge_lbl.setText("SELECT A USER FROM THE LIST")

    def show_error(self, message):
        QMessageBox.critical(self, "Database Error", message)

    def clear_details(self):
        self.grants_list.clear()
        self.badge_lbl.setText("NO USER SELECTED")
        self.selected_user = None
        self.selected_host = None

    def refresh_users(self):
        if not self.connection or not self.connection.is_connected():
            self.show_not_connected()
            return

        self.show_connected()
        self.users_tree.clear()
        self.clear_details()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT User, Host FROM mysql.user ORDER BY User")
            users = cursor.fetchall()
            for user, host in users:
                item = QTreeWidgetItem(self.users_tree)
                item.setText(0, user)
                item.setText(1, host)
            cursor.close()
        except mysql.connector.Error as e:
            # Check if access denied or table mysql.user doesn't exist/can't select
            self.show_error(f"Failed to fetch users:\n{e.msg}\n\nMake sure the connected session has SELECT privileges on 'mysql.user'.")

    def on_user_selected(self, item, column):
        self.selected_user = item.text(0)
        self.selected_host = item.text(1)
        self.badge_lbl.setText(f"USER: {self.selected_user} @ {self.selected_host}")
        self.refresh_grants()

    def refresh_grants(self):
        self.grants_list.clear()
        if not self.connection or not self.connection.is_connected():
            self.show_not_connected()
            return
        if self.selected_user is None:
            return

        try:
            cursor = self.connection.cursor()
            # SHOW GRANTS FOR 'user'@'host'
            query = f"SHOW GRANTS FOR '{self.selected_user}'@'{self.selected_host}'"
            cursor.execute(query)
            grants = cursor.fetchall()
            for grant in grants:
                # grant is a tuple, e.g. ("GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost'",)
                self.grants_list.addItem(grant[0])
            cursor.close()
        except mysql.connector.Error as e:
            self.grants_list.addItem(f"ERROR FETCHING GRANTS: {e.msg}")

    def create_user(self):
        if not self.connection or not self.connection.is_connected():
            self.show_not_connected()
            return

        username = self.new_user_input.text().strip()
        host = self.new_host_input.text().strip()
        password = self.new_pass_input.text()

        if not username:
            QMessageBox.warning(self, "Validation Error", "Username cannot be empty.")
            return
        if not host:
            host = "%"

        try:
            cursor = self.connection.cursor()
            # CREATE USER 'username'@'host' IDENTIFIED BY 'password'
            # Note: We must construct query safely. Since we cannot use parameters for USER syntax,
            # we sanitize inputs by stripping and quoting safely.
            sanitized_username = username.replace("\\", "\\\\").replace("'", "\\'")
            sanitized_host = host.replace("\\", "\\\\").replace("'", "\\'")
            sanitized_password = password.replace("\\", "\\\\").replace("'", "\\'")

            query = f"CREATE USER '{sanitized_username}'@'{sanitized_host}' IDENTIFIED BY '{sanitized_password}'"
            cursor.execute(query)
            cursor.execute("FLUSH PRIVILEGES")
            cursor.close()
            self.connection.commit()

            # Clean inputs
            self.new_user_input.clear()
            self.new_pass_input.clear()
            self.new_host_input.setText("localhost")

            QMessageBox.information(self, "Success", f"User '{username}'@'{host}' created successfully!")
            self.refresh_users()
        except mysql.connector.Error as e:
            if e.errno == 1396:
                self.show_error(f"User '{username}'@'{host}' already exists.")
            else:
                self.show_error(f"Failed to create user:\n{e.msg}")

    def drop_user(self):
        if not self.connection or not self.connection.is_connected():
            self.show_not_connected()
            return
        if not self.selected_user:
            return

        user_str = f"'{self.selected_user}'@'{self.selected_host}'"
        confirm = QMessageBox.question(
            self, 
            "Confirm Drop User", 
            f"Are you sure you want to drop/delete the user {user_str}?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.connection.cursor()
                query = f"DROP USER {user_str}"
                cursor.execute(query)
                cursor.execute("FLUSH PRIVILEGES")
                cursor.close()
                self.connection.commit()

                QMessageBox.information(self, "Success", f"User {user_str} dropped successfully!")
                self.refresh_users()
            except mysql.connector.Error as e:
                self.show_error(f"Failed to drop user:\n{e.msg}")

    def grant_privilege(self):
        if not self.connection or not self.connection.is_connected():
            self.show_not_connected()
            return
        if not self.selected_user:
            return

        priv = self.priv_combo.currentText()
        scope = self.scope_input.text().strip()
        if not scope:
            scope = "*.*"

        user_str = f"'{self.selected_user}'@'{self.selected_host}'"
        
        try:
            cursor = self.connection.cursor()
            # GRANT SELECT ON *.* TO 'user'@'host'
            query = f"GRANT {priv} ON {scope} TO {user_str}"
            cursor.execute(query)
            cursor.execute("FLUSH PRIVILEGES")
            cursor.close()
            self.connection.commit()

            QMessageBox.information(self, "Success", f"Successfully granted {priv} on {scope} to {user_str}!")
            self.refresh_grants()
        except mysql.connector.Error as e:
            self.show_error(f"Failed to grant privilege:\n{e.msg}")

    def revoke_privilege(self):
        if not self.connection or not self.connection.is_connected():
            self.show_not_connected()
            return
        if not self.selected_user:
            return

        priv = self.priv_combo.currentText()
        scope = self.scope_input.text().strip()
        if not scope:
            scope = "*.*"

        user_str = f"'{self.selected_user}'@'{self.selected_host}'"

        try:
            cursor = self.connection.cursor()
            # REVOKE SELECT ON *.* FROM 'user'@'host'
            query = f"REVOKE {priv} ON {scope} FROM {user_str}"
            cursor.execute(query)
            cursor.execute("FLUSH PRIVILEGES")
            cursor.close()
            self.connection.commit()

            QMessageBox.information(self, "Success", f"Successfully revoked {priv} on {scope} from {user_str}!")
            self.refresh_grants()
        except mysql.connector.Error as e:
            self.show_error(f"Failed to revoke privilege:\n{e.msg}")
