from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
import subprocess

class DiagnosticsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("🌐 Network Diagnostics"))

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter IP address")

        btn = QPushButton("Ping")
        btn.clicked.connect(self.ping)

        layout.addWidget(self.ip_input)
        layout.addWidget(btn)
        self.setLayout(layout)

    def ping(self):
        ip = self.ip_input.text().strip()
        if not ip:
            return

        result = subprocess.call(
            ["ping", "-n", "1", ip],
            stdout=subprocess.DEVNULL
        )

        if result == 0:
            QMessageBox.information(self, "Result", f"{ip} is reachable")
        else:
            QMessageBox.warning(self, "Result", f"{ip} is NOT reachable")
