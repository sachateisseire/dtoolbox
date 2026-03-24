from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem,
    QPushButton, QLineEdit, QTextEdit,
    QLabel, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCharFormat, QFont, QColor


# =====================
# ✍️ EDITOR TEXTO
# =====================
class CustomTextEdit(QTextEdit):
    def __init__(self, theme):
        super().__init__()
        self.theme = theme

        self.setPlaceholderText("Contenido")
        self.apply_theme(theme)

    def apply_theme(self, theme):
        self.theme = theme
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {theme["bg_sidebar"]};
                color: {theme["text"]};
                border: 1px solid {theme["bg_hover"]};
                border-radius: 6px;
                padding: 6px;
            }}
        """)

    def insertFromMimeData(self, source):
        text = source.text()
        cursor = self.textCursor()

        fmt = QTextCharFormat()
        fmt.setForeground(QColor(self.theme["text"]))
        fmt.setFontWeight(QFont.Normal)

        cursor.insertText(text, fmt)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_B:
                self.toggle_bold(); return
            if event.key() == Qt.Key_I:
                self.toggle_italic(); return
            if event.key() == Qt.Key_U:
                self.toggle_underline(); return

        super().keyPressEvent(event)

    def apply_format(self, fmt):
        cursor = self.textCursor()
        if cursor.hasSelection():
            cursor.mergeCharFormat(fmt)
        else:
            self.mergeCurrentCharFormat(fmt)

    def toggle_bold(self):
        fmt = QTextCharFormat()
        current = self.textCursor().charFormat().fontWeight()
        fmt.setFontWeight(QFont.Normal if current == QFont.Bold else QFont.Bold)
        self.apply_format(fmt)

    def toggle_italic(self):
        fmt = QTextCharFormat()
        current = self.textCursor().charFormat().fontItalic()
        fmt.setFontItalic(not current)
        self.apply_format(fmt)

    def toggle_underline(self):
        fmt = QTextCharFormat()
        current = self.textCursor().charFormat().fontUnderline()
        fmt.setFontUnderline(not current)
        self.apply_format(fmt)


# =====================
# 📦 WIDGET PRINCIPAL
# =====================
class EditorWidget(QWidget):
    def __init__(self, theme, service):
        super().__init__()

        self.theme = theme
        self.service = service

        self.selected_id = None
        self.mode = "idle"

        layout = QVBoxLayout()
        self.setLayout(layout)

        # =====================
        self.title = QLabel("Editor de Snippets")
        layout.addWidget(self.title)

        # 🔍 BUSCADOR
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar...")
        layout.addWidget(self.search_input)

        # =====================
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        layout.addWidget(self.tree)

        # =====================
        self.form_frame = QFrame()
        self.form_layout = QVBoxLayout()
        self.form_frame.setLayout(self.form_layout)

        self.input_group = QLineEdit()
        self.input_group.setPlaceholderText("Grupo")

        self.input_title = QLineEdit()
        self.input_title.setPlaceholderText("Título")

        self.input_content = CustomTextEdit(self.theme)

        self.form_layout.addWidget(self.input_group)
        self.form_layout.addWidget(self.input_title)
        self.form_layout.addWidget(self.input_content)

        layout.addWidget(self.form_frame)

        # =====================
        self.btn_layout = QHBoxLayout()

        self.btn_new = QPushButton("Nuevo")
        self.btn_edit = QPushButton("Editar")
        self.btn_delete = QPushButton("Eliminar")
        self.btn_save = QPushButton("Guardar")
        self.btn_cancel = QPushButton("Cancelar")

        for btn in [self.btn_new, self.btn_edit, self.btn_delete, self.btn_save, self.btn_cancel]:
            btn.setMaximumWidth(90)

        self.btn_layout.addWidget(self.btn_new)
        self.btn_layout.addWidget(self.btn_edit)
        self.btn_layout.addWidget(self.btn_delete)
        self.btn_layout.addWidget(self.btn_save)
        self.btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(self.btn_layout)

        # =====================
        self.tree.itemClicked.connect(self.load_selected)

        self.btn_new.clicked.connect(self.new_snippet)
        self.btn_edit.clicked.connect(self.enter_edit_mode)
        self.btn_delete.clicked.connect(self.delete_snippet)
        self.btn_save.clicked.connect(self.save_snippet)
        self.btn_cancel.clicked.connect(self.cancel_edit)

        self.search_input.textChanged.connect(self.apply_search)

        self.load_snippets()
        self.update_ui()

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

            QLineEdit {{
                background-color: {theme["bg_sidebar"]};
                border: 1px solid {theme["bg_hover"]};
                border-radius: 6px;
                padding: 4px;
            }}

            QTreeWidget {{
                background-color: {theme["bg_sidebar"]};
                border: 1px solid {theme["bg_hover"]};
                border-radius: 6px;
            }}

            QTreeWidget::item:selected {{
                background-color: {theme["bg_active"]};
            }}

            QPushButton {{
                border: 1px solid {theme["bg_hover"]};
                border-radius: 6px;
                padding: 3px 8px;
            }}

            QPushButton:hover {{
                background-color: {theme["bg_hover"]};
            }}
        """)

        # 🔥 actualizar editor interno
        if hasattr(self, "input_content"):
            self.input_content.apply_theme(theme)

    # =====================
    def apply_search(self):
        text = self.search_input.text().strip()

        if not text:
            self.load_snippets()
            return

        results = self.service.search(text)

        self.tree.clear()

        groups = {}
        for s in results:
            groups.setdefault(s["group"], []).append(s)

        for group_name in sorted(groups.keys()):
            group_item = QTreeWidgetItem([group_name])
            self.tree.addTopLevelItem(group_item)

            for s in groups[group_name]:
                child = QTreeWidgetItem([s["title"]])
                child.setData(0, Qt.UserRole, s)
                group_item.addChild(child)

        self.tree.expandAll()

    # =====================
    def update_ui(self):
        for btn in [self.btn_new, self.btn_edit, self.btn_delete, self.btn_save, self.btn_cancel]:
            btn.hide()

        if self.mode == "idle":
            self.btn_new.show()

        elif self.mode == "view":
            self.btn_new.show()
            self.btn_edit.show()
            self.btn_delete.show()

        elif self.mode == "edit":
            self.btn_save.show()
            self.btn_cancel.show()

        if self.mode == "edit":
            self.form_frame.setStyleSheet(f"""
                QFrame {{
                    border: 2px solid {self.theme["accent"]};
                    border-radius: 6px;
                    padding: 6px;
                }}
            """)
        else:
            self.form_frame.setStyleSheet("")

        editable = self.mode == "edit"

        for w in [self.input_group, self.input_title, self.input_content]:
            w.setReadOnly(not editable)

    # =====================
    def load_snippets(self):
        self.tree.clear()
        snippets = self.service.get_all()

        groups = {}
        for s in snippets:
            groups.setdefault(s["group"], []).append(s)

        for group_name in sorted(groups.keys()):
            group_item = QTreeWidgetItem([group_name])
            self.tree.addTopLevelItem(group_item)

            for s in groups[group_name]:
                child = QTreeWidgetItem([s["title"]])
                child.setData(0, Qt.UserRole, s)
                group_item.addChild(child)

    # =====================
    def load_selected(self, item, column):
        snippet = item.data(0, Qt.UserRole)

        if not snippet:
            return

        self.selected_id = snippet["id"]

        self.input_group.setText(snippet["group"])
        self.input_title.setText(snippet["title"])
        self.input_content.setHtml(snippet["content"])

        self.mode = "view"
        self.update_ui()

    # =====================
    def new_snippet(self):
        self.selected_id = None
        self.input_group.clear()
        self.input_title.clear()
        self.input_content.clear()

        self.mode = "edit"
        self.update_ui()

    def enter_edit_mode(self):
        if not self.selected_id:
            return

        self.mode = "edit"
        self.update_ui()

    def save_snippet(self):
        group = self.input_group.text()
        title = self.input_title.text()
        content = self.input_content.toHtml()

        try:
            if self.selected_id:
                self.service.update(
                    self.selected_id,
                    group=group,
                    title=title,
                    content=content
                )
            else:
                self.service.add(group, title, content)

            self.load_snippets()
            self.mode = "idle"
            self.update_ui()

        except Exception as e:
            print("Error:", e)

    def cancel_edit(self):
        self.mode = "idle"
        self.update_ui()

    def delete_snippet(self):
        if not self.selected_id:
            return

        try:
            self.service.delete(self.selected_id)

            self.selected_id = None
            self.input_group.clear()
            self.input_title.clear()
            self.input_content.clear()

            self.load_snippets()
            self.mode = "idle"
            self.update_ui()

        except Exception as e:
            print("Error:", e)