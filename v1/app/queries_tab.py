import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QDialog, QLineEdit, QPlainTextEdit,
    QApplication, QMessageBox
)
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtCore import Qt

from .styles import (
    apply_neo_shadow, BG_CREAM, COLOR_WHITE, COLOR_BLACK,
    ACCENT_PURPLE, ACCENT_YELLOW, ACCENT_LIME, ACCENT_RED, ACCENT_CYAN
)
from . import queries_manager

class QueryEditDialog(QDialog):
    """Neo-brutalist dialog to add or edit a query."""
    def __init__(self, parent=None, title="EDIT QUERY", name="", sql=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(450, 350)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        
        self.init_ui(name, sql)
        
    def init_ui(self, name, sql):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Dialog Header
        header_lbl = QLabel(self.windowTitle(), self)
        header_lbl.setFont(QFont("Arial Black", 14, QFont.Weight.Bold))
        header_lbl.setStyleSheet(f"color: {COLOR_BLACK};")
        layout.addWidget(header_lbl)
        
        # Name Input
        name_lbl = QLabel("QUERY NAME // LABEL", self)
        name_lbl.setFont(QFont("Arial Black", 9))
        name_lbl.setStyleSheet(f"color: {COLOR_BLACK};")
        layout.addWidget(name_lbl)
        
        self.name_input = QLineEdit(self)
        self.name_input.setText(name)
        self.name_input.setPlaceholderText("e.g., Get All Users")
        self.name_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                padding: 8px;
                font-family: 'Arial';
                font-size: 12px;
                font-weight: bold;
                color: {COLOR_BLACK};
            }}
        """)
        apply_neo_shadow(self.name_input, 3, 3)
        layout.addWidget(self.name_input)
        
        # SQL Input
        sql_lbl = QLabel("SQL STATEMENT", self)
        sql_lbl.setFont(QFont("Arial Black", 9))
        sql_lbl.setStyleSheet(f"color: {COLOR_BLACK};")
        layout.addWidget(sql_lbl)
        
        self.sql_input = QPlainTextEdit(self)
        self.sql_input.setPlainText(sql)
        self.sql_input.setPlaceholderText("SELECT * FROM table_name;")
        self.sql_input.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                font-weight: bold;
                color: {COLOR_BLACK};
            }}
        """)
        apply_neo_shadow(self.sql_input, 3, 3)
        layout.addWidget(self.sql_input)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.cancel_btn = QPushButton("CANCEL", self)
        self.cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                color: {COLOR_BLACK};
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {ACCENT_YELLOW};
            }}
        """)
        apply_neo_shadow(self.cancel_btn, 3, 3)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("SAVE QUERY", self)
        self.save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_LIME};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                color: {COLOR_BLACK};
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: #CBE600;
            }}
        """)
        apply_neo_shadow(self.save_btn, 3, 3)
        self.save_btn.clicked.connect(self.handle_save)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BG_CREAM};
                border: 4px solid {COLOR_BLACK};
            }}
        """)

    def handle_save(self):
        name = self.name_input.text().strip()
        sql = self.sql_input.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Query name cannot be empty.")
            return
        if not sql:
            QMessageBox.warning(self, "Validation Error", "SQL statement cannot be empty.")
            return
            
        self.accept()

    def get_data(self):
        return self.name_input.text().strip(), self.sql_input.toPlainText().strip()


class QueryCard(QFrame):
    """Neo-brutalist card widget representing a saved query."""
    def __init__(self, name, sql, run_callback, on_update_callback, is_beginner=False, parent=None):
        super().__init__(parent)
        self.query_name = name
        self.query_sql = sql
        self.run_callback = run_callback
        self.on_update_callback = on_update_callback
        self.is_beginner = is_beginner
        self.init_ui()

    def init_ui(self):
        self.setObjectName("QueryCard")
        self.setStyleSheet(f"""
            QFrame#QueryCard {{
                background-color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
            }}
        """)
        apply_neo_shadow(self, 4, 4)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Header (Title and Run Button)
        header_layout = QHBoxLayout()
        
        title_lbl = QLabel(self.query_name, self)
        title_lbl.setFont(QFont("Arial Black", 11, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color: {COLOR_BLACK};")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        
        # Run Button
        btn_label = "▶ LOAD TO TERMINAL" if self.is_beginner else "▶ RUN QUERY"
        run_btn = QPushButton(btn_label, self)
        run_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        run_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_PURPLE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                font-family: 'Arial Black';
                font-size: 10px;
                font-weight: 900;
                color: {COLOR_WHITE};
                padding: 5px 10px;
            }}
            QPushButton:hover {{
                background-color: #7C3AED;
            }}
        """)
        apply_neo_shadow(run_btn, 2, 2)
        if self.is_beginner:
            run_btn.clicked.connect(self.load_to_terminal)
        else:
            run_btn.clicked.connect(lambda: self.run_callback(self.query_sql))
        header_layout.addWidget(run_btn)
        
        layout.addLayout(header_layout)
        
        # SQL Code Area
        sql_box = QPlainTextEdit(self)
        sql_box.setPlainText(self.query_sql)
        sql_box.setReadOnly(True)
        sql_box.setMaximumHeight(80)
        sql_box.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: #F3F4F6;
                border: 2px solid {COLOR_BLACK};
                border-radius: 0px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                font-weight: bold;
                color: #374151;
                padding: 5px;
            }}
        """)
        layout.addWidget(sql_box)
        
        # Footer Action Buttons
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(8)
        
        # Copy
        copy_btn = QPushButton("📋 COPY", self)
        copy_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        copy_btn.setStyleSheet(self.get_action_btn_style(ACCENT_YELLOW))
        apply_neo_shadow(copy_btn, 2, 2)
        copy_btn.clicked.connect(self.copy_to_clipboard)
        footer_layout.addWidget(copy_btn)
        
        if not self.is_beginner:
            # Edit
            edit_btn = QPushButton("✏️ EDIT", self)
            edit_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            edit_btn.setStyleSheet(self.get_action_btn_style(ACCENT_CYAN))
            apply_neo_shadow(edit_btn, 2, 2)
            edit_btn.clicked.connect(self.edit_query)
            footer_layout.addWidget(edit_btn)
            
            footer_layout.addStretch()
            
            # Delete
            delete_btn = QPushButton("🗑️ DELETE", self)
            delete_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            delete_btn.setStyleSheet(self.get_action_btn_style(ACCENT_RED))
            apply_neo_shadow(delete_btn, 2, 2)
            delete_btn.clicked.connect(self.delete_query)
            footer_layout.addWidget(delete_btn)
        else:
            footer_layout.addStretch()
            
        layout.addLayout(footer_layout)

    def get_action_btn_style(self, bg_color):
        return f"""
            QPushButton {{
                background-color: {bg_color};
                border: 2px solid {COLOR_BLACK};
                border-radius: 0px;
                font-family: 'Arial Black';
                font-size: 9px;
                font-weight: 900;
                color: {COLOR_BLACK};
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                opacity: 0.9;
                background-color: {COLOR_BLACK};
                color: {COLOR_WHITE};
            }}
        """

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.query_sql)
        # Briefly change text to show success feedback
        sender = self.sender()
        if sender:
            original_text = sender.text()
            sender.setText("✅ COPIED!")
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1000, lambda: sender.setText(original_text))

    def load_to_terminal(self):
        # Copy to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(self.query_sql)
        
        # Briefly change the run button text to show success feedback
        sender = self.sender()
        if sender:
            original_text = sender.text()
            sender.setText("✅ LOADED & COPIED!")
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1000, lambda: sender.setText(original_text))

        # Load to terminal input without executing
        try:
            self.run_callback(self.query_sql, execute=False)
        except TypeError:
            self.run_callback(self.query_sql)

    def edit_query(self):
        dialog = QueryEditDialog(self, title="EDIT QUERY", name=self.query_name, sql=self.query_sql)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name, new_sql = dialog.get_data()
            if queries_manager.update_query(self.query_name, new_name, new_sql):
                self.on_update_callback()

    def delete_query(self):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the query '{self.query_name}'?"
        )
        if reply == QMessageBox.StandardButton.Yes:
            if queries_manager.delete_query(self.query_name):
                self.on_update_callback()


BEGINNER_TEMPLATES = [
    {
        "name": "SELECT // Fetch Data",
        "sql": "-- Fetch all columns and rows from a table\nSELECT * FROM table_name LIMIT 100;\n\n-- Fetch specific columns with a condition\nSELECT column1, column2 \nFROM table_name \nWHERE condition_column = 'value';"
    },
    {
        "name": "INSERT // Add New Rows",
        "sql": "-- Insert a new row specifying columns and values\nINSERT INTO table_name (column_name1, column_name2) \nVALUES ('string_value', 12345);"
    },
    {
        "name": "UPDATE // Modify Existing Data",
        "sql": "-- Update values of rows matching a condition\nUPDATE table_name \nSET column1 = 'new_value', column2 = 999 \nWHERE id_column = 1;"
    },
    {
        "name": "DELETE // Remove Rows",
        "sql": "-- Delete rows matching a condition\nDELETE FROM table_name \nWHERE id_column = 1;"
    },
    {
        "name": "CREATE TABLE // Create Structure",
        "sql": "-- Create a new table with column definitions\nCREATE TABLE students (\n    id INT AUTO_INCREMENT PRIMARY KEY,\n    name VARCHAR(100) NOT NULL,\n    email VARCHAR(100) UNIQUE,\n    age INT DEFAULT 18\n);"
    },
    {
        "name": "JOIN // Combine Tables",
        "sql": "-- Combine columns from two tables based on matching keys\nSELECT orders.id, customers.name \nFROM orders \nINNER JOIN customers ON orders.customer_id = customers.id;"
    },
    {
        "name": "GROUP BY // Aggregate Data",
        "sql": "-- Group rows and calculate aggregates (COUNT, SUM, AVG)\nSELECT country, COUNT(*), AVG(age) \nFROM users \nGROUP BY country;"
    }
]


class QueriesTab(QWidget):
    """Neo-brutalist tab to manage and run saved queries, and beginner guide."""
    def __init__(self, run_query_callback, parent=None):
        super().__init__(parent)
        self.run_query_callback = run_query_callback
        self.view_mode = "saved" # "saved" or "beginner"
        self.init_ui()
        self.refresh_queries()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(12)
        
        # 1. Header Panel
        self.header_panel = QFrame(self)
        self.header_panel.setObjectName("HeaderPanel")
        self.header_panel.setStyleSheet(f"""
            QFrame#HeaderPanel {{
                background-color: {ACCENT_LIME};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
            }}
        """)
        apply_neo_shadow(self.header_panel, 4, 4)
        
        header_layout = QHBoxLayout(self.header_panel)
        header_layout.setContentsMargins(15, 12, 15, 12)
        
        self.title_label = QLabel("🔑 SAVED SQL QUERIES", self.header_panel)
        self.title_label.setFont(QFont("Arial Black", 13, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"color: {COLOR_BLACK};")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        # Add Query Button
        self.add_btn = QPushButton("➕ ADD QUERY", self.header_panel)
        self.add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                padding: 6px 14px;
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            QPushButton:hover {{
                background-color: {ACCENT_YELLOW};
            }}
        """)
        apply_neo_shadow(self.add_btn, 3, 3)
        self.add_btn.clicked.connect(self.add_new_query)
        header_layout.addWidget(self.add_btn)
        
        self.main_layout.addWidget(self.header_panel)
        
        # 1.5. Sub-header Navigation (Saved vs Beginner)
        self.sub_nav = QFrame(self)
        sub_nav_layout = QHBoxLayout(self.sub_nav)
        sub_nav_layout.setContentsMargins(0, 0, 0, 0)
        sub_nav_layout.setSpacing(10)
        
        self.saved_tab_btn = QPushButton("📂 SAVED TEMPLATES", self.sub_nav)
        self.saved_tab_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.saved_tab_btn.clicked.connect(lambda: self.switch_view_mode("saved"))
        apply_neo_shadow(self.saved_tab_btn, 2, 2)
        
        self.beginner_tab_btn = QPushButton("📖 BEGINNER SQL GUIDE", self.sub_nav)
        self.beginner_tab_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.beginner_tab_btn.clicked.connect(lambda: self.switch_view_mode("beginner"))
        apply_neo_shadow(self.beginner_tab_btn, 2, 2)
        
        sub_nav_layout.addWidget(self.saved_tab_btn, 1)
        sub_nav_layout.addWidget(self.beginner_tab_btn, 1)
        
        self.main_layout.addWidget(self.sub_nav)
        self.update_nav_buttons()
        
        # 2. Scroll Area for Query Cards
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                border: 2px solid {COLOR_BLACK};
                background: {BG_CREAM};
                width: 16px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {ACCENT_PURPLE};
                border: 2px solid {COLOR_BLACK};
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: 2px solid {COLOR_BLACK};
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
        """)
        
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("ScrollContent")
        self.scroll_content.setStyleSheet(f"QWidget#ScrollContent {{ background-color: transparent; }}")
        
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 5, 0)
        self.scroll_layout.setSpacing(15)
        self.scroll_layout.addStretch()
        
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

    def switch_view_mode(self, mode):
        self.view_mode = mode
        self.update_nav_buttons()
        if mode == "saved":
            self.title_label.setText("🔑 SAVED SQL QUERIES")
            self.add_btn.show()
        else:
            self.title_label.setText("📖 BEGINNER SQL SYNTAX GUIDE")
            self.add_btn.hide()
        self.refresh_queries()

    def update_nav_buttons(self):
        # Styled to match active/inactive states in neo-brutalist palette
        active_style = f"""
            QPushButton {{
                background-color: {ACCENT_PURPLE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                padding: 10px;
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                color: {COLOR_WHITE};
            }}
        """
        inactive_style = f"""
            QPushButton {{
                background-color: {COLOR_WHITE};
                border: 3px solid {COLOR_BLACK};
                border-radius: 0px;
                padding: 10px;
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            QPushButton:hover {{
                background-color: {ACCENT_YELLOW};
            }}
        """
        if self.view_mode == "saved":
            self.saved_tab_btn.setStyleSheet(active_style)
            self.beginner_tab_btn.setStyleSheet(inactive_style)
        else:
            self.saved_tab_btn.setStyleSheet(inactive_style)
            self.beginner_tab_btn.setStyleSheet(active_style)

    def refresh_queries(self):
        # Clear existing items (except stretch)
        while self.scroll_layout.count() > 1:
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        if self.view_mode == "saved":
            queries = queries_manager.load_queries()
            for q in queries:
                card = QueryCard(
                    name=q["name"],
                    sql=q["sql"],
                    run_callback=self.run_query_callback,
                    on_update_callback=self.refresh_queries,
                    is_beginner=False,
                    parent=self
                )
                self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, card)
        else:
            for q in BEGINNER_TEMPLATES:
                card = QueryCard(
                    name=q["name"],
                    sql=q["sql"],
                    run_callback=self.run_query_callback,
                    on_update_callback=self.refresh_queries,
                    is_beginner=True,
                    parent=self
                )
                self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, card)

    def add_new_query(self):
        dialog = QueryEditDialog(self, title="ADD NEW QUERY")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, sql = dialog.get_data()
            if queries_manager.add_query(name, sql):
                self.refresh_queries()
