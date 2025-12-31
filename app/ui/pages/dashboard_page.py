from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("📊 Network Admin Dashboard"))
        layout.addWidget(QLabel("✔ System running"))
        layout.addWidget(QLabel("✔ Database connected"))
        layout.addWidget(QLabel("✔ Admin privileges active"))

        self.setLayout(layout)
