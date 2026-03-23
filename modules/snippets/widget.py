from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem,
    QTextEdit, QSplitter, QApplication,
    QPushButton, QLabel, QLineEdit
)
from PySide6.QtCore import Qt, QMimeData, QTimer
from PySide6.QtGui import QTextDocument, QColor


# =====================
# ✍️ EDITOR
# =====================
class CustomTextEdit(QTextEdit):
    def __init__(self, theme):
        super().__init__()
        self.theme = theme

        self.setPlaceholderText("Pegá y editá texto aquí...")

        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.theme["bg_sidebar"]};
                color: {self.theme["text"]};
                border: 1px solid {self.theme["bg_hover"]};
                border-radius: 6px;
                padding: 8px;
            }}
        """)


# =====================
# 📦 WIDGET PRINCIPAL
# =====================
class SnippetsWidget(QWidget):

    persistent_html = ""

    def __init__(self, theme, service):
        super().__init__()

        self.theme = theme
        self.service = service

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme["bg_main"]};
                color: {self.theme["text"]};
            }}
        """)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # =====================
        title = QLabel("Snippets")
        main_layout.addWidget(title)

        # 🔍 BUSCADOR
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme["bg_sidebar"]};
                border: 1px solid {self.theme["bg_hover"]};
                border-radius: 6px;
                padding: 4px;
            }}
        """)
        main_layout.addWidget(self.search_input)

        # =====================
        splitter = QSplitter(Qt.Vertical)

        # =====================
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)

        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {self.theme["bg_sidebar"]};
                border: 1px solid {self.theme["bg_hover"]};
                border-radius: 6px;
                padding: 4px;
            }}
            QTreeWidget::item:selected {{
                background-color: {self.theme["bg_active"]};
            }}
        """)

        splitter.addWidget(self.tree)

        # =====================
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout()
        bottom_widget.setLayout(bottom_layout)

        self.editor = CustomTextEdit(self.theme)
        bottom_layout.addWidget(self.editor)

        # =====================
        buttons_layout = QHBoxLayout()

        self.btn_copy_all = QPushButton("Copiar todo")
        self.btn_clear = QPushButton("Borrar todo")

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_copy_all)
        buttons_layout.addWidget(self.btn_clear)
        buttons_layout.addStretch()

        bottom_layout.addLayout(buttons_layout)

        splitter.addWidget(bottom_widget)
        splitter.setSizes([350, 250])

        main_layout.addWidget(splitter)

        # =====================
        self.tree.itemDoubleClicked.connect(self.copy_snippet)
        self.btn_clear.clicked.connect(self.clear_editor)
        self.btn_copy_all.clicked.connect(self.copy_all_editor)
        self.editor.textChanged.connect(self.save_persistent_content)

        self.search_input.textChanged.connect(self.apply_search)

        self.service.data_changed.connect(self.load_snippets)

        self.load_snippets()

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

        # 🔥 CLAVE UX
        self.tree.expandAll()

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

            for s in sorted(groups[group_name], key=lambda x: x["title"]):
                child = QTreeWidgetItem([s["title"]])
                child.setData(0, Qt.UserRole, s)
                group_item.addChild(child)

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

        original_color = item.foreground(0)
        highlight_color = QColor(self.theme["accent"])

        item.setForeground(0, highlight_color)
        QTimer.singleShot(1000, lambda: item.setForeground(0, original_color))

    def copy_all_editor(self):
        html = self.editor.toHtml()

        doc = QTextDocument()
        doc.setHtml(html)
        plain_text = doc.toPlainText()

        mime = QMimeData()
        mime.setHtml(html)
        mime.setText(plain_text)

        QApplication.clipboard().setMimeData(mime)

    def clear_editor(self):
        self.editor.clear()
        SnippetsWidget.persistent_html = ""

    def save_persistent_content(self):
        SnippetsWidget.persistent_html = self.editor.toHtml()