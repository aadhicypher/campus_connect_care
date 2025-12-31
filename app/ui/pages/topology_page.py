from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class TopologyPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🗺️ Network Topology"))
        layout.addWidget(QLabel("Topology visualization coming soon"))
        self.setLayout(layout)
