from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem,
    QPushButton, QLineEdit, QTextEdit,
    QLabel, QFrame, QSizePolicy
)
from PySide6.QtGui import QTextCharFormat, QFont, QTextBlockFormat
from PySide6.QtCore import Qt

from core.snippets_manager import SnippetsManager


class CustomTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("Contenido")
        self.apply_block_format()

    def apply_block_format(self):
        cursor = self.textCursor()
        cursor.beginEditBlock()

        block = self.document().firstBlock()
        while block.isValid():
            cursor.setPosition(block.position())

            fmt = cursor.blockFormat()
            fmt.setBottomMargin(12)
            fmt.setAlignment(Qt.AlignJustify)  # 🔥 JUSTIFICADO

            cursor.setBlockFormat(fmt)
            block = block.next()

        cursor.endEditBlock()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.apply_block_format()


class EditorWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.manager = SnippetsManager()
        self.selected_id = None
        self.edit_mode = False
        self.creating = False

        layout = QVBoxLayout()
        self.setLayout(layout)

        # =====================
        title = QLabel("Módulo Editor")
        layout.addWidget(title)

        # =====================
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        layout.addWidget(self.tree)

        # =====================
        main_buttons = QHBoxLayout()

        self.btn_create = QPushButton("Crear")
        self.btn_create.setCheckable(True)

        self.btn_modify = QPushButton("Modificar")
        self.btn_modify.setCheckable(True)

        self.btn_delete = QPushButton("Eliminar")

        button_style = """
        QPushButton {
            padding: 2px 6px;
            min-height: 20px;
        }
        QPushButton:checked {
            background-color: #820933;
            color: white;
        }
        """

        for btn in (self.btn_create, self.btn_modify, self.btn_delete):
            btn.setStyleSheet(button_style)
            btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)

        main_buttons.addStretch()
        main_buttons.addWidget(self.btn_create)
        main_buttons.addWidget(self.btn_modify)
        main_buttons.addWidget(self.btn_delete)
        main_buttons.addStretch()

        layout.addLayout(main_buttons)

        # =====================
        self.form_frame = QFrame()
        self.form_frame.setStyleSheet("""
        QFrame {
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px;
        }
        """)

        form_layout = QVBoxLayout()
        self.form_frame.setLayout(form_layout)

        self.input_group = QLineEdit()
        self.input_group.setPlaceholderText("Grupo")

        self.input_title = QLineEdit()
        self.input_title.setPlaceholderText("Título")

        self.input_content = CustomTextEdit()

        # =====================
        format_layout = QHBoxLayout()

        self.btn_bold = QPushButton("Negrita")
        self.btn_bold.setCheckable(True)

        self.btn_italic = QPushButton("Itálica")
        self.btn_italic.setCheckable(True)

        self.btn_underline = QPushButton("Subrayado")
        self.btn_underline.setCheckable(True)

        for btn in (self.btn_bold, self.btn_italic, self.btn_underline):
            btn.setStyleSheet(button_style)

        format_layout.addWidget(self.btn_bold)
        format_layout.addWidget(self.btn_italic)
        format_layout.addWidget(self.btn_underline)

        # =====================
        form_buttons = QHBoxLayout()
        self.btn_save = QPushButton("Guardar")
        self.btn_cancel = QPushButton("Cancelar")

        form_buttons.addWidget(self.btn_save)
        form_buttons.addWidget(self.btn_cancel)

        form_layout.addWidget(self.input_group)
        form_layout.addWidget(self.input_title)
        form_layout.addLayout(format_layout)
        form_layout.addWidget(self.input_content)
        form_layout.addLayout(form_buttons)

        layout.addWidget(self.form_frame)

        # =====================
        self.btn_create.clicked.connect(self.create_mode)
        self.btn_modify.clicked.connect(self.toggle_modify_mode)
        self.btn_delete.clicked.connect(self.delete_snippet)

        self.btn_save.clicked.connect(self.save_snippet)
        self.btn_cancel.clicked.connect(self.cancel_edit)

        self.tree.itemClicked.connect(self.load_selected)

        self.btn_bold.clicked.connect(self.toggle_bold)
        self.btn_italic.clicked.connect(self.toggle_italic)
        self.btn_underline.clicked.connect(self.toggle_underline)

        self.input_content.cursorPositionChanged.connect(self.update_buttons)

        self.load_snippets()
        self.update_buttons_state()
        self.set_read_only_mode()

    # =====================
    def load_snippets(self):
        self.tree.clear()
        snippets = self.manager.get_all()

        groups = {}
        for s in snippets:
            groups.setdefault(s["group"], []).append(s)

        for group_name in sorted(groups.keys()):
            group_item = QTreeWidgetItem([group_name])
            self.tree.addTopLevelItem(group_item)

            for s in sorted(groups[group_name], key=lambda x: x["title"]):
                child = QTreeWidgetItem([s["title"]])
                child.setData(0, Qt.UserRole, s)
                group_item.addChild(child)

        self.tree.collapseAll()

    # =====================
    def load_selected(self, item, column):
        snippet = item.data(0, Qt.UserRole)

        if not snippet or self.creating:
            return

        self.selected_id = snippet["id"]

        self.input_group.setText(snippet["group"])
        self.input_title.setText(snippet["title"])

        self.input_content.setHtml(snippet["content"])
        self.input_content.apply_block_format()  # 🔥 aplicar también al cargar

        self.set_read_only_mode()
        self.update_buttons_state()

    # =====================
    def update_buttons_state(self):
        if self.creating:
            self.btn_modify.setEnabled(False)
            self.btn_delete.setEnabled(False)
        else:
            has_selection = self.selected_id is not None
            self.btn_modify.setEnabled(has_selection)
            self.btn_delete.setEnabled(has_selection)

    # =====================
    def set_read_only_mode(self):
        self.edit_mode = False
        self.creating = False

        self.btn_modify.setChecked(False)
        self.btn_create.setChecked(False)

        for w in (self.input_group, self.input_title, self.input_content):
            w.setReadOnly(True)

        self.form_frame.setStyleSheet("""
        QFrame {
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px;
            opacity: 0.6;
        }
        """)

        self.update_buttons_state()

    # =====================
    def toggle_modify_mode(self):
        if not self.selected_id or self.creating:
            return

        if self.btn_modify.isChecked():
            self.edit_mode = True
            self.btn_create.setChecked(False)

            for w in (self.input_group, self.input_title, self.input_content):
                w.setReadOnly(False)

            self.form_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #820933;
                border-radius: 6px;
                padding: 8px;
            }
            """)
        else:
            self.set_read_only_mode()

    # =====================
    def create_mode(self):
        self.clear_form()
        self.edit_mode = True
        self.creating = True

        self.tree.clearSelection()

        self.btn_create.setChecked(True)
        self.btn_modify.setChecked(False)

        for w in (self.input_group, self.input_title, self.input_content):
            w.setReadOnly(False)

        self.form_frame.setStyleSheet("""
        QFrame {
            border: 1px solid #820933;
            border-radius: 6px;
            padding: 8px;
        }
        """)

        self.update_buttons_state()

    # =====================
    def cancel_edit(self):
        self.clear_form()
        self.set_read_only_mode()

    # =====================
    def save_snippet(self):
        if not self.edit_mode:
            return

        group = self.input_group.text()
        title = self.input_title.text()
        content = self.input_content.toHtml()

        try:
            if self.selected_id:
                self.manager.update(self.selected_id, group=group, title=title, content=content)
            else:
                self.manager.add(group, title, content)
        except Exception as e:
            print("Error:", e)
            return

        self.load_snippets()
        self.clear_form()
        self.set_read_only_mode()

    # =====================
    def delete_snippet(self):
        if not self.selected_id:
            return

        self.manager.delete(self.selected_id)
        self.load_snippets()
        self.clear_form()
        self.set_read_only_mode()

    # =====================
    def clear_form(self):
        self.selected_id = None
        self.input_group.clear()
        self.input_title.clear()
        self.input_content.clear()

        self.update_buttons_state()

    # =====================
    # FORMATO
    # =====================
    def apply_format(self, fmt):
        if not self.edit_mode:
            return

        cursor = self.input_content.textCursor()

        if cursor.hasSelection():
            cursor.mergeCharFormat(fmt)
        else:
            self.input_content.mergeCurrentCharFormat(fmt)

        self.input_content.setFocus()

    def toggle_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if self.btn_bold.isChecked() else QFont.Normal)
        self.apply_format(fmt)

    def toggle_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.btn_italic.isChecked())
        self.apply_format(fmt)

    def toggle_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.btn_underline.isChecked())
        self.apply_format(fmt)

    def update_buttons(self):
        cursor = self.input_content.textCursor()
        fmt = cursor.charFormat()

        self.btn_bold.setChecked(fmt.fontWeight() == QFont.Bold)
        self.btn_italic.setChecked(fmt.fontItalic())
        self.btn_underline.setChecked(fmt.fontUnderline())