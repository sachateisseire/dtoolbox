from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget
)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DToolbox")
        self.resize(1000, 600)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal (horizontal)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)

        # Sidebar
        self.sidebar = QVBoxLayout()
        self.sidebar.setContentsMargins(10, 10, 10, 10)
        self.sidebar.setSpacing(10)

        sidebar_container = QWidget()
        sidebar_container.setLayout(self.sidebar)
        sidebar_container.setFixedWidth(80)  # ancho inicial minimal

        # Área de contenido (donde van los módulos)
        self.stack = QStackedWidget()

        # Agregar al layout principal
        main_layout.addWidget(sidebar_container)
        main_layout.addWidget(self.stack)

        # ----- BOTONES SIDEBAR -----
        self.btn_snippets = QPushButton("S")
        self.btn_editor = QPushButton("E")

        self.btn_snippets.setFixedHeight(40)
        self.btn_editor.setFixedHeight(40)

        self.sidebar.addWidget(self.btn_snippets)
        self.sidebar.addWidget(self.btn_editor)
        self.sidebar.addStretch()

        # ----- VISTAS (placeholders por ahora) -----
        self.snippets_view = QLabel("Snippets Module")
        self.editor_view = QLabel("Editor Module")

        self.snippets_view.setAlignment(Qt.AlignCenter)
        self.editor_view.setAlignment(Qt.AlignCenter)

        self.stack.addWidget(self.snippets_view)
        self.stack.addWidget(self.editor_view)

        # ----- CONEXIONES -----
        self.btn_snippets.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_editor.clicked.connect(lambda: self.stack.setCurrentIndex(1))