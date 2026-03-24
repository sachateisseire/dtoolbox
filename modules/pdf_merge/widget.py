from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel,
    QMessageBox, QTableView, QHeaderView
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from pypdf import PdfReader, PdfWriter
import os
from datetime import datetime


# =====================
# 📊 MODELO PRO
# =====================
class PDFTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.sort_ascending = True

    def rowCount(self, parent=None):
        return len(self.rows)

    def columnCount(self, parent=None):
        return 2

    def data(self, index, role):
        if not index.isValid():
            return None

        row = self.rows[index.row()]

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return row["name"]
            if index.column() == 1:
                return row["date_str"]

        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return ["Archivo", "Fecha creación"][section]
        return None

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

    # =====================
    # DRAG & DROP REAL
    def supportedDropActions(self):
        return Qt.MoveAction

    def mimeTypes(self):
        return ["application/x-row"]

    def mimeData(self, indexes):
        mime = super().mimeData(indexes)
        mime.setText(str(indexes[0].row()))
        return mime

    def dropMimeData(self, data, action, row, column, parent):
        if action == Qt.IgnoreAction:
            return False

        source_row = int(data.text())

        if row == -1:
            row = parent.row()

        if row < 0:
            row = len(self.rows)

        if source_row == row or source_row + 1 == row:
            return False

        self.beginMoveRows(QModelIndex(), source_row, source_row, QModelIndex(), row)

        item = self.rows.pop(source_row)

        if row > source_row:
            row -= 1

        self.rows.insert(row, item)

        self.endMoveRows()
        return True

    # =====================
    def add_file(self, path):
        name = os.path.basename(path)

        try:
            ts = os.path.getctime(path)
            dt = datetime.fromtimestamp(ts)
            date_str = dt.strftime("%d/%m/%Y %H:%M:%S")
        except:
            ts = 0
            date_str = "N/A"

        self.beginInsertRows(QModelIndex(), len(self.rows), len(self.rows))
        self.rows.append({
            "path": path,
            "name": name,
            "timestamp": ts,
            "date_str": date_str
        })
        self.endInsertRows()

    def remove_row(self, row):
        if row < 0:
            return
        self.beginRemoveRows(QModelIndex(), row, row)
        self.rows.pop(row)
        self.endRemoveRows()

    def clear(self):
        self.beginResetModel()
        self.rows = []
        self.endResetModel()

    def get_files(self):
        return [r["path"] for r in self.rows]

    def sort_by_date(self):
        self.sort_ascending = not self.sort_ascending
        self.beginResetModel()
        self.rows.sort(key=lambda x: x["timestamp"], reverse=not self.sort_ascending)
        self.endResetModel()


# =====================
# 📦 WIDGET
# =====================
class PDFMergeWidget(QWidget):
    def __init__(self, theme):
        super().__init__()

        self.theme = theme
        self.model = PDFTableModel()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.title = QLabel("Merge de PDFs")
        layout.addWidget(self.title)

        # =====================
        self.table = QTableView()
        self.table.setModel(self.model)

        self.table.setDragEnabled(True)
        self.table.setAcceptDrops(True)
        self.table.setDropIndicatorShown(True)
        self.table.setDragDropMode(QTableView.InternalMove)

        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.sectionClicked.connect(self.on_header_click)

        layout.addWidget(self.table)

        # =====================
        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("Agregar")
        self.btn_remove = QPushButton("Eliminar")
        self.btn_clear = QPushButton("Eliminar todo")
        self.btn_merge = QPushButton("Mergear")

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_merge)

        layout.addLayout(btn_layout)

        # =====================
        self.btn_add.clicked.connect(self.add_files)
        self.btn_remove.clicked.connect(self.remove_selected)
        self.btn_clear.clicked.connect(self.model.clear)
        self.btn_merge.clicked.connect(self.merge_pdfs)

        # 🔥 aplicar theme inicial
        self.apply_theme(self.theme)

    # =====================
    # 🔥 THEME DINÁMICO
    def apply_theme(self, theme):
        self.theme = theme

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["bg_main"]};
                color: {theme["text"]};
            }}

            QTableView {{
                background-color: {theme["bg_sidebar"]};
                border: 1px solid {theme["bg_hover"]};
                border-radius: 6px;
            }}

            QTableView::item:selected {{
                background-color: {theme["bg_active"]};
            }}

            QPushButton {{
                border: 1px solid {theme["bg_hover"]};
                border-radius: 6px;
                padding: 3px 8px;
                min-width: 90px;
            }}

            QPushButton:hover {{
                background-color: {theme["bg_hover"]};
            }}
        """)

    # =====================
    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "PDFs", "", "PDF (*.pdf)")
        for f in files:
            if f not in self.model.get_files():
                self.model.add_file(f)

    def remove_selected(self):
        idx = self.table.currentIndex()
        self.model.remove_row(idx.row())

    def on_header_click(self, index):
        if index == 1:
            self.model.sort_by_date()

    # =====================
    def merge_pdfs(self):
        files = self.model.get_files()

        if not files:
            QMessageBox.warning(self, "Error", "No hay archivos")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Guardar", "", "PDF (*.pdf)")
        if not save_path:
            return

        writer = PdfWriter()

        try:
            for f in files:
                reader = PdfReader(f)
                for p in reader.pages:
                    writer.add_page(p)

            with open(save_path, "wb") as f:
                writer.write(f)

            QMessageBox.information(self, "OK", "PDF generado")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))