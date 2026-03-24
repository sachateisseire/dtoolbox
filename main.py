import sys
import os

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
from modules.pdf_merge.widget import PDFMergeWidget
from modules.settings.widget import SettingsWidget

from core.snippets_manager import SnippetsManager
from core.snippets_service import SnippetsService


DARK_THEME = {
    "bg_main": "#0f0f0f",
    "bg_sidebar": "#151515",
    "bg_hover": "#1f1f1f",
    "bg_active": "#262626",
    "text": "#e5e5e5",
    "text_muted": "#888888",
    "accent": "#3b82f6"
}

LIGHT_THEME = {
    "bg_main": "#f5f5f5",
    "bg_sidebar": "#ffffff",
    "bg_hover": "#e5e5e5",
    "bg_active": "#dcdcdc",
    "text": "#111111",
    "text_muted": "#555555",
    "accent": "#3b82f6"
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)

        self.theme_mode = "dark"
        self.theme = DARK_THEME.copy()

        self.sidebar_width = 80
        self.module_width = 700

        self.current_index = None
        self.drag_pos = None

        self.icon_cache = {}

        self.manager = SnippetsManager()
        self.service = SnippetsService(self.manager)

        # =====================
        # CENTRAL
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget.setLayout(self.main_layout)

        # =====================
        # SIDEBAR
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(self.sidebar_width)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(12)
        self.sidebar.setLayout(sidebar_layout)

        # 🔴🟡🟢 BOTONES SISTEMA
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

        # =====================
        # BOTONES
        self.btn_snippets = QPushButton()
        self.btn_editor = QPushButton()
        self.btn_pdf = QPushButton()
        self.btn_settings = QPushButton()

        self.icon_snippets_path = "assets/icons/file-text.svg"
        self.icon_editor_path = "assets/icons/pen-line.svg"
        self.icon_pdf_path = "assets/icons/file-stack.svg"
        self.icon_settings_path = "assets/icons/settings.svg"

        for btn, tip in [
            (self.btn_snippets, "Snippets"),
            (self.btn_editor, "Editor"),
            (self.btn_pdf, "PDF Merge"),
        ]:
            btn.setFixedSize(48, 48)
            btn.setIconSize(QSize(24, 24))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(tip)
            sidebar_layout.addWidget(btn, alignment=Qt.AlignCenter)

        sidebar_layout.addStretch()

        self.btn_settings.setFixedSize(48, 48)
        self.btn_settings.setIconSize(QSize(24, 24))
        self.btn_settings.setToolTip("Configuración")
        sidebar_layout.addWidget(self.btn_settings, alignment=Qt.AlignCenter)

        # =====================
        # STACK
        self.stack = QStackedWidget()

        self.snippets = SnippetsWidget(self.theme, self.service)
        self.editor = EditorWidget(self.theme, self.service)
        self.pdf = PDFMergeWidget(self.theme)
        self.settings = SettingsWidget(self)

        self.stack.addWidget(self.snippets)
        self.stack.addWidget(self.editor)
        self.stack.addWidget(self.pdf)
        self.stack.addWidget(self.settings)

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.stack)

        self.stack.hide()
        self.set_window_width(self.sidebar_width)

        # =====================
        # CONEXIONES
        self.btn_snippets.clicked.connect(lambda: self.toggle_module(0))
        self.btn_editor.clicked.connect(lambda: self.toggle_module(1))
        self.btn_pdf.clicked.connect(lambda: self.toggle_module(2))
        self.btn_settings.clicked.connect(lambda: self.toggle_module(3))

        self.btn_close.clicked.connect(self.close)
        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_max.clicked.connect(self.toggle_maximize)

        # =====================
        self.apply_theme()
        self.update_buttons()

    # =====================
    def get_icon(self, path, color):
        if not os.path.exists(path):
            return QIcon()

        try:
            renderer = QSvgRenderer(path)
            if not renderer.isValid():
                return QIcon()

            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.transparent)

            painter = QPainter(pixmap)
            renderer.render(painter)

            if self.theme_mode == "light":
                color = "#000000"

            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(pixmap.rect(), QColor(color))
            painter.end()

            return QIcon(pixmap)

        except:
            return QIcon()

    # =====================
    def apply_theme(self):
        self.central_widget.setStyleSheet(f"""
            background-color: {self.theme["bg_main"]};
            color: {self.theme["text"]};
        """)

        self.sidebar.setStyleSheet(f"""
            background-color: {self.theme["bg_sidebar"]};
        """)

        for widget in [self.snippets, self.editor, self.pdf]:
            if hasattr(widget, "apply_theme"):
                widget.apply_theme(self.theme)

    # =====================
    def toggle_theme(self):
        if self.theme_mode == "dark":
            self.theme_mode = "light"
            self.theme = LIGHT_THEME.copy()
        else:
            self.theme_mode = "dark"
            self.theme = DARK_THEME.copy()

        self.apply_theme()
        self.update_buttons()

    def set_accent_color(self, color):
        self.theme["accent"] = color
        self.update_buttons()

    # 🔥 NUEVO SISTEMA DE NIVELES
    def set_font_size(self, level):
        sizes = {
            1: 12,
            2: 14,
            3: 16
        }

        size = sizes.get(level, 12)

        app = QApplication.instance()
        font = app.font()
        font.setPointSize(size)
        app.setFont(font)

        self.repaint()
        for widget in [self.snippets, self.editor, self.pdf]:
            widget.update()

    # =====================
    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def set_window_width(self, width):
        self.setMinimumWidth(width)
        self.setMaximumWidth(width)
        self.resize(width, self.height())

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

    # =====================
    def update_buttons(self):
        icon_color_inactive = "#000000" if self.theme_mode == "light" else self.theme["text_muted"]

        for btn, idx, path in [
            (self.btn_snippets, 0, self.icon_snippets_path),
            (self.btn_editor, 1, self.icon_editor_path),
            (self.btn_pdf, 2, self.icon_pdf_path),
            (self.btn_settings, 3, self.icon_settings_path),
        ]:
            if self.current_index == idx:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.theme["bg_active"]};
                        border-radius: 10px;
                        border-left: 3px solid {self.theme["accent"]};
                    }}
                """)
                btn.setIcon(self.get_icon(path, self.theme["accent"]))
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
                btn.setIcon(self.get_icon(path, icon_color_inactive))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())