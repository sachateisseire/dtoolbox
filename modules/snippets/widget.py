from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem,
    QTextEdit, QSplitter, QApplication,
    QPushButton, QLabel
)
from PySide6.QtCore import Qt, QMimeData, QTimer
from PySide6.QtGui import QTextDocument, QColor

from core.snippets_manager import SnippetsManager


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

    def __init__(self, theme):
        super().__init__()

        self.theme = theme
        self.manager = SnippetsManager()

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme["bg_main"]};
                color: {self.theme["text"]};
            }}
        """)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)

        # =====================
        # 🏷 TÍTULO (igual que Editor)
        # =====================
        title = QLabel("Snippets")
        main_layout.addWidget(title)

        # =====================
        # SPLITTER
        # =====================
        splitter = QSplitter(Qt.Vertical)

        # =====================
        # 🌳 TREE
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
            QTreeWidget::item {{
                padding: 4px;
            }}
            QTreeWidget::item:selected {{
                background-color: {self.theme["bg_active"]};
            }}
        """)

        splitter.addWidget(self.tree)

        # =====================
        # 🔽 PARTE INFERIOR
        # =====================
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(8)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_widget.setLayout(bottom_layout)

        self.editor = CustomTextEdit(self.theme)
        bottom_layout.addWidget(self.editor)

        # =====================
        # BOTONES
        # =====================
        buttons_layout = QHBoxLayout()

        self.btn_copy_all = QPushButton("Copiar todo")
        self.btn_clear = QPushButton("Borrar todo")

        for btn in (self.btn_copy_all, self.btn_clear):
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.theme["bg_active"]};
                    color: {self.theme["text"]};
                    border-radius: 6px;
                    padding: 6px 10px;
                }}
                QPushButton:hover {{
                    background-color: {self.theme["bg_hover"]};
                }}
            """)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_copy_all)
        buttons_layout.addWidget(self.btn_clear)
        buttons_layout.addStretch()

        bottom_layout.addLayout(buttons_layout)

        splitter.addWidget(bottom_widget)

        splitter.setSizes([350, 250])

        main_layout.addWidget(splitter)

        # =====================
        # CONEXIONES
        # =====================
        self.tree.itemDoubleClicked.connect(self.copy_snippet)
        self.btn_clear.clicked.connect(self.clear_editor)
        self.btn_copy_all.clicked.connect(self.copy_all_editor)
        self.editor.textChanged.connect(self.save_persistent_content)

        self.load_snippets()

        if SnippetsWidget.persistent_html:
            self.editor.setHtml(SnippetsWidget.persistent_html)

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
    def clear_editor(self):
        self.editor.clear()
        SnippetsWidget.persistent_html = ""

    # =====================
    def save_persistent_content(self):
        SnippetsWidget.persistent_html = self.editor.toHtml()