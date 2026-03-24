from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QColorDialog, QHBoxLayout
)
from PySide6.QtCore import Qt


class SettingsWidget(QWidget):
    def __init__(self, app_ref):
        super().__init__()

        self.app = app_ref

        layout = QVBoxLayout()
        self.setLayout(layout)

        # =====================
        title = QLabel("Configuración")
        layout.addWidget(title)

        # =====================
        # 🌗 TEMA
        self.btn_theme = QPushButton("Cambiar tema (Dark / Light)")
        self.btn_theme.clicked.connect(self.toggle_theme)
        layout.addWidget(self.btn_theme)

        # =====================
        # 🎨 COLOR
        self.btn_color = QPushButton("Cambiar color principal")
        self.btn_color.clicked.connect(self.change_color)
        layout.addWidget(self.btn_color)

        # =====================
        # 🔠 TAMAÑO TEXTO (3 niveles)
        self.label_font = QLabel("Tamaño de texto")
        layout.addWidget(self.label_font)

        btn_layout = QHBoxLayout()

        self.btn_font_small = QPushButton("1")
        self.btn_font_medium = QPushButton("2")
        self.btn_font_large = QPushButton("3")

        for btn, level in [
            (self.btn_font_small, 1),
            (self.btn_font_medium, 2),
            (self.btn_font_large, 3),
        ]:
            btn.setFixedWidth(40)
            btn.clicked.connect(lambda _, l=level: self.change_font_size(l))
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)

        layout.addStretch()

    # =====================
    def toggle_theme(self):
        self.app.toggle_theme()

    def change_color(self):
        color = QColorDialog.getColor()

        if color.isValid():
            self.app.set_accent_color(color.name())

    def change_font_size(self, level):
        self.app.set_font_size(level)