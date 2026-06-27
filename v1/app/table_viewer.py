import sys
import mysql.connector
from mysql.connector import Error
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView,
    QStackedWidget, QFrame, QApplication, QMessageBox
)
from PyQt6.QtGui import QColor, QFont, QCursor
from PyQt6.QtCore import Qt

from .styles import (
    apply_neo_shadow, BG_CREAM, COLOR_WHITE, COLOR_BLACK, 
    ACCENT_PURPLE, ACCENT_YELLOW, ACCENT_LIME, ACCENT_RED
)

class TableViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.connection = None
        self.table_name = None
        self.db_name = None
        
        # ⭐ NEW: Tracking variables
        self.modified_cells = {}      # (row, col) -> new_value
        self.column_names = []        # List of column names
        self.primary_key = None       # Primary key column name
        self.row_pk_map = {}          # row_index -> primary_key_value
        self.original_data = []       # Store original data for comparison
        self.is_loading = False       # Prevent signal loops
        
        self.init_ui()
        
        if self.connection and self.table_name:
            self.refresh_data()

    def init_ui(self):
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(12)
        
        # 1. Header Panel
        self.header_panel = QFrame(self)
        self.header_panel.setObjectName("HeaderPanel")
        self.header_layout = QHBoxLayout(self.header_panel)
        self.header_layout.setContentsMargins(15, 12, 15, 12)
        
        self.title_label = QLabel("📋 TABLE: (Select a table)", self.header_panel)
        self.title_label.setObjectName("TitleLabel")
        self.header_layout.addWidget(self.title_label)
        
        self.status_label = QLabel("", self.header_panel)
        self.status_label.setObjectName("StatusLabel")
        self.header_layout.addWidget(self.status_label)
        
        self.header_layout.addStretch()
        
        # ⭐ NEW: SAVE Button
        self.save_btn = QPushButton("💾 SAVE CHANGES", self.header_panel)
        self.save_btn.setObjectName("SaveBtn")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_changes)
        self.save_btn.setEnabled(False)  # Disabled until changes made
        self.header_layout.addWidget(self.save_btn)
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh", self.header_panel)
        self.refresh_btn.setObjectName("RefreshBtn")
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.header_layout.addWidget(self.refresh_btn)
        
        # Close button
        self.close_btn = QPushButton("✕", self.header_panel)
        self.close_btn.setObjectName("CloseBtn")
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.hide)
        self.header_layout.addWidget(self.close_btn)
        
        self.main_layout.addWidget(self.header_panel)
        
        # 2. Stacked Widget
        self.stacked_widget = QStackedWidget(self)
        
        # --- State 0: Loading Page ---
        self.loading_widget = QFrame()
        self.loading_widget.setObjectName("LoadingWidget")
        loading_layout = QVBoxLayout(self.loading_widget)
        loading_lbl = QLabel("⏳ FETCHING ROWS...", self.loading_widget)
        loading_lbl.setObjectName("LoadingLabel")
        loading_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_layout.addWidget(loading_lbl)
        self.stacked_widget.addWidget(self.loading_widget)
        
        # --- State 1: Table Page ---
        self.table = QTableWidget(self)
        
        # ⭐ ENABLE EDITING
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed
        )
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setShowGrid(True)
        self.table.setGridStyle(Qt.PenStyle.SolidLine)
        
        # ⭐ CONNECT SIGNALS
        self.table.cellChanged.connect(self.on_cell_changed)
        self.table.currentCellChanged.connect(self.on_cell_selected)
        
        # Configure headers
        self.table.horizontalHeader().setMinimumSectionSize(120)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.stacked_widget.addWidget(self.table)
        
        # --- State 2: Error Page ---
        self.error_widget = QFrame()
        self.error_widget.setObjectName("ErrorWidget")
        error_layout = QVBoxLayout(self.error_widget)
        error_layout.setContentsMargins(30, 30, 30, 30)
        error_layout.setSpacing(15)
        
        self.error_title = QLabel("⚠️ FAILED TO LOAD DATA", self.error_widget)
        self.error_title.setObjectName("ErrorTitle")
        self.error_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_layout.addWidget(self.error_title)
        
        self.error_details = QLabel("", self.error_widget)
        self.error_details.setObjectName("ErrorDetails")
        self.error_details.setWordWrap(True)
        self.error_details.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_layout.addWidget(self.error_details)
        
        self.stacked_widget.addWidget(self.error_widget)
        
        self.main_layout.addWidget(self.stacked_widget)
        
        apply_neo_shadow(self.header_panel, 4, 4)
        self.apply_styles()

    def apply_styles(self):
        title_font = QFont("Arial Black", 12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
            }}
            
            QFrame#HeaderPanel {{
                background-color: {ACCENT_LIME};
                border: 3px solid #000000;
                border-radius: 0px;
            }}
            
            QLabel#TitleLabel {{
                font-family: 'Arial Black';
                font-size: 13px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            
            QLabel#StatusLabel {{
                font-family: 'Courier New', monospace;
                font-size: 12px;
                font-weight: bold;
                color: {COLOR_BLACK};
                padding-left: 10px;
            }}
            
            QPushButton#SaveBtn {{
                background-color: {ACCENT_PURPLE};
                border: 3px solid #000000;
                border-radius: 0px;
                padding: 5px 12px;
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                color: {COLOR_WHITE};
            }}
            QPushButton#SaveBtn:hover:enabled {{
                background-color: #7C3AED;
            }}
            QPushButton#SaveBtn:disabled {{
                background-color: #D1D5DB;
                color: #6B7280;
            }}
            
            QPushButton#RefreshBtn {{
                background-color: {COLOR_WHITE};
                border: 3px solid #000000;
                border-radius: 0px;
                padding: 5px 12px;
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            QPushButton#RefreshBtn:hover {{
                background-color: {ACCENT_YELLOW};
            }}
            
            QPushButton#CloseBtn {{
                background-color: {COLOR_WHITE};
                border: 3px solid #000000;
                border-radius: 0px;
                font-family: 'Arial';
                font-size: 11px;
                font-weight: bold;
                color: {COLOR_BLACK};
            }}
            QPushButton#CloseBtn:hover {{
                background-color: {ACCENT_RED};
                color: {COLOR_WHITE};
            }}
            
            QFrame#LoadingWidget {{
                background-color: {BG_CREAM};
                border: 3px solid #000000;
                border-radius: 0px;
            }}
            
            QLabel#LoadingLabel {{
                font-family: 'Arial Black';
                font-size: 14px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            
            QFrame#ErrorWidget {{
                background-color: {ACCENT_RED};
                border: 3px solid #000000;
                border-radius: 0px;
            }}
            
            QLabel#ErrorTitle {{
                font-family: 'Arial Black';
                font-size: 15px;
                font-weight: 900;
                color: {COLOR_BLACK};
            }}
            
            QLabel#ErrorDetails {{
                font-family: 'Courier New', monospace;
                font-size: 12px;
                font-weight: bold;
                color: {COLOR_BLACK};
                background-color: #FFFFFF;
                border: 2px solid #000000;
                padding: 15px;
            }}
            
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
                padding: 6px;
                border-bottom: 1px solid #000000;
                border-right: 1px solid #000000;
            }}
            
            QTableWidget::item:selected {{
                background-color: {ACCENT_PURPLE};
                color: {COLOR_WHITE};
            }}
            
            QHeaderView::section {{
                background-color: {ACCENT_YELLOW};
                color: {COLOR_BLACK};
                font-family: 'Arial Black';
                font-size: 11px;
                font-weight: 900;
                border: 2px solid #000000;
                padding: 6px;
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

    def load_table(self, connection, table_name, db_name=None):
        """Public method to bind connection and table, then refresh data."""
        self.connection = connection
        self.table_name = table_name
        self.db_name = db_name
        self.modified_cells = {}
        self.save_btn.setEnabled(False)
        self.refresh_data()

    def refresh_data(self):
        """Executes a query to pull columns and rows from the table."""
        if not self.connection:
            self.show_error("No active MySQL connection.")
            return
            
        if not self.table_name:
            self.show_error("No table specified to query.")
            return
            
        self.show_loading()
        self.is_loading = True
        
        try:
            cursor = self.connection.cursor()
            
            # Find primary key
            self.find_primary_key(cursor)
            
            # Get column info
            if self.db_name:
                cursor.execute(f"DESCRIBE `{self.db_name}`.`{self.table_name}`")
            else:
                cursor.execute(f"DESCRIBE `{self.table_name}`")
            columns_info = cursor.fetchall()
            self.column_names = [col[0] for col in columns_info]
            
            # Get data
            if self.db_name:
                cursor.execute(f"SELECT * FROM `{self.db_name}`.`{self.table_name}` LIMIT 100")
            else:
                cursor.execute(f"SELECT * FROM `{self.table_name}` LIMIT 100")
            
            rows = cursor.fetchall()
            cursor.close()
            
            self.display_data(rows)
            
        except Exception as e:
            self.show_error(f"SQL Error: {str(e)}")
        finally:
            self.is_loading = False

    def find_primary_key(self, cursor):
        """Find the primary key column."""
        try:
            if self.db_name:
                cursor.execute(f"SHOW KEYS FROM `{self.db_name}`.`{self.table_name}` WHERE Key_name = 'PRIMARY'")
            else:
                cursor.execute(f"SHOW KEYS FROM `{self.table_name}` WHERE Key_name = 'PRIMARY'")
            result = cursor.fetchall()
            if result:
                self.primary_key = result[0][4]  # Column_name is at index 4
            else:
                self.primary_key = None
        except:
            self.primary_key = None

    def display_data(self, rows):
        """Fills the grid table with retrieved rows."""
        self.table.blockSignals(True)  # Prevent signals while populating
        self.table.clear()
        
        self.original_data = rows  # Store for comparison
        self.row_pk_map = {}
        self.modified_cells = {}
        self.save_btn.setEnabled(False)
        
        if not rows:
            self.table.setRowCount(0)
            self.table.setColumnCount(len(self.column_names))
            self.table.setHorizontalHeaderLabels(self.column_names)
            self.status_label.setText("[ 0 rows returned ]")
            self.stacked_widget.setCurrentIndex(1)
            self.table.blockSignals(False)
            return
        
        # Find primary key index
        pk_index = -1
        if self.primary_key and self.primary_key in self.column_names:
            pk_index = self.column_names.index(self.primary_key)
        
        self.table.setColumnCount(len(self.column_names))
        self.table.setRowCount(len(rows))
        self.table.setHorizontalHeaderLabels(self.column_names)
        
        for row_idx, row_data in enumerate(rows):
            # Store primary key
            if pk_index >= 0:
                self.row_pk_map[row_idx] = row_data[pk_index]
            
            for col_idx, val in enumerate(row_data):
                if val is None:
                    item = QTableWidgetItem("NULL")
                    item.setForeground(QColor("#9CA3AF"))
                    item.setBackground(QColor("#FEE2E2"))
                else:
                    item = QTableWidgetItem(str(val))
                    item.setForeground(QColor(COLOR_BLACK))
                
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)
        
        self.status_label.setText(f"[ {len(rows)} row(s) returned ]")
        self.table.resizeColumnsToContents()
        self.stacked_widget.setCurrentIndex(1)
        self.table.blockSignals(False)

    def on_cell_selected(self, row, col, prev_row, prev_col):
        """Show cell info when selected."""
        if row >= 0 and col >= 0:
            item = self.table.item(row, col)
            if item:
                col_name = self.column_names[col] if col < len(self.column_names) else "?"
                row_num = row + 1
                value = item.text()
                self.status_label.setText(f"[ 📝 Row {row_num}, '{col_name}' = {value} ]")

    def on_cell_changed(self, row, col):
        """⭐ Track when a cell is modified."""
        if self.is_loading:
            return
        
        item = self.table.item(row, col)
        if not item:
            return
        
        new_value = item.text()
        
        # Get original value
        original_value = None
        if row < len(self.original_data):
            if col < len(self.column_names):
                col_name = self.column_names[col]
                original_value = self.original_data[row][col] if col < len(self.original_data[row]) else None
                if original_value is None:
                    original_value = "NULL"
        
        # If value didn't actually change, remove from tracking
        if str(original_value) == new_value:
            if (row, col) in self.modified_cells:
                del self.modified_cells[(row, col)]
                # Reset background
                if new_value == "NULL":
                    item.setBackground(QColor("#FEE2E2"))
                else:
                    item.setBackground(QColor(COLOR_WHITE))
            self.save_btn.setEnabled(bool(self.modified_cells))
            self.update_status()
            return
        
        # Store the change - ⭐ THIS IS THE CRITICAL PART
        self.modified_cells[(row, col)] = new_value
        
        # Highlight cell YELLOW
        item.setBackground(QColor("#FEF08A"))
        
        # Enable save button
        self.save_btn.setEnabled(True)
        self.update_status()

    def update_status(self):
        """Update status with change count."""
        count = len(self.modified_cells)
        if count > 0:
            self.status_label.setText(f"[ ✏️ {count} cell(s) modified - Click SAVE ]")
        else:
            self.status_label.setText("[ ✅ No pending changes ]")

    def save_changes(self):
        """⭐ Save all modified cells to database."""
        if not self.modified_cells:
            QMessageBox.information(self, "No Changes", "No changes to save.")
            return
        
        if not self.primary_key:
            QMessageBox.warning(self, "No Primary Key", 
                               "This table doesn't have a primary key. Cannot update rows safely.")
            return
        
        try:
            self.is_loading = True
            self.status_label.setText("[ ⏳ Saving changes... ]")
            QApplication.processEvents()
            
            cursor = self.connection.cursor()
            
            # Group changes by row
            changes_by_row = {}
            for (row, col), new_value in self.modified_cells.items():
                if row not in changes_by_row:
                    changes_by_row[row] = {}
                changes_by_row[row][col] = new_value
            
            success_count = 0
            error_count = 0
            error_messages = []
            
            for row_idx, changes in changes_by_row.items():
                pk_value = self.row_pk_map.get(row_idx)
                if pk_value is None:
                    error_count += 1
                    error_messages.append(f"Row {row_idx+1}: No primary key found")
                    continue
                
                # Build UPDATE query
                set_parts = []
                values = []
                
                for col_idx, new_value in changes.items():
                    col_name = self.column_names[col_idx]
                    set_parts.append(f"`{col_name}` = %s")
                    
                    # Convert "NULL" string to real NULL
                    if new_value.strip().upper() == "NULL":
                        values.append(None)
                    else:
                        values.append(new_value)
                
                values.append(pk_value)
                
                if self.db_name:
                    query = f"UPDATE `{self.db_name}`.`{self.table_name}` SET {', '.join(set_parts)} WHERE `{self.primary_key}` = %s"
                else:
                    query = f"UPDATE `{self.table_name}` SET {', '.join(set_parts)} WHERE `{self.primary_key}` = %s"
                
                try:
                    cursor.execute(query, values)
                    self.connection.commit()
                    success_count += 1
                    
                    # Reset cell backgrounds for this row
                    for col_idx in changes.keys():
                        item = self.table.item(row_idx, col_idx)
                        if item:
                            if item.text().strip().upper() == "NULL":
                                item.setBackground(QColor("#FEE2E2"))
                            else:
                                item.setBackground(QColor(COLOR_WHITE))
                    
                except mysql.connector.Error as e:
                    error_count += 1
                    error_messages.append(f"Row {row_idx+1}: {e}")
            
            # Clear modified cells
            self.modified_cells = {}
            self.save_btn.setEnabled(False)
            
            # Show result
            if error_count == 0:
                self.status_label.setText(f"[ ✅ {success_count} row(s) updated successfully ]")
                QMessageBox.information(self, "Success", f"Updated {success_count} row(s) successfully!")
            else:
                self.status_label.setText(f"[ ⚠️ {success_count} updated, {error_count} failed ]")
                QMessageBox.warning(self, "Partial Success", 
                                   f"{success_count} row(s) updated.\n{error_count} failed.\n\nErrors:\n" + "\n".join(error_messages[:5]))
            
            # Refresh to get latest data
            self.refresh_data()
            
        except Exception as e:
            self.status_label.setText(f"[ ❌ Error: {str(e)} ]")
            QMessageBox.critical(self, "Error", f"Failed to save changes:\n{str(e)}")
        
        finally:
            self.is_loading = False

    def show_loading(self):
        """Switches UI state to loading."""
        self.status_label.setText("[ Fetching... ]")
        self.stacked_widget.setCurrentIndex(0)

    def show_error(self, message):
        """Switches UI state to error showing the details."""
        self.status_label.setText("[ Error ]")
        self.error_details.setText(message)
        self.stacked_widget.setCurrentIndex(2)