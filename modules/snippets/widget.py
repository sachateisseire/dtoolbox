from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem,
    QTextEdit, QSplitter, QApplication,
    QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, QMimeData, QTimer
from PySide6.QtGui import QTextDocument, QColor

from core.snippets_manager import SnippetsManager


# =====================
# ✍️ EDITOR LIBRE
# =====================
class CustomTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("Pegá y editá texto libremente aquí...")
        self.apply_block_format()

    def apply_block_format(self):
        cursor = self.textCursor()
        cursor.beginEditBlock()

        block = self.document().firstBlock()
        while block.isValid():
            cursor.setPosition(block.position())

            fmt = cursor.blockFormat()
            fmt.setBottomMargin(12)
            fmt.setAlignment(Qt.AlignJustify)

            cursor.setBlockFormat(fmt)
            block = block.next()

        cursor.endEditBlock()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.apply_block_format()


# =====================
# 📦 WIDGET PRINCIPAL
# =====================
class SnippetsWidget(QWidget):

    # 🔥 Persistencia en memoria (mientras la app está abierta)
    persistent_html = ""

    def __init__(self):
        super().__init__()

        self.manager = SnippetsManager()

        layout = QVBoxLayout()
        self.setLayout(layout)

        splitter = QSplitter(Qt.Vertical)

        # =====================
        # 🌳 TREE
        # =====================
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        splitter.addWidget(self.tree)

        # =====================
        # CONTENEDOR INFERIOR
        # =====================
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout()
        bottom_widget.setLayout(bottom_layout)

        # ✍️ EDITOR
        self.editor = CustomTextEdit()
        bottom_layout.addWidget(self.editor)

        # =====================
        # BOTONES
        # =====================
        buttons_layout = QHBoxLayout()

        self.btn_copy_all = QPushButton("Copiar todo")
        self.btn_clear = QPushButton("Borrar todo")

        button_style = """
        QPushButton {
            padding: 2px 6px;
            min-height: 20px;
        }
        """

        for btn in (self.btn_copy_all, self.btn_clear):
            btn.setStyleSheet(button_style)
            btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_copy_all)
        buttons_layout.addWidget(self.btn_clear)
        buttons_layout.addStretch()

        bottom_layout.addLayout(buttons_layout)

        splitter.addWidget(bottom_widget)
        splitter.setSizes([400, 200])

        layout.addWidget(splitter)

        # =====================
        # CONEXIONES
        # =====================
        self.tree.itemDoubleClicked.connect(self.copy_snippet)
        self.btn_clear.clicked.connect(self.clear_editor)
        self.btn_copy_all.clicked.connect(self.copy_all_editor)
        self.editor.textChanged.connect(self.save_persistent_content)

        self.load_snippets()

        # =====================
        # RESTAURAR CONTENIDO
        # =====================
        if SnippetsWidget.persistent_html:
            self.editor.setHtml(SnippetsWidget.persistent_html)

    # =====================
    # 🌳 CARGA SNIPPETS
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
    # 📋 COPIAR SNIPPET
    # =====================
    def copy_snippet(self, item, column):
        snippet = item.data(0, Qt.UserRole)

        if not snippet:
            return

        html = snippet["content"]

        doc = QTextDocument()
        doc.setHtml(html)
        plain_text = doc.toPlainText()

        mime = QMimeData()
        mime.setHtml(html)
        mime.setText(plain_text)

        QApplication.clipboard().setMimeData(mime)

        # 🔥 FEEDBACK VISUAL
        original_color = item.foreground(0)
        highlight_color = QColor("#820933")

        item.setForeground(0, highlight_color)

        QTimer.singleShot(1000, lambda: item.setForeground(0, original_color))

    # =====================
    # 📋 COPIAR TODO EDITOR
    # =====================
    def copy_all_editor(self):
        html = self.editor.toHtml()

        doc = QTextDocument()
        doc.setHtml(html)
        plain_text = doc.toPlainText()

        mime = QMimeData()
        mime.setHtml(html)
        mime.setText(plain_text)

        QApplication.clipboard().setMimeData(mime)

    # =====================
    # 🧹 BORRAR EDITOR
    # =====================
    def clear_editor(self):
        self.editor.clear()
        SnippetsWidget.persistent_html = ""

    # =====================
    # 💾 PERSISTENCIA
    # =====================
    def save_persistent_content(self):
        SnippetsWidget.persistent_html = self.editor.toHtml()