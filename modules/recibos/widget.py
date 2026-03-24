from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QTextEdit, QHBoxLayout, QSpinBox
)
from PySide6.QtCore import Qt, QThread, Signal

import asyncio
from modules.recibos.service import RecibosService


# =====================
class RecibosWorker(QThread):
    log_signal = Signal(str)
    finished_signal = Signal()

    def __init__(self, year, m_from, m_to):
        super().__init__()
        self.year = year
        self.m_from = m_from
        self.m_to = m_to

        self.service = RecibosService()

    def run(self):
        asyncio.run(self.main())

    async def main(self):
        try:
            await self.service.run(
                self.year,
                self.m_from,
                self.m_to,
                self.log_signal.emit
            )
        except Exception as e:
            self.log_signal.emit(f"❌ Error: {str(e)}")

        self.finished_signal.emit()


# =====================
class RecibosWidget(QWidget):
    def __init__(self, theme):
        super().__init__()

        self.theme = theme

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        # =====================
        title = QLabel("Descarga de Recibos")
        layout.addWidget(title)

        # =====================
        range_layout = QHBoxLayout()

        self.year_input = QSpinBox()
        self.year_input.setRange(2000, 2100)
        self.year_input.setValue(2024)

        self.from_input = QSpinBox()
        self.from_input.setRange(1, 12)
        self.from_input.setValue(1)

        self.to_input = QSpinBox()
        self.to_input.setRange(1, 12)
        self.to_input.setValue(12)

        range_layout.addWidget(QLabel("Año"))
        range_layout.addWidget(self.year_input)
        range_layout.addWidget(QLabel("Desde"))
        range_layout.addWidget(self.from_input)
        range_layout.addWidget(QLabel("Hasta"))
        range_layout.addWidget(self.to_input)

        layout.addLayout(range_layout)

        # =====================
        self.btn_start = QPushButton("Abrir navegador")
        self.btn_start.clicked.connect(self.start_process)
        layout.addWidget(self.btn_start)

        # 🔥 NUEVO
        self.btn_continue = QPushButton("Ya me logueé / continuar")
        self.btn_continue.clicked.connect(self.continue_process)
        self.btn_continue.setEnabled(False)
        layout.addWidget(self.btn_continue)

        # =====================
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        layout.addStretch()

        self.worker = None

    # =====================
    def start_process(self):
        year = self.year_input.value()
        m_from = self.from_input.value()
        m_to = self.to_input.value()

        self.log.clear()
        self.log.append("🚀 Abriendo navegador...")

        self.btn_start.setEnabled(False)
        self.btn_continue.setEnabled(True)

        self.worker = RecibosWorker(year, m_from, m_to)
        self.worker.log_signal.connect(self.log.append)
        self.worker.finished_signal.connect(self.finish)

        self.worker.start()

    def continue_process(self):
        if self.worker and self.worker.service:
            self.worker.service.set_ready()
            self.log.append("✅ Continuando proceso...")

    def finish(self):
        self.btn_start.setEnabled(True)
        self.btn_continue.setEnabled(False)

    # =====================
    def apply_theme(self, theme):
        self.theme = theme

        self.setStyleSheet(f"""
            QWidget {{
                color: {theme["text"]};
            }}

            QPushButton {{
                background-color: {theme["bg_active"]};
                border-radius: 8px;
                padding: 8px;
            }}

            QPushButton:hover {{
                background-color: {theme["accent"]};
            }}

            QTextEdit {{
                background-color: {theme["bg_sidebar"]};
                border-radius: 8px;
            }}
        """)