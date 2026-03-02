from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QFrame, QGridLayout, QGraphicsDropShadowEffect,
    QPushButton, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

from app.core.network_discovery import network_discovery, NetworkDiscovery


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.network_discovery = NetworkDiscovery()
        self.init_ui()
        self.load_network_config()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)
        
        # Header with Edit button
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
        
        title = QLabel("◈ NETWORK TOPOLOGY CONFIGURATION")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #0f172a; letter-spacing: 1px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        edit_btn = QPushButton("EDIT CONFIGURATION")
        edit_btn.setFixedHeight(40)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setStyleSheet("""
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
        edit_btn.clicked.connect(self.edit_configuration)
        header_layout.addWidget(edit_btn)
        
        main_layout.addWidget(header)
        
        # Content Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(15)
        
        scroll.setWidget(self.content_widget)
        main_layout.addWidget(scroll, stretch=1)
        
        self.setLayout(main_layout)
    
    def load_network_config(self):
        """Load and display network configuration from database"""
        # Clear existing
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        success = self.network_discovery.load_from_database()
        
        if not success or not self.network_discovery.local_info:
            # Show setup required message
            self.show_setup_required()
            return
        
        # Display Master PC Info
        self.add_section_header("MASTER PC")
        info = self.network_discovery.local_info
        self.add_info_card(
            "Local Machine",
            f"IP Address: {info.ip_address}\n"
            f"Interface: {info.interface}\n"
            f"Gateway: {info.gateway}\n"
            f"DHCP Mode: {'Automatic' if info.is_dhcp else 'Static IP'}"
        )
        
        # Display Firewall Info
        self.add_section_header("FIREWALL")
        for iface in self.network_discovery.firewall_interfaces:
            if iface.interface_type == "WAN":
                icon = "🌐"
                desc = "Internet Connection"
            else:
                icon = "🔌"
                desc = "Internal Network"
            
            self.add_interface_card(iface, icon, desc)
        
        # Display Switches
        self.add_section_header("MANAGED SWITCHES")
        self.load_switches()
        
        self.content_layout.addStretch()
    
    def add_section_header(self, title: str):
        """Add a section header"""
        label = QLabel(title)
        label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        label.setStyleSheet("color: #64748b; margin-top: 10px;")
        self.content_layout.addWidget(label)
    
    def add_info_card(self, title: str, content: str):
        """Add an information card"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
                padding: 5px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title_label.setStyleSheet("color: #0f172a;")
        layout.addWidget(title_label)
        
        content_label = QLabel(content)
        content_label.setStyleSheet("color: #475569; font-family: Consolas; line-height: 1.6;")
        layout.addWidget(content_label)
        
        self.content_layout.addWidget(card)
    
    def add_interface_card(self, iface, icon: str, description: str):
        """Add a firewall interface card"""
        card = QFrame()
        
        # Color coding
        if iface.interface_type == "WAN":
            border_color = "#0ea5e9"  # Blue
        elif iface.interface_type == "LAN":
            border_color = "#10b981"  # Green
        else:
            border_color = "#8b5cf6"  # Purple
        
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                border-left: 4px solid {border_color};
                border-top: 1px solid #e2e8f0;
                border-right: 1px solid #e2e8f0;
                border-bottom: 1px solid #e2e8f0;
            }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Icon and type
        left = QVBoxLayout()
        type_label = QLabel(f"{icon} {iface.interface_type}")
        type_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        type_label.setStyleSheet(f"color: {border_color};")
        left.addWidget(type_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #64748b; font-size: 11px;")
        left.addWidget(desc_label)
        
        layout.addLayout(left)
        layout.addStretch()
        
        # IP details
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignRight)
        
        ip_label = QLabel(iface.ip_address)
        ip_label.setFont(QFont("Consolas", 11, QFont.Bold))
        ip_label.setStyleSheet("color: #0f172a;")
        right.addWidget(ip_label)
        
        cidr_label = QLabel(iface.subnet_cidr)
        cidr_label.setStyleSheet("color: #64748b; font-family: Consolas;")
        right.addWidget(cidr_label)
        
        dhcp_label = QLabel("DHCP: " + ("✓" if iface.is_dhcp_enabled else "✗"))
        dhcp_label.setStyleSheet("color: #64748b;")
        right.addWidget(dhcp_label)
        
        layout.addLayout(right)
        
        self.content_layout.addWidget(card)
    
    def load_switches(self):
        """Load switches from database"""
        try:
            from app.db.connection import get_connection
            conn = get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT ms.switch_ip, ms.switch_type, ms.last_seen,
                       fi.interface_type, fi.subnet_cidr
                FROM managed_switches ms
                JOIN firewall_interfaces fi ON ms.subnet_id = fi.id
                ORDER BY fi.interface_type
            """)
            
            rows = cur.fetchall()
            cur.close()
            conn.close()
            
            if not rows:
                self.add_info_card(
                    "No Switches Configured",
                    "No managed switches have been configured for the internal subnets.\n"
                    "Click 'Edit Configuration' to add switches."
                )
                return
            
            for row in rows:
                switch_ip, switch_type, last_seen, iface_type, subnet = row
                self.add_switch_card(switch_ip, switch_type, last_seen, iface_type, subnet)
                
        except Exception as e:
            self.add_info_card("Error", f"Could not load switches: {str(e)}")
    
    def add_switch_card(self, ip: str, sw_type: str, last_seen, iface_type: str, subnet: str):
        """Add a switch information card"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #f0fdf4;
                border-radius: 8px;
                border: 1px solid #bbf7d0;
                padding: 5px;
            }
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        
        left = QVBoxLayout()
        
        title = QLabel(f"🖧 {sw_type}")
        title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title.setStyleSheet("color: #15803d;")
        left.addWidget(title)
        
        subnet_label = QLabel(f"Connected to: {iface_type} ({subnet})")
        subnet_label.setStyleSheet("color: #64748b;")
        left.addWidget(subnet_label)
        
        layout.addLayout(left)
        layout.addStretch()
        
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignRight)
        
        ip_label = QLabel(ip)
        ip_label.setFont(QFont("Consolas", 11, QFont.Bold))
        ip_label.setStyleSheet("color: #15803d;")
        right.addWidget(ip_label)
        
        status = QLabel("● Online" if last_seen else "● Unknown")
        status.setStyleSheet("color: #22c55e;" if last_seen else "color: #94a3b8;")
        right.addWidget(status)
        
        layout.addLayout(right)
        
        self.content_layout.addWidget(card)
    
    def show_setup_required(self):
        """Show message when setup is not complete"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #fef2f2;
                border-radius: 12px;
                border: 2px dashed #fecaca;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        icon = QLabel("⚠")
        icon.setFont(QFont("Segoe UI", 48))
        icon.setStyleSheet("color: #ef4444;")
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)
        
        title = QLabel("Network Setup Required")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #991b1b;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        desc = QLabel(
            "The network topology has not been configured yet. "
            "Please complete the initial setup to discover your firewall and switches."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #7f1d1d;")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        self.content_layout.addWidget(card)
    
    def edit_configuration(self):
        """Open setup wizard to reconfigure"""
        from PySide6.QtWidgets import QDialog
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Network Configuration")
        dialog.setMinimumSize(800, 700)
        
        from app.ui.pages.setup_wizard import SetupWizard
        wizard = SetupWizard(lambda: dialog.accept())
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(wizard)
        
        dialog.exec()
        
        # Reload after edit
        self.load_network_config()
