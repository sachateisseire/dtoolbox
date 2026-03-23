import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow,
    QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QStackedWidget
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer

from modules.snippets.widget import SnippetsWidget
from modules.editor.widget import EditorWidget
from core.logger import setup_logger

logger = setup_logger()
logger.info("Aplicación iniciada")


# 🎨 SISTEMA DE TEMA
DARK_THEME = {
    "bg_main": "#0f0f0f",
    "bg_sidebar": "#151515",
    "bg_hover": "#1f1f1f",
    "bg_active": "#262626",
    "text": "#e5e5e5",
    "text_muted": "#888888",
    "accent": "#3b82f6"
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)

        self.theme = DARK_THEME
        self.accent_color = self.theme["accent"]

        self.sidebar_width = 80
        self.module_width = 700

        self.current_index = None
        self.drag_pos = None

        self.setWindowTitle("DGARHC Toolbox")

        # 🔥 CACHE DE ICONOS
        self.icon_cache = {}

        # ----- CENTRAL -----
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet(f"""
            background-color: {self.theme["bg_main"]};
        """)
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget.setLayout(self.main_layout)

        # ----- SIDEBAR -----
        sidebar_widget = QWidget()
        sidebar_widget.setStyleSheet(f"""
            background-color: {self.theme["bg_sidebar"]};
        """)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(12)
        sidebar_widget.setLayout(sidebar_layout)
        sidebar_widget.setFixedWidth(self.sidebar_width)

        # 🟢🟡🔴 BOTONES
        window_controls = QHBoxLayout()
        window_controls.setSpacing(8)
        window_controls.setAlignment(Qt.AlignCenter)

        self.btn_min = QPushButton()
        self.btn_max = QPushButton()
        self.btn_close = QPushButton()

        for btn, color in [
            (self.btn_min, "#27c93f"),
            (self.btn_max, "#ffbd2e"),
            (self.btn_close, "#ff5f56"),
        ]:
            btn.setFixedSize(12, 12)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border-radius: 6px;
                    border: none;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
            window_controls.addWidget(btn)

        sidebar_layout.addLayout(window_controls)

        # ----- ICONOS -----
        self.btn_snippets = QPushButton()
        self.btn_editor = QPushButton()

        self.icon_snippets_path = "assets/icons/file-text.svg"
        self.icon_editor_path = "assets/icons/pen-line.svg"

        for btn, tooltip in [
            (self.btn_snippets, "Snippets"),
            (self.btn_editor, "Editor"),
        ]:
            btn.setFixedSize(48, 48)
            btn.setIconSize(QSize(24, 24))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(tooltip)
            sidebar_layout.addWidget(btn, alignment=Qt.AlignCenter)

        sidebar_layout.addStretch()

        # ----- STACK -----
        self.stack = QStackedWidget()

        self.snippets_widget = SnippetsWidget(self.theme)
        self.editor_widget = EditorWidget(self.theme)

        self.stack.addWidget(self.snippets_widget)
        self.stack.addWidget(self.editor_widget)

        # ----- CONEXIONES -----
        self.btn_snippets.clicked.connect(lambda: self.toggle_module(0))
        self.btn_editor.clicked.connect(lambda: self.toggle_module(1))

        self.btn_close.clicked.connect(self.close)
        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_max.clicked.connect(self.toggle_maximize)

        # ----- LAYOUT -----
        self.main_layout.addWidget(sidebar_widget)
        self.main_layout.addWidget(self.stack)

        # Estado inicial
        self.stack.hide()
        self.set_window_width(self.sidebar_width)

        self.update_buttons()

    # --------- ICONOS (CACHEADOS) ---------

    def get_icon(self, path, color):
        key = f"{path}_{color}"
        if key in self.icon_cache:
            return self.icon_cache[key]

        renderer = QSvgRenderer(path)

        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)

        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), QColor(color))
        painter.end()

        icon = QIcon(pixmap)
        self.icon_cache[key] = icon
        return icon

    # --------- DRAG ---------

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.drag_pos = event.globalPosition().toPoint()

    # --------- MAXIMIZE ---------

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    # --------- TAMAÑO ---------

    def set_window_width(self, width):
        self.setMinimumWidth(width)
        self.setMaximumWidth(width)
        self.resize(width, self.height())

    # --------- TOGGLE ---------

    def toggle_module(self, index):
        if self.current_index == index:
            self.current_index = None
            self.stack.hide()
            self.set_window_width(self.sidebar_width)
        else:
            self.current_index = index
            self.stack.setCurrentIndex(index)
            self.stack.show()
            self.set_window_width(self.sidebar_width + self.module_width)

        self.update_buttons()

    # --------- ESTILO ---------

    def update_buttons(self):
        for btn, idx, path in [
            (self.btn_snippets, 0, self.icon_snippets_path),
            (self.btn_editor, 1, self.icon_editor_path)
        ]:
            if self.current_index == idx:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.theme["bg_active"]};
                        border-radius: 10px;
                        border-left: 3px solid {self.accent_color};
                    }}
                """)
                btn.setIcon(self.get_icon(path, self.accent_color))
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        border-radius: 10px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.theme["bg_hover"]};
                    }}
                """)
                btn.setIcon(self.get_icon(path, self.theme["text_muted"]))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())