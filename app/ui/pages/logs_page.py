from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class LogsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🧾 System Logs"))
        layout.addWidget(QLabel("User sessions and events"))
        self.setLayout(layout)
