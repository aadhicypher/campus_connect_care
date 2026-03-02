from PySide6.QtWidgets import (
    QWidget, QListWidget, QStackedWidget,
    QHBoxLayout, QVBoxLayout, QLabel, QFrame,
    QGraphicsDropShadowEffect, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor

from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.User_management import UserManagementPage
from app.ui.pages.diagnostics_page import DiagnosticsPage
from app.ui.pages.topology_page import TopologyPage
from app.ui.pages.logs_page import LogsPage
from app.ui.pages.change_password_page import ChangePasswordPage


class MainWindow(QWidget):
    def __init__(self, role):
        super().__init__()
        self.setWindowTitle("Campus Connect-Care | System Diagnostics")
        # Smaller initial size for VMs
        self.resize(1280, 800)
        self.setMinimumSize(1024, 700)
        self.role = role
        
        # Global styling - Optimized for VM displays
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f4f8;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #1e293b;
            }
            QFrame {
                border: none;
            }
            /* Scrollbar styling for VMs */
            QScrollBar:vertical {
                width: 12px;
                background: #f1f5f9;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
        """)
        
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # LEFT SIDEBAR - Narrower for VMs
        sidebar = QFrame()
        sidebar.setFixedWidth(240)  # Reduced from 280
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border-right: 3px solid #0ea5e9;
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 15)
        sidebar_layout.setSpacing(0)

        # System Header - Compact
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #0f172a; border-bottom: 2px solid #334155;")
        header_frame.setFixedHeight(90)  # Reduced from 100
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 15, 15, 15)
        header_layout.setSpacing(5)
        
        sys_icon = QLabel("◈")
        sys_icon.setStyleSheet("color: #0ea5e9; font-size: 20px;")
        sys_icon.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(sys_icon)
        
        sys_title = QLabel("CAMPUS CONNECT")
        sys_title.setFont(QFont("Segoe UI", 12, QFont.Bold))  # Smaller font
        sys_title.setStyleSheet("color: #f8fafc; letter-spacing: 1px;")
        sys_title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(sys_title)
        
        sys_ver = QLabel("DIAGNOSTIC v2.0")
        sys_ver.setFont(QFont("Consolas", 7))
        sys_ver.setStyleSheet("color: #64748b;")
        sys_ver.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(sys_ver)
        
        sidebar_layout.addWidget(header_frame)

        # Navigation Menu - Compact
        self.menu = QListWidget()
        self.menu.setFont(QFont("Segoe UI", 10))  # Smaller font
        self.menu.setSpacing(3)  # Reduced spacing
        self.menu.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                padding: 10px 5px 10px 5px;
                outline: none;
            }
            QListWidget::item {
                color: #94a3b8;
                padding: 12px 15px;  /* Reduced padding */
                border-radius: 6px;
                margin: 2px 4px;
                border-left: 3px solid transparent;
            }
            QListWidget::item:hover {
                background-color: #334155;
                color: #e2e8f0;
                border-left: 3px solid #64748b;
            }
            QListWidget::item:selected {
                background-color: #0ea5e9;
                color: white;
                border-left: 3px solid #38bdf8;
                font-weight: bold;
            }
        """)
        
        # Menu items
        menu_items = [
            "◈ DASHBOARD",
            "◈ USER MGMT",  # Shortened
            "◈ NETWORK DIAG",
            "◈ TOPOLOGY",
            "◈ LOGS",
            "◈ SECURITY"
        ]
        self.menu.addItems(menu_items)
        self.menu.setCurrentRow(0)
        sidebar_layout.addWidget(self.menu)

        # Bottom Status - Compact
        sidebar_layout.addStretch()
        
        status_frame = QFrame()
        status_frame.setStyleSheet("background-color: #0f172a; border-top: 1px solid #334155;")
        status_frame.setFixedHeight(70)  # Reduced from 80
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(15, 10, 15, 10)
        
        role_label = QLabel(f"ROLE: {self.role.upper()}")
        role_label.setFont(QFont("Consolas", 8, QFont.Bold))
        role_label.setStyleSheet("color: #0ea5e9;")
        status_layout.addWidget(role_label)
        
        status_text = QLabel("● ONLINE")
        status_text.setFont(QFont("Consolas", 7))
        status_text.setStyleSheet("color: #10b981;")
        status_layout.addWidget(status_text)
        
        sidebar_layout.addWidget(status_frame)

        # MAIN CONTENT AREA with Scroll Capability
        content_scroll = QScrollArea()
        content_scroll.setWidgetResizable(True)
        content_scroll.setStyleSheet("QScrollArea { border: none; background-color: #f0f4f8; }")
        
        content_container = QWidget()
        content_container.setStyleSheet("background-color: #f0f4f8;")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)  # Reduced margins
        content_layout.setSpacing(15)  # Reduced spacing

        # Top Bar - Compact
        top_bar = QFrame()
        top_bar.setFixedHeight(50)  # Reduced from 60
        top_bar.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)  # Softer shadow
        shadow.setColor(QColor(15, 23, 42, 30))
        shadow.setOffset(0, 2)
        top_bar.setGraphicsEffect(shadow)
        
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(15, 10, 15, 10)  # Compact
        
        self.page_title = QLabel("SYSTEM DASHBOARD")
        self.page_title.setFont(QFont("Segoe UI", 14, QFont.Bold))  # Smaller
        self.page_title.setStyleSheet("color: #0f172a; letter-spacing: 1px;")
        top_layout.addWidget(self.page_title)
        
        top_layout.addStretch()
        
        datetime_label = QLabel("▼ SESSION ACTIVE")
        datetime_label.setFont(QFont("Consolas", 9))
        datetime_label.setStyleSheet("color: #64748b;")
        top_layout.addWidget(datetime_label)
        
        content_layout.addWidget(top_bar)

        # Pages Stack
        self.pages = QStackedWidget()
        self.pages.setStyleSheet("QStackedWidget { background-color: transparent; }")
        
        # Initialize pages with size policies for VM
        self.dashboard = DashboardPage()
        self.users = UserManagementPage()
        self.diagnostics = DiagnosticsPage()
        self.topology = TopologyPage()
        self.logs = LogsPage()
        self.password = ChangePasswordPage()
        
        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.users)
        self.pages.addWidget(self.diagnostics)
        self.pages.addWidget(self.topology)
        self.pages.addWidget(self.logs)
        self.pages.addWidget(self.password)

        self.menu.currentRowChanged.connect(self.change_page)
        
        content_layout.addWidget(self.pages, stretch=1)
        
        content_scroll.setWidget(content_container)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_scroll, stretch=1)
        self.setLayout(main_layout)

    def change_page(self, index):
        self.pages.setCurrentIndex(index)
        titles = [
            "SYSTEM DASHBOARD",
            "USER MANAGEMENT",
            "NETWORK DIAGNOSTICS", 
            "TOPOLOGY MAP",
            "SYSTEM LOGS",
            "SECURITY SETTINGS"
        ]
        self.page_title.setText(titles[index])
