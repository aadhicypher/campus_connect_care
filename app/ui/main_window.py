from PySide6.QtWidgets import (
    QWidget, QListWidget, QStackedWidget,
    QHBoxLayout
)

from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.User_management import UserManagementPage
from app.ui.pages.diagnostics_page import DiagnosticsPage
from app.ui.pages.topology_page import TopologyPage
from app.ui.pages.logs_page import LogsPage
from app.ui.pages.change_password_page import ChangePasswordPage


class MainWindow(QWidget):
    def __init__(self, role):
        super().__init__()
        self.setWindowTitle("Campus Connect-Care | Network Admin")
        self.resize(1200, 700)
        self.role = role
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        # Left navigation
        self.menu = QListWidget()
        self.menu.addItems([
            "Dashboard",
            "User Management",
            "Network Diagnostics",
            "Topology",
            "Logs",
            "Change Password"
        ])
        self.menu.setFixedWidth(220)

        # Page container
        self.pages = QStackedWidget()
        self.pages.addWidget(DashboardPage())
        self.pages.addWidget(UserManagementPage())
        self.pages.addWidget(DiagnosticsPage())
        self.pages.addWidget(TopologyPage())
        self.pages.addWidget(LogsPage())
        self.pages.addWidget(ChangePasswordPage())

        self.menu.currentRowChanged.connect(self.pages.setCurrentIndex)

        layout.addWidget(self.menu)
        layout.addWidget(self.pages)
        self.setLayout(layout)