from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QHBoxLayout,
    QGraphicsDropShadowEffect, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
import bcrypt

from app.db.connection import get_connection


class ChangePasswordPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Main layout with subtle background
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignTop)

        # Header Section (like other pages)
        header_card = QFrame()
        header_card.setStyleSheet("""
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
        header_card.setGraphicsEffect(shadow)

        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(25, 20, 25, 20)

        # Icon and title row
        title_row = QHBoxLayout()
        
        icon_label = QLabel("◈")
        icon_label.setStyleSheet("color: #ef4444; font-size: 24px;")  # Red icon only
        title_row.addWidget(icon_label)
        
        title_text = QLabel("SECURITY PROTOCOL")
        title_text.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_text.setStyleSheet("color: #0f172a; letter-spacing: 1px;")
        title_row.addWidget(title_text)
        title_row.addStretch()
        
        header_layout.addLayout(title_row)

        desc = QLabel("Access key rotation and credential management")
        desc.setFont(QFont("Segoe UI", 11))
        desc.setStyleSheet("color: #64748b;")
        header_layout.addWidget(desc)

        main_layout.addWidget(header_card)

        # Content Grid - Two columns
        content_grid = QHBoxLayout()
        content_grid.setSpacing(20)

        # Left: Password Change Form
        form_card = self.create_form_card()
        content_grid.addWidget(form_card, stretch=1)

        # Right: Security Guidelines
        guidelines_card = self.create_guidelines_card()
        content_grid.addWidget(guidelines_card, stretch=1)

        main_layout.addLayout(content_grid, stretch=1)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def create_form_card(self):
        """Create the password change form - CLEAN STYLE"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border-top: 4px solid #ef4444;  /* Only top border red */
                border-left: 1px solid #e2e8f0;
                border-right: 1px solid #e2e8f0;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(15, 23, 42, 20))
        shadow.setOffset(0, 6)
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(18)

        # Form Title
        form_title = QLabel("ROTATE ACCESS KEY")
        form_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        form_title.setStyleSheet("color: #ef4444;")  # Red title only
        layout.addWidget(form_title)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #fecaca; margin: 5px 0;")
        layout.addWidget(sep)

        layout.addSpacing(10)

        # Current Password Field - NO RED BORDER
        curr_label = QLabel("Current Access Key")
        curr_label.setFont(QFont("Consolas", 9))
        curr_label.setStyleSheet("color: #475569; font-weight: bold;")  # Normal dark gray, NO border
        layout.addWidget(curr_label)

        self.current_pass = QLineEdit()
        self.current_pass.setPlaceholderText("Enter current password")
        self.current_pass.setEchoMode(QLineEdit.Password)
        self.current_pass.setFixedHeight(45)
        self.current_pass.setStyleSheet("""
            QLineEdit {
                padding: 0 15px;
                font-size: 13px;
                border: 2px solid #e2e8f0;  /* GRAY border, not red */
                border-radius: 8px;
                background-color: #f8fafc;
                font-family: 'Consolas', monospace;
                color: #0f172a;
            }
            QLineEdit:focus {
                border: 2px solid #ef4444;  /* Red only on focus */
                background-color: white;
            }
            QLineEdit:hover {
                border: 2px solid #cbd5e1;
            }
        """)
        layout.addWidget(self.current_pass)

        layout.addSpacing(8)

        # New Password Field - NO RED BORDER
        new_label = QLabel("New Access Key")
        new_label.setFont(QFont("Consolas", 9))
        new_label.setStyleSheet("color: #475569; font-weight: bold;")  # Normal style
        layout.addWidget(new_label)

        self.new_pass = QLineEdit()
        self.new_pass.setPlaceholderText("Minimum 8 characters required")
        self.new_pass.setEchoMode(QLineEdit.Password)
        self.new_pass.setFixedHeight(45)
        self.new_pass.setStyleSheet("""
            QLineEdit {
                padding: 0 15px;
                font-size: 13px;
                border: 2px solid #e2e8f0;  /* GRAY border */
                border-radius: 8px;
                background-color: #f8fafc;
                font-family: 'Consolas', monospace;
                color: #0f172a;
            }
            QLineEdit:focus {
                border: 2px solid #ef4444;  /* Red only on focus */
                background-color: white;
            }
            QLineEdit:hover {
                border: 2px solid #cbd5e1;
            }
        """)
        layout.addWidget(self.new_pass)

        layout.addSpacing(8)

        # Confirm Password Field - NO RED BORDER
        conf_label = QLabel("Confirm New Key")
        conf_label.setFont(QFont("Consolas", 9))
        conf_label.setStyleSheet("color: #475569; font-weight: bold;")  # Normal style
        layout.addWidget(conf_label)

        self.confirm_pass = QLineEdit()
        self.confirm_pass.setPlaceholderText("Re-enter new password")
        self.confirm_pass.setEchoMode(QLineEdit.Password)
        self.confirm_pass.setFixedHeight(45)
        self.confirm_pass.setStyleSheet("""
            QLineEdit {
                padding: 0 15px;
                font-size: 13px;
                border: 2px solid #e2e8f0;  /* GRAY border */
                border-radius: 8px;
                background-color: #f8fafc;
                font-family: 'Consolas', monospace;
                color: #0f172a;
            }
            QLineEdit:focus {
                border: 2px solid #ef4444;  /* Red only on focus */
                background-color: white;
            }
            QLineEdit:hover {
                border: 2px solid #cbd5e1;
            }
        """)
        layout.addWidget(self.confirm_pass)

        layout.addSpacing(20)

        # Action Buttons Row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        # Cancel Button
        cancel_btn = QPushButton("CANCEL")
        cancel_btn.setFixedHeight(45)
        cancel_btn.setFixedWidth(120)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
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
        cancel_btn.clicked.connect(self.clear_fields)
        btn_row.addWidget(cancel_btn)

        btn_row.addStretch()

        # Update Button - Red accent (only the button, not everything)
        update_btn = QPushButton("◈ ROTATE KEY")
        update_btn.setFixedHeight(45)
        update_btn.setFixedWidth(160)
        update_btn.setCursor(Qt.PointingHandCursor)
        update_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ef4444, stop:1 #dc2626);
                color: white;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #dc2626, stop:1 #b91c1c);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #b91c1c, stop:1 #991b1b);
            }
        """)
        update_btn.clicked.connect(self.handle_change_password)
        btn_row.addWidget(update_btn)

        layout.addLayout(btn_row)

        return card

    def create_guidelines_card(self):
        """Security guidelines side panel"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #fef2f2;  /* Very light red tint */
                border-radius: 12px;
                border: 1px solid #fecaca;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(15, 23, 42, 15))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # Header
        header = QLabel("◈ SECURITY GUIDELINES")
        header.setFont(QFont("Segoe UI", 13, QFont.Bold))
        header.setStyleSheet("color: #991b1b;")  # Dark red text
        layout.addWidget(header)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet("background-color: #fca5a5;")
        layout.addWidget(sep)

        layout.addSpacing(10)

        # Guidelines content
        guidelines_text = """
<strong>Password Requirements:</strong><br><br>
• Minimum 8 characters length<br>
• Mix of uppercase & lowercase<br>
• Include numbers (0-9)<br>
• Include special characters<br>
• Avoid common dictionary words<br><br>

<strong>Security Protocols:</strong><br><br>
• Immediate session logout after rotation<br>
• Email notification to administrator<br>
• Automatic backup of previous key<br>
• 24-hour cooldown between changes
        """

        content = QLabel(guidelines_text)
        content.setFont(QFont("Consolas", 10))
        content.setStyleSheet("""
            color: #7f1d1d; 
            line-height: 1.6;
            background-color: transparent;
        """)
        content.setWordWrap(True)
        content.setTextFormat(Qt.RichText)
        layout.addWidget(content)

        layout.addStretch()

        # Security badge at bottom
        badge = QLabel("🔒 Classified Access Only")
        badge.setFont(QFont("Consolas", 9, QFont.Bold))
        badge.setStyleSheet("""
            color: #dc2626;
            background-color: #fee2e2;
            padding: 10px;
            border-radius: 6px;
        """)
        badge.setAlignment(Qt.AlignCenter)
        layout.addWidget(badge)

        return card

    def clear_fields(self):
        """Clear all input fields"""
        self.current_pass.clear()
        self.new_pass.clear()
        self.confirm_pass.clear()

    def handle_change_password(self):
        current = self.current_pass.text().strip()
        new = self.new_pass.text().strip()
        confirm = self.confirm_pass.text().strip()

        if not all([current, new, confirm]):
            QMessageBox.warning(self, "Validation Error", 
                "⚠ All fields are required to complete key rotation.")
            return

        if new != confirm:
            QMessageBox.warning(self, "Validation Error", 
                "⚠ New access keys do not match. Please verify.")
            return

        if len(new) < 8:
            QMessageBox.warning(self, "Validation Error", 
                "⚠ Access key must contain at least 8 characters.")
            return

        try:
            success = self.update_password(current, new)
            
            if success:
                QMessageBox.information(self, "Success", 
                    "✓ Access key rotated successfully.\n\n"
                    "Please authenticate with your new credentials.")
                self.clear_fields()
            else:
                QMessageBox.critical(self, "Authentication Failed", 
                    "✗ Current access key is incorrect.\n\n"
                    "Please verify and try again.")
        except Exception as e:
            QMessageBox.critical(self, "System Error", 
                f"✗ Operation failed: {str(e)}")

    def update_password(self, current_pass, new_pass):
        """Update password in database"""
        conn = get_connection()
        cur = conn.cursor()
        
        # Get current user from session (placeholder - implement with your session)
        # For now using hardcoded, you should pass user from login
        username = "netadmin_1"  # TODO: Get from session
        
        cur.execute("SELECT password_hash FROM users WHERE username=%s", (username,))
        result = cur.fetchone()
        
        if not result:
            return False
            
        stored_hash = result[0].encode()
        if not bcrypt.checkpw(current_pass.encode(), stored_hash):
            cur.close()
            conn.close()
            return False
            
        # Update to new password
        new_hash = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt()).decode()
        cur.execute("UPDATE users SET password_hash=%s WHERE username=%s", 
                   (new_hash, username))
        conn.commit()
        cur.close()
        conn.close()
        return True
