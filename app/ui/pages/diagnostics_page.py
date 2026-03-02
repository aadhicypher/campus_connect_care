from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QHBoxLayout, QFrame,
    QGraphicsDropShadowEffect, QGridLayout, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
import subprocess
import socket


class DiagnosticsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        # Control Panel
        control_card = QFrame()
        control_card.setStyleSheet("""
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
        control_card.setGraphicsEffect(shadow)

        control_layout = QVBoxLayout(control_card)
        control_layout.setContentsMargins(30, 25, 30, 25)
        control_layout.setSpacing(15)

        # Header
        header = QLabel("◈ NETWORK DIAGNOSTIC TOOLS")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.setStyleSheet("color: #0f172a; letter-spacing: 1px;")
        control_layout.addWidget(header)

        # Tool Selection Grid
        tools_grid = QGridLayout()
        tools_grid.setSpacing(15)

        # Target Input
        target_label = QLabel("TARGET NODE / IP ADDRESS")
        target_label.setFont(QFont("Consolas", 9))
        target_label.setStyleSheet("color: #64748b;")
        tools_grid.addWidget(target_label, 0, 0)

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("e.g., 192.168.1.1 or core-switch.local")
        self.target_input.setFixedHeight(45)
        self.target_input.setStyleSheet("""
            QLineEdit {
                padding: 0 15px;
                font-size: 14px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background-color: #f8fafc;
                font-family: 'Consolas', monospace;
                color: #0f172a;
            }
            QLineEdit:focus {
                border: 2px solid #0ea5e9;
                background-color: white;
            }
        """)
        tools_grid.addWidget(self.target_input, 1, 0)

        # Tool Type Selection
        tool_label = QLabel("DIAGNOSTIC MODULE")
        tool_label.setFont(QFont("Consolas", 9))
        tool_label.setStyleSheet("color: #64748b;")
        tools_grid.addWidget(tool_label, 0, 1)

        self.tool_combo = QComboBox()
        self.tool_combo.addItems(["ICMP Echo (Ping)", "TCP Port Scan", "DNS Lookup"])
        self.tool_combo.setFixedHeight(45)
        self.tool_combo.setStyleSheet("""
            QComboBox {
                padding: 0 15px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background-color: #f8fafc;
                font-size: 13px;
            }
            QComboBox:focus {
                border: 2px solid #0ea5e9;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
        """)
        tools_grid.addWidget(self.tool_combo, 1, 1)

        control_layout.addLayout(tools_grid)

        # Execute Button Row
        btn_layout = QHBoxLayout()
        
        self.execute_btn = QPushButton("◈ EXECUTE DIAGNOSTIC")
        self.execute_btn.setFixedHeight(50)
        self.execute_btn.setCursor(Qt.PointingHandCursor)
        self.execute_btn.setStyleSheet("""
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
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0369a1, stop:1 #075985);
            }
            QPushButton:disabled {
                background-color: #cbd5e1;
                color: #64748b;
            }
        """)
        self.execute_btn.clicked.connect(self.run_diagnostic)
        btn_layout.addWidget(self.execute_btn)

        self.clear_btn = QPushButton("CLEAR CONSOLE")
        self.clear_btn.setFixedHeight(50)
        self.clear_btn.setFixedWidth(150)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setStyleSheet("""
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
        """)
        self.clear_btn.clicked.connect(self.clear_console)
        btn_layout.addWidget(self.clear_btn)

        control_layout.addLayout(btn_layout)

        main_layout.addWidget(control_card)

        # Results Console
        console_card = QFrame()
        console_card.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border-radius: 12px;
                border: 2px solid #334155;
            }
        """)
        console_layout = QVBoxLayout(console_card)
        console_layout.setContentsMargins(20, 20, 20, 20)

        console_header = QHBoxLayout()
        console_title = QLabel("◈ TERMINAL OUTPUT")
        console_title.setFont(QFont("Consolas", 10, QFont.Bold))
        console_title.setStyleSheet("color: #0ea5e9;")
        console_header.addWidget(console_title)

        console_status = QLabel("READY")
        console_status.setFont(QFont("Consolas", 9))
        console_status.setStyleSheet("color: #10b981;")
        console_header.addWidget(console_status, alignment=Qt.AlignRight)
        console_layout.addLayout(console_header)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 11))
        self.console.setStyleSheet("""
            QTextEdit {
                background-color: #1e293b;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 15px;
                line-height: 1.5;
            }
        """)
        self.console.setPlaceholderText("""Campus Connect-Care Diagnostic Console v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: System Ready
Awaiting command input...
        """)
        console_layout.addWidget(self.console)

        main_layout.addWidget(console_card, stretch=1)
        self.setLayout(main_layout)

    def run_diagnostic(self):
        target = self.target_input.text().strip()
        tool = self.tool_combo.currentText()
        
        if not target:
            self.log_output("ERROR: No target specified.", error=True)
            return

        self.execute_btn.setEnabled(False)
        self.log_output(f"\n{'='*50}")
        self.log_output(f"INITIATING: {tool}")
        self.log_output(f"TARGET: {target}")
        self.log_output(f"TIMESTAMP: 2025-01-30 14:35:22")
        self.log_output(f"{'='*50}\n")

        # Run without threading (simpler)
        if "Ping" in tool:
            self.run_ping(target)
        elif "Port Scan" in tool:
            self.port_scan(target)
        else:
            self.log_output(f"DNS Lookup simulation for: {target}")
            self.log_output(f"  Resolved: {target} -> 192.168.1.100")
            self.execute_btn.setEnabled(True)

    def run_ping(self, target):
        try:
            param = '-n' if subprocess.os.name == 'nt' else '-c'
            result = subprocess.run(
                ["ping", param, "4", target],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.log_output("✓ DIAGNOSTIC COMPLETE - HOST REACHABLE", color="#10b981")
                self.log_output(result.stdout, color="#10b981")
            else:
                self.log_output("✗ DIAGNOSTIC FAILED - HOST UNREACHABLE", error=True)
                self.log_output(result.stderr, color="#ef4444")
        except Exception as e:
            self.log_output(f"ERROR: {str(e)}", error=True)
        
        self.execute_btn.setEnabled(True)

    def port_scan(self, target):
        common_ports = [22, 80, 443, 3306, 5432]
        self.log_output(f"Scanning {len(common_ports)} common ports on {target}...")
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((target, port))
                service = {22: "SSH", 80: "HTTP", 443: "HTTPS", 3306: "MySQL", 5432: "PostgreSQL"}.get(port, "Unknown")
                
                if result == 0:
                    self.log_output(f"  ● Port {port} ({service}): OPEN", color="#10b981")
                else:
                    self.log_output(f"  ○ Port {port} ({service}): Closed")
                sock.close()
            except Exception as e:
                self.log_output(f"  ! Port {port}: Error {str(e)}", error=True)
        
        self.log_output("Scan complete.")
        self.execute_btn.setEnabled(True)

    def log_output(self, text, error=False, color=None):
        if color:
            self.console.append(f"<span style='color: {color};'>{text}</span>")
        elif error:
            self.console.append(f"<span style='color: #ef4444;'>[!] {text}</span>")
        else:
            self.console.append(f"<span style='color: #e2e8f0;'>{text}</span>")

    def clear_console(self):
        self.console.clear()
        self.log_output("Console cleared. System ready.")
