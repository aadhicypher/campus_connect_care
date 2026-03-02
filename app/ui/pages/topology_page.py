from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, 
    QFrame, QHBoxLayout, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor


class TopologyPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignCenter)

        # Info Card
        card = QFrame()
        card.setFixedWidth(600)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                border: 2px dashed #cbd5e1;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(15, 23, 42, 15))
        shadow.setOffset(0, 6)
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(25)

        icon = QLabel("◈")
        icon.setStyleSheet("color: #8b5cf6; font-size: 48px;")
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)

        title = QLabel("TOPOLOGY VISUALIZATION")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #0f172a; letter-spacing: 2px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        status = QLabel("MODULE STATUS: DEVELOPMENT")
        status.setFont(QFont("Consolas", 10))
        status.setStyleSheet("color: #8b5cf6; background-color: #ede9fe; padding: 8px; border-radius: 4px;")
        status.setAlignment(Qt.AlignCenter)
        layout.addWidget(status)

        desc = QLabel(
            "Network topology mapping functionality is currently under development.\n\n"
            "The system will display:\n"
            "• LLDP neighbor discovery\n"
            "• Switch hierarchy visualization\n"
            "• Real-time link status\n"
            "• MAC address table mapping"
        )
        desc.setFont(QFont("Segoe UI", 12))
        desc.setStyleSheet("color: #64748b; line-height: 1.6;")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Placeholder Action Button
        btn = QPushButton("◈ RUN DISCOVERY SCAN")
        btn.setFixedHeight(50)
        btn.setFixedWidth(250)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        btn.clicked.connect(self.run_scan)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

        main_layout.addWidget(card)
        self.setLayout(main_layout)

    def run_scan(self):
        # Placeholder for topology scan
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Scan Initiated", 
            "Topology discovery started...\n\nCheck System Logs for details.")
