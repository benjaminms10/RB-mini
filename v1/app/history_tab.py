import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QAbstractItemView, QMessageBox
)
from PyQt6.QtGui import QColor, QFont, QCursor
from PyQt6.QtCore import Qt

from .styles import (
    apply_neo_shadow, BG_CREAM, COLOR_WHITE, COLOR_BLACK,
    ACCENT_PURPLE, ACCENT_YELLOW, ACCENT_LIME, ACCENT_RED
)
from . import history_manager

class HistoryTab(QWidget):
    """Neo-brutalist tab to view query execution history and re-run queries."""
    def __init__(self, run_query_callback, parent=None):
        super().__init__(parent)
        self.run_query_callback = run_query_callback
        self.init_ui()
        self.refresh_history()

    def init_ui(self):
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(12)
        
        # 1. Header Panel
        self.header_panel = QFrame(self)
        self.header_panel.setObjectName("HeaderPanel")
        self.header_panel.setStyleSheet(f"""
            QFrame#HeaderPanel {{
                background-color: {ACCENT_LIME};
                border: 3px solid #000000;
                border-radius: 0px;
            }}
        """)
        apply_neo_shadow(self.header_panel, 4, 4)
        
        header_layout = QHBoxLayout(self.header_panel)
        header_layout.setContentsMargins(15, 12, 15, 12)
        
        title_label = QLabel("⏳ QUERY EXECUTION HISTORY", self.header_panel)
        title_label.setFont(QFont("Arial Black", 13, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {COLOR_BLACK};")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Refresh Button
        refresh_btn = QPushButton("🔄 REFRESH", self.header_panel)
        refresh_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_WHITE};
                border: 3px solid #000000;
                border-radius: 0px;
                padding: 6px 12px;
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            QPushButton:hover {{
                background-color: {ACCENT_YELLOW};
            }}
        """)
        apply_neo_shadow(refresh_btn, 3, 3)
        refresh_btn.clicked.connect(self.refresh_history)
        header_layout.addWidget(refresh_btn)
        
        self.main_layout.addWidget(self.header_panel)
        
        # 2. History Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["TIMESTAMP", "SQL STATEMENT", "DURATION (ms)", "STATUS"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setShowGrid(True)
        self.table.setGridStyle(Qt.PenStyle.SolidLine)
        
        # Table Double Click to Run
        self.table.doubleClicked.connect(self.handle_row_double_clicked)
        
        # Configure headers behavior
        self.table.horizontalHeader().setMinimumSectionSize(120)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.main_layout.addWidget(self.table)
        
        # 3. Action Buttons Panel (Footer)
        self.footer_panel = QFrame(self)
        footer_layout = QHBoxLayout(self.footer_panel)
        footer_layout.setContentsMargins(0, 5, 0, 5)
        footer_layout.setSpacing(15)
        
        # Run Again Button
        self.run_again_btn = QPushButton("▶ RUN AGAIN", self.footer_panel)
        self.run_again_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.run_again_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_PURPLE};
                border: 3px solid #000000;
                border-radius: 0px;
                padding: 10px 20px;
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                color: {COLOR_WHITE};
            }}
            QPushButton:hover {{
                background-color: #7C3AED;
            }}
        """)
        apply_neo_shadow(self.run_again_btn, 4, 4)
        self.run_again_btn.clicked.connect(self.run_selected_query)
        footer_layout.addWidget(self.run_again_btn)
        
        footer_layout.addStretch()
        
        # Clear History Button
        self.clear_btn = QPushButton("🗑️ CLEAR HISTORY", self.footer_panel)
        self.clear_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_RED};
                border: 3px solid #000000;
                border-radius: 0px;
                padding: 10px 20px;
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            QPushButton:hover {{
                background-color: #EF4444;
                color: {COLOR_WHITE};
            }}
        """)
        apply_neo_shadow(self.clear_btn, 4, 4)
        self.clear_btn.clicked.connect(self.clear_history)
        footer_layout.addWidget(self.clear_btn)
        
        self.main_layout.addWidget(self.footer_panel)
        
        # Apply Table styling matching table_viewer.py
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
            }}
            
            /* Table Styling */
            QTableWidget {{
                background-color: #FFFFFF;
                gridline-color: #000000;
                border: 3px solid #000000;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                font-weight: bold;
                color: {COLOR_BLACK};
            }}
            
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #000000;
                border-right: 1px solid #000000;
            }}
            
            QTableWidget::item:selected {{
                background-color: {ACCENT_PURPLE};
                color: {COLOR_WHITE};
            }}
            
            /* Table Headers Styling */
            QHeaderView::section {{
                background-color: {ACCENT_YELLOW};
                color: {COLOR_BLACK};
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                border: 2px solid #000000;
                padding: 8px;
            }}
            
            QHeaderView::section:horizontal {{
                border-top: none;
                border-left: none;
                border-right: 2px solid #000000;
                border-bottom: 3px solid #000000;
            }}
            
            QHeaderView::section:vertical {{
                background-color: {BG_CREAM};
                border-top: none;
                border-left: none;
                border-right: 3px solid #000000;
                border-bottom: 2px solid #000000;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                font-weight: bold;
                color: {COLOR_BLACK};
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

    def refresh_history(self):
        """Reload and display the execution history from history_manager."""
        history = history_manager.load_history()
        
        # Sort in reverse chronological order (newest first)
        history = list(reversed(history))
        
        self.table.setRowCount(len(history))
        
        for row_idx, event in enumerate(history):
            # Timestamp
            ts_item = QTableWidgetItem(event.get("timestamp", ""))
            ts_item.setFlags(ts_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_idx, 0, ts_item)
            
            # SQL Query
            sql_text = event.get("sql", "")
            sql_item = QTableWidgetItem(sql_text)
            sql_item.setToolTip(sql_text)  # Show full query on hover
            sql_item.setFlags(sql_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_idx, 1, sql_item)
            
            # Duration
            dur = event.get("execution_time_ms", 0)
            dur_item = QTableWidgetItem(f"{dur} ms")
            dur_item.setFlags(dur_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_idx, 2, dur_item)
            
            # Status (Neo-brutalist colored cells)
            status = event.get("status", "Success")
            status_item = QTableWidgetItem(status)
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            if status == "Success":
                status_item.setBackground(QColor("#A7F3D0"))  # Mint green
                status_item.setForeground(QColor(COLOR_BLACK))
            else:
                status_item.setBackground(QColor(ACCENT_RED))  # Soft red
                status_item.setForeground(QColor(COLOR_BLACK))
                # Tooltip for error details
                err_msg = event.get("error_message", "")
                if err_msg:
                    status_item.setToolTip(err_msg)
            
            self.table.setItem(row_idx, 3, status_item)
            
        # Configure sizing - timestamp, duration, status fit content; SQL stretches
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def get_selected_sql(self):
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return None
        
        row = selected_ranges[0].topRow()
        sql_item = self.table.item(row, 1)
        if sql_item:
            return sql_item.text()
        return None

    def run_selected_query(self):
        sql = self.get_selected_sql()
        if not sql:
            QMessageBox.information(self, "No Selection", "Please select a history record to run.")
            return
        
        self.run_query_callback(sql)

    def handle_row_double_clicked(self, index):
        row = index.row()
        sql_item = self.table.item(row, 1)
        if sql_item:
            self.run_query_callback(sql_item.text())

    def clear_history(self):
        reply = QMessageBox.question(
            self, "Clear History",
            "Are you sure you want to clear the entire query history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if history_manager.clear_history():
                self.refresh_history()
