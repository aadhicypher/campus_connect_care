#!/usr/bin/env python3
"""
Initial Setup Wizard for Network Configuration
Runs on first admin login
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QStackedWidget, 
    QFrame, QGraphicsDropShadowEffect, QMessageBox,
    QComboBox, QCheckBox, QGridLayout, QScrollArea,
    QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor

from app.core.network_discovery import network_discovery, NetworkInterface
from app.db.connection import get_connection


class SetupWorker(QThread):
    """Background worker for network discovery"""
    progress = Signal(str)
    finished_signal = Signal(bool, str)
    
    def __init__(self, firewall_ip, username, password):
        super().__init__()
        self.firewall_ip = firewall_ip
        self.username = username
        self.password = password
    
    def run(self):
        self.progress.emit("Discovering local network...")
        success, msg = network_discovery.discover_local_network()
        
        if not success:
            self.finished_signal.emit(False, msg)
            return
        
        self.progress.emit("Testing firewall connectivity...")
        if not network_discovery.ping_test(self.firewall_ip):
            self.finished_signal.emit(False, "FIREWALL_UNREACHABLE")
            return
        
        self.progress.emit("Fetching firewall interfaces...")
        success, msg = network_discovery.discover_firewall_interfaces(
            self.firewall_ip, self.username, self.password
        )
        
        if not success:
            self.finished_signal.emit(False, msg)
            return
        
        self.progress.emit("Validating PC in DHCP leases...")
        in_dhcp, dhcp_msg = network_discovery.validate_pc_in_firewall(
            self.firewall_ip, self.username, self.password
        )
        
        self.progress.emit("Saving configuration...")
        network_discovery.save_to_database()
        
        self.finished_signal.emit(True, dhcp_msg)


class SetupWizard(QWidget):
    def __init__(self, on_complete_callback):
        super().__init__()
        self.on_complete = on_complete_callback
        self.current_step = 0
        self.firewall_creds = {}
        self.switch_configs = []
        
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f4f8;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #1e293b;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Main Card
        self.card = QFrame()
        self.card.setFixedWidth(700)
        self.card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(15, 23, 42, 40))
        shadow.setOffset(0, 8)
        self.card.setGraphicsEffect(shadow)
        
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(40, 40, 40, 40)
        self.card_layout.setSpacing(20)
        
        # Header
        self.header_icon = QLabel("◈")
        self.header_icon.setStyleSheet("color: #0ea5e9; font-size: 32px;")
        self.header_icon.setAlignment(Qt.AlignCenter)
        self.card_layout.addWidget(self.header_icon)
        
        self.header_title = QLabel("NETWORK INITIALIZATION")
        self.header_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.header_title.setStyleSheet("color: #0f172a; letter-spacing: 1px;")
        self.header_title.setAlignment(Qt.AlignCenter)
        self.card_layout.addWidget(self.header_title)
        
        self.header_sub = QLabel("Configure your network topology")
        self.header_sub.setFont(QFont("Segoe UI", 11))
        self.header_sub.setStyleSheet("color: #64748b;")
        self.header_sub.setAlignment(Qt.AlignCenter)
        self.card_layout.addWidget(self.header_sub)
        
        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #e2e8f0; margin: 10px 0;")
        self.card_layout.addWidget(sep)
        
        # Content Stack
        self.stack = QStackedWidget()
        self.card_layout.addWidget(self.stack)
        
        # Create Steps
        self.step1_credentials = self.create_step1_credentials()
        self.step2_discovery = self.create_step2_discovery()
        self.step3_validation = self.create_step3_validation()
        self.step4_switches = self.create_step4_switches()
        self.step5_summary = self.create_step5_summary()
        
        self.stack.addWidget(self.step1_credentials)
        self.stack.addWidget(self.step2_discovery)
        self.stack.addWidget(self.step3_validation)
        self.stack.addWidget(self.step4_switches)
        self.stack.addWidget(self.step5_summary)
        
        main_layout.addWidget(self.card)
        self.setLayout(main_layout)
    
    def create_step1_credentials(self) -> QWidget:
        """Step 1: Firewall Credentials"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        # Info Box
        info = QLabel(
            "Enter your pfSense firewall credentials to auto-discover "
            "network topology. The wizard will detect WAN, LAN, and OPT interfaces."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #64748b; padding: 10px; background-color: #f0f9ff; border-radius: 6px;")
        layout.addWidget(info)
        
        # Firewall IP
        ip_label = QLabel("FIREWALL IP ADDRESS")
        ip_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        ip_label.setStyleSheet("color: #475569;")
        layout.addWidget(ip_label)
        
        self.firewall_ip = QLineEdit()
        self.firewall_ip.setPlaceholderText("e.g., 192.168.10.1 or 192.168.99.1")
        self.firewall_ip.setFixedHeight(45)
        self.firewall_ip.setStyleSheet(self._input_style())
        layout.addWidget(self.firewall_ip)
        
        # Username
        user_label = QLabel("ADMIN USERNAME")
        user_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        user_label.setStyleSheet("color: #475569;")
        layout.addWidget(user_label)
        
        self.firewall_user = QLineEdit()
        self.firewall_user.setPlaceholderText("e.g., admin")
        self.firewall_user.setFixedHeight(45)
        self.firewall_user.setStyleSheet(self._input_style())
        self.firewall_user.setText("admin")
        layout.addWidget(self.firewall_user)
        
        # Password
        pass_label = QLabel("ADMIN PASSWORD")
        pass_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        pass_label.setStyleSheet("color: #475569;")
        layout.addWidget(pass_label)
        
        self.firewall_pass = QLineEdit()
        self.firewall_pass.setPlaceholderText("Enter password")
        self.firewall_pass.setEchoMode(QLineEdit.Password)
        self.firewall_pass.setFixedHeight(45)
        self.firewall_pass.setStyleSheet(self._input_style())
        self.firewall_pass.setText("pfsense")
        layout.addWidget(self.firewall_pass)
        
        layout.addStretch()
        
        # Next Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        next_btn = QPushButton("START DISCOVERY →")
        next_btn.setFixedHeight(50)
        next_btn.setFixedWidth(200)
        next_btn.setCursor(Qt.PointingHandCursor)
        next_btn.setStyleSheet(self._primary_button_style())
        next_btn.clicked.connect(self.start_discovery)
        btn_layout.addWidget(next_btn)
        
        layout.addLayout(btn_layout)
        
        return page
    
    def create_step2_discovery(self) -> QWidget:
        """Step 2: Discovery Progress"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        self.progress_label = QLabel("Initializing...")
        self.progress_label.setFont(QFont("Segoe UI", 12))
        self.progress_label.setStyleSheet("color: #0f172a;")
        self.progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #e2e8f0;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #0ea5e9;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        self.progress_detail = QLabel("")
        self.progress_detail.setStyleSheet("color: #64748b; font-family: Consolas;")
        self.progress_detail.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_detail)
        
        layout.addStretch()
        
        return page
    
    def create_step3_validation(self) -> QWidget:
        """Step 3: Show Validation Results"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        self.validation_title = QLabel("Discovery Complete")
        self.validation_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.validation_title.setStyleSheet("color: #0f172a;")
        self.validation_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.validation_title)
        
        # Results Container
        self.results_frame = QFrame()
        self.results_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
                padding: 15px;
            }
        """)
        results_layout = QVBoxLayout(self.results_frame)
        
        self.results_text = QLabel("")
        self.results_text.setWordWrap(True)
        self.results_text.setStyleSheet("color: #475569; font-family: Consolas; line-height: 1.6;")
        results_layout.addWidget(self.results_text)
        
        layout.addWidget(self.results_frame)
        
        # Warning label (for manual IP)
        self.warning_label = QLabel("")
        self.warning_label.setWordWrap(True)
        self.warning_label.setStyleSheet("""
            color: #92400e; 
            background-color: #fef3c7; 
            padding: 15px; 
            border-radius: 6px;
            border-left: 4px solid #f59e0b;
        """)
        self.warning_label.hide()
        layout.addWidget(self.warning_label)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        retry_btn = QPushButton("← RETRY")
        retry_btn.setFixedHeight(45)
        retry_btn.setFixedWidth(120)
        retry_btn.setStyleSheet(self._secondary_button_style())
        retry_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_layout.addWidget(retry_btn)
        
        btn_layout.addStretch()
        
        self.continue_btn = QPushButton("CONTINUE →")
        self.continue_btn.setFixedHeight(45)
        self.continue_btn.setFixedWidth(150)
        self.continue_btn.setStyleSheet(self._primary_button_style())
        self.continue_btn.clicked.connect(self.go_to_switches)
        btn_layout.addWidget(self.continue_btn)
        
        layout.addLayout(btn_layout)
        
        return page
    
    def create_step4_switches(self) -> QWidget:
        """Step 4: Configure Switches for Each Subnet"""
        page = QScrollArea()
        page.setWidgetResizable(True)
        page.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        
        title = QLabel("CONFIGURE MANAGED SWITCHES")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #0f172a;")
        layout.addWidget(title)
        
        desc = QLabel(
            "For each internal subnet (LAN, OPT1, etc.), specify the "
            "management IP of the connected switch, or select 'No Switch'."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #64748b;")
        layout.addWidget(desc)
        
        # Container for subnet configurations
        self.switches_container = QVBoxLayout()
        self.switches_container.setSpacing(15)
        layout.addLayout(self.switches_container)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        back_btn = QPushButton("← BACK")
        back_btn.setFixedHeight(45)
        back_btn.setFixedWidth(120)
        back_btn.setStyleSheet(self._secondary_button_style())
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        btn_layout.addWidget(back_btn)
        
        btn_layout.addStretch()
        
        save_btn = QPushButton("SAVE CONFIGURATION ✓")
        save_btn.setFixedHeight(45)
        save_btn.setFixedWidth(200)
        save_btn.setStyleSheet(self._primary_button_style())
        save_btn.clicked.connect(self.save_switches)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        page.setWidget(container)
        return page
    
    def create_step5_summary(self) -> QWidget:
        """Step 5: Final Summary"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Success Icon
        success_icon = QLabel("✓")
        success_icon.setFont(QFont("Segoe UI", 48))
        success_icon.setStyleSheet("color: #10b981;")
        success_icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(success_icon)
        
        title = QLabel("SETUP COMPLETE")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #0f172a;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.summary_text = QLabel("")
        self.summary_text.setWordWrap(True)
        self.summary_text.setStyleSheet("""
            color: #475569; 
            background-color: #f0fdf4; 
            padding: 20px; 
            border-radius: 8px;
            border: 1px solid #bbf7d0;
            font-family: Consolas;
            line-height: 1.6;
        """)
        layout.addWidget(self.summary_text)
        
        layout.addStretch()
        
        finish_btn = QPushButton("GO TO DASHBOARD →")
        finish_btn.setFixedHeight(50)
        finish_btn.setStyleSheet(self._primary_button_style())
        finish_btn.clicked.connect(self.finish_setup)
        layout.addWidget(finish_btn, alignment=Qt.AlignCenter)
        
        return page
    
    def _input_style(self) -> str:
        return """
            QLineEdit {
                padding: 0 15px;
                font-size: 13px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background-color: #f8fafc;
                color: #0f172a;
                font-family: Consolas;
            }
            QLineEdit:focus {
                border: 2px solid #0ea5e9;
                background-color: white;
            }
        """
    
    def _primary_button_style(self) -> str:
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0ea5e9, stop:1 #0284c7);
                color: white;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0284c7, stop:1 #0369a1);
            }
        """
    
    def _secondary_button_style(self) -> str:
        return """
            QPushButton {
                background-color: transparent;
                color: #64748b;
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #cbd5e1;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                border-color: #94a3b8;
                color: #475569;
            }
        """
    
    def start_discovery(self):
        """Start the discovery process"""
        ip = self.firewall_ip.text().strip()
        user = self.firewall_user.text().strip()
        password = self.firewall_pass.text().strip()
        
        if not all([ip, user, password]):
            QMessageBox.warning(self, "Validation", "Please fill all fields")
            return
        
        self.firewall_creds = {
            'ip': ip,
            'username': user,
            'password': password
        }
        
        self.stack.setCurrentIndex(1)  # Go to progress page
        
        self.worker = SetupWorker(ip, user, password)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished_signal.connect(self.discovery_finished)
        self.worker.start()
    
    def update_progress(self, message: str):
        self.progress_detail.setText(message)
    
    def discovery_finished(self, success: bool, message: str):
        if not success:
            self.show_error(message)
            return
        
        # Show validation results
        self.show_validation_results(message)
        self.stack.setCurrentIndex(2)
    
    def show_error(self, error_code: str):
        """Handle different error codes"""
        error_messages = {
            'NO_GATEWAY': "No default gateway detected.\n\nPlease ensure your PC has network connectivity via DHCP or manual configuration.",
            'NO_IP_ADDRESS': "Could not determine local IP address.",
            'FIREWALL_UNREACHABLE': f"Cannot reach firewall at {self.firewall_creds['ip']}\n\nPlease check:\n• Firewall is powered on\n• Network cable is connected\n• IP address is correct",
            'AUTH_FAILED': "Authentication failed.\n\nPlease check username and password.",
        }
        
        msg = error_messages.get(error_code, f"Error: {error_code}")
        
        QMessageBox.critical(self, "Discovery Failed", msg)
        self.stack.setCurrentIndex(0)
    
    def show_validation_results(self, dhcp_message: str):
        """Display discovery results"""
        info = network_discovery.local_info
        interfaces = network_discovery.firewall_interfaces
        
        # Build results text
        text = f"""LOCAL PC:
  IP: {info.ip_address}
  Gateway: {info.gateway}
  Interface: {info.interface}
  DHCP Mode: {'Yes' if info.is_dhcp else 'No (Static IP)'}

