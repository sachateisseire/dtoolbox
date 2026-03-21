import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow,
    QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel
)

from modules.snippets.widget import SnippetsWidget
from modules.editor.widget import EditorWidget
from core.logger import setup_logger

logger = setup_logger()
logger.info("Aplicación iniciada")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DGARHC Toolbox")
        self.resize(900, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # SIDEBAR
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar_widget.setLayout(sidebar_layout)

        btn_snippets = QPushButton("Snippets")
        btn_editor = QPushButton("Editor")

        btn_snippets.clicked.connect(self.show_snippets)
        btn_editor.clicked.connect(self.show_editor)

        sidebar_layout.addWidget(btn_snippets)
        sidebar_layout.addWidget(btn_editor)
        sidebar_layout.addStretch()

        # CONTENIDO
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)

        self.set_content(QLabel("Seleccioná un módulo"))

        main_layout.addWidget(sidebar_widget, 1)
        main_layout.addWidget(self.content_widget, 4)

    def set_content(self, widget):
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.content_layout.addWidget(widget)

    def show_snippets(self):
        self.set_content(SnippetsWidget())

    def show_editor(self):
        self.set_content(EditorWidget())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())