from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QTextEdit, 
    QPushButton, QHBoxLayout, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor


class LogsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        # Header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(15, 23, 42, 25))
        shadow.setOffset(0, 4)
        header.setGraphicsEffect(shadow)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(25, 20, 25, 20)

        title = QLabel("◈ SYSTEM LOGS")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #0f172a;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        refresh_btn = QPushButton("REFRESH")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #0ea5e9;
                color: white;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #0284c7;
            }
        """)
        refresh_btn.clicked.connect(self.load_logs)
        header_layout.addWidget(refresh_btn)

        main_layout.addWidget(header)

        # Log Console
        console_card = QFrame()
        console_card.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border-radius: 12px;
                border: 1px solid #334155;
            }
        """)
        
        console_layout = QVBoxLayout(console_card)
        console_layout.setContentsMargins(20, 20, 20, 20)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 10))
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: #cbd5e1;
                border: none;
                line-height: 1.6;
            }
        """)
        console_layout.addWidget(self.log_display)

        main_layout.addWidget(console_card, stretch=1)
        self.setLayout(main_layout)

        # Load initial logs
        self.load_logs()

    def load_logs(self):
        # Sample logs - replace with database query
        logs = """[2025-01-30 14:32:01] ◈ INFO: System initialization complete
[2025-01-30 14:32:05] ◈ INFO: Database connection established (campusdb)
[2025-01-30 14:35:12] ● AUTH: User 'netadmin_1' authenticated successfully
[2025-01-30 14:35:15] ◈ INFO: Session created (ID: 1024)
[2025-01-30 14:42:33] ⚠ WARN: SNMP timeout on device 192.168.1.5
[2025-01-30 14:45:01] ◈ INFO: Topology scan initiated
[2025-01-30 14:45:12] ◈ INFO: Scan complete - 24 devices discovered
[2025-01-30 15:01:45] ● AUTH: User 'itsupport_03' login attempt failed
[2025-01-30 15:02:12] ◈ INFO: Password recovery email dispatched"""
        
        # Apply color formatting
        formatted = logs.replace("◈ INFO:", "<span style='color: #0ea5e9;'>◈ INFO:</span>")
        formatted = formatted.replace("● AUTH:", "<span style='color: #10b981;'>● AUTH:</span>")
        formatted = formatted.replace("⚠ WARN:", "<span style='color: #f59e0b;'>⚠ WARN:</span>")
        formatted = formatted.replace("login attempt failed", "<span style='color: #ef4444;'>login attempt failed</span>")
        
        self.log_display.setHtml(f"<pre>{formatted}</pre>")