FIREWALL INTERFACES:
"""
        for iface in interfaces:
            text += f"  {iface.interface_type} ({iface.name}): {iface.ip_address} - {iface.subnet_cidr}\n"
        
        text += f"\nDHCP VALIDATION: {dhcp_message}"
        
        self.results_text.setText(text)
        
        # Show warning if manual IP
        if "not found in DHCP" in dhcp_message or not info.is_dhcp:
            self.warning_label.setText(
                "⚠ WARNING: Your PC appears to have a static IP configuration "
                "or is not registered in the firewall's DHCP leases. "
                "Please verify the IP configuration is correct for this network."
            )
            self.warning_label.show()
        else:
            self.warning_label.hide()
    
    def go_to_switches(self):
        """Build switch configuration page"""
        # Clear previous
        while self.switches_container.count():
            item = self.switches_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add config for each non-WAN interface
        self.switch_inputs = {}
        
        for iface in network_discovery.firewall_interfaces:
            if iface.interface_type == 'WAN':
                continue
            
            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 8px;
                    border: 1px solid #e2e8f0;
                    padding: 10px;
                }
            """)
            frame_layout = QVBoxLayout(frame)
            
            # Subnet info
            subnet_label = QLabel(f"{iface.interface_type}: {iface.subnet_cidr}")
            subnet_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
            subnet_label.setStyleSheet("color: #0f172a;")
            frame_layout.addWidget(subnet_label)
            
            # Gateway info
            gw_label = QLabel(f"Gateway: {iface.ip_address}")
            gw_label.setStyleSheet("color: #64748b; font-family: Consolas;")
            frame_layout.addWidget(gw_label)
            
            # Switch IP input
            input_layout = QHBoxLayout()
            
            has_switch = QCheckBox("Has Managed Switch")
            has_switch.setChecked(True)
            has_switch.setStyleSheet("color: #475569;")
            input_layout.addWidget(has_switch)
            
            switch_ip = QLineEdit()
            switch_ip.setPlaceholderText("Switch management IP (e.g., 192.168.10.2)")
            switch_ip.setStyleSheet(self._input_style())
            switch_ip.setFixedHeight(40)
            input_layout.addWidget(switch_ip, stretch=1)
            
            # Enable/disable IP input based on checkbox
            has_switch.toggled.connect(switch_ip.setEnabled)
            
            frame_layout.addLayout(input_layout)
            
            # Credentials (collapsed by default, optional)
            self.switch_inputs[iface.interface_type] = {
                'frame': frame,
                'has_switch': has_switch,
                'ip': switch_ip,
                'subnet_id': iface  # Will map to DB ID later
            }
            
            self.switches_container.addWidget(frame)
        
        self.stack.setCurrentIndex(3)
    
    def save_switches(self):
        """Save switch configurations"""
        configs = []
        
        for iface_type, widgets in self.switch_inputs.items():
            if widgets['has_switch'].isChecked():
                ip = widgets['ip'].text().strip()
                if ip:
                    configs.append({
                        'subnet_type': iface_type,
                        'ip': ip,
                        'username': 'sourav',  # Default from your setup
                        'password': 'exam'
                    })
        
        # Save to database
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # Get interface IDs from database
            cur.execute("SELECT id, interface_type FROM firewall_interfaces")
            id_map = {row[1]: row[0] for row in cur.fetchall()}
            
            for config in configs:
                subnet_id = id_map.get(config['subnet_type'])
                if subnet_id:
                    # Test connectivity first
                    success, sw_type, details = network_discovery.test_switch_connectivity(
                        config['ip'], config['username'], config['password']
                    )
                    
                    cur.execute("""
                        INSERT INTO managed_switches 
                        (subnet_id, switch_ip, switch_type, ssh_username, 
                         ssh_password_encrypted, last_seen)
                        VALUES (%s, %s, %s, %s, %s, NOW())
                    """, (
                        subnet_id,
                        config['ip'],
                        sw_type if success else 'Unknown',
                        config['username'],
                        'ENCRYPTED:' + config['password']  # TODO: Proper encryption
                    ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            self.show_summary()
            self.stack.setCurrentIndex(4)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
    
    def show_summary(self):
        """Show final summary"""
        info = network_discovery.local_info
        interfaces = network_discovery.firewall_interfaces
        
        text = f"""Network configuration saved successfully!

MASTER PC: {info.ip_address}
GATEWAY: {info.gateway}

CONFIGURED SUBNETS:
"""
        for iface in interfaces:
            text += f"  • {iface.interface_type}: {iface.subnet_cidr}\n"
        
        text += "\nYou can modify this configuration later from Settings."
        
        self.summary_text.setText(text)
    
    def finish_setup(self):
        """Complete setup and go to dashboard"""
        self.on_complete()


# For testing
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    wizard = SetupWizard(lambda: print("Setup complete!"))
    wizard.show()
    sys.exit(app.exec())
