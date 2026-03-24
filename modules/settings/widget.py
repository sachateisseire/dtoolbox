from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QColorDialog, QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt


class SettingsWidget(QWidget):
    def __init__(self, app_ref):
        super().__init__()

        self.app = app_ref

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(24)
        self.setLayout(self.main_layout)

        # =====================
        title = QLabel("Configuración")
        title.setObjectName("title")
        self.main_layout.addWidget(title)

        # =====================
        self.appearance_card = self.create_card("Apariencia")
        self.main_layout.addWidget(self.appearance_card)

        app_layout = self.appearance_card.layout()

        # Tema
        theme_label = QLabel("Tema")
        theme_label.setObjectName("sectionLabel")
        app_layout.addWidget(theme_label)

        theme_row = QHBoxLayout()
        theme_row.setSpacing(10)

        self.btn_dark = QPushButton("🌙 Dark")
        self.btn_light = QPushButton("☀ Light")

        for btn, mode in [
            (self.btn_dark, "dark"),
            (self.btn_light, "light")
        ]:
            btn.setMinimumHeight(36)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, m=mode: self.set_theme(m))
            theme_row.addWidget(btn)

        app_layout.addLayout(theme_row)

        # Color
        color_label = QLabel("Color principal")
        color_label.setObjectName("sectionLabel")
        app_layout.addWidget(color_label)

        color_row = QHBoxLayout()
        color_row.setSpacing(10)

        self.color_preview = QLabel()
        self.color_preview.setFixedSize(50, 24)
        self.color_preview.setObjectName("colorPreview")

        self.btn_color = QPushButton("Cambiar")
        self.btn_color.setMinimumHeight(32)
        self.btn_color.clicked.connect(self.change_color)

        color_row.addWidget(self.color_preview)
        color_row.addWidget(self.btn_color)
        color_row.addStretch()

        app_layout.addLayout(color_row)

        # =====================
        self.font_card = self.create_card("Tipografía")
        self.main_layout.addWidget(self.font_card)

        font_layout = self.font_card.layout()

        font_label = QLabel("Tamaño de texto")
        font_label.setObjectName("sectionLabel")
        font_layout.addWidget(font_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_font_small = QPushButton("S")
        self.btn_font_medium = QPushButton("M")
        self.btn_font_large = QPushButton("L")

        self.font_buttons = {
            1: self.btn_font_small,
            2: self.btn_font_medium,
            3: self.btn_font_large
        }

        for btn in self.font_buttons.values():
            btn.setFixedSize(40, 40)
            btn.setCursor(Qt.PointingHandCursor)
            btn_layout.addWidget(btn)

        self.btn_font_small.clicked.connect(lambda: self.change_font_size(1))
        self.btn_font_medium.clicked.connect(lambda: self.change_font_size(2))
        self.btn_font_large.clicked.connect(lambda: self.change_font_size(3))

        font_layout.addLayout(btn_layout)

        self.main_layout.addStretch()

        self.update_ui()

    # =====================
    def create_card(self, title_text):
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        card.setLayout(layout)

        title = QLabel(title_text)
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        return card

    # =====================
    def apply_theme(self, theme):
        self.setStyleSheet(f"""
            QWidget {{
                color: {theme["text"]};
            }}

            QLabel {{
                background: transparent;
            }}

            QLabel#title {{
                font-size: 18px;
                font-weight: bold;
            }}

            QLabel#cardTitle {{
                font-size: 14px;
                font-weight: bold;
            }}

            QLabel#sectionLabel {{
                font-size: 12px;
                color: {theme["text_muted"]};
            }}

            QFrame#card {{
                background-color: {theme["bg_sidebar"]};
                border-radius: 12px;
            }}

            QPushButton {{
                border-radius: 8px;
                padding: 6px;
            }}

            QPushButton:hover {{
                background-color: {theme["bg_hover"]};
            }}

            QLabel#colorPreview {{
                border-radius: 6px;
            }}
        """)

        self.update_ui()

    # =====================
    def update_ui(self):
        theme = self.app.theme

        self.color_preview.setStyleSheet(f"""
            background-color: {self.app.accent_color};
            border-radius: 6px;
        """)

        # Tema
        for btn, mode in [
            (self.btn_dark, "dark"),
            (self.btn_light, "light")
        ]:
            if self.app.theme_mode == mode:
                btn.setStyleSheet(f"""
                    background-color: {theme["bg_active"]};
                    border: 2px solid {theme["accent"]};
                    font-weight: bold;
                """)
            else:
                btn.setStyleSheet("")

        # Font
        for level, btn in self.font_buttons.items():
            if level == self.app.current_font_level:
                btn.setStyleSheet(f"""
                    background-color: {theme["bg_active"]};
                    border: 2px solid {theme["accent"]};
                    font-weight: bold;
                """)
            else:
                btn.setStyleSheet("")

    # =====================
    def set_theme(self, mode):
        if self.app.theme_mode != mode:
            self.app.toggle_theme()
        self.update_ui()

    def change_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.app.set_accent_color(color.name())
            self.update_ui()

    def change_font_size(self, level):
        self.app.set_font_size(level)
        self.update_ui()