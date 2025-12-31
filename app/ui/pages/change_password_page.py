from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class ChangePasswordPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # Header
        header = QLabel("Change Password")
        header_font = QFont()
        header_font.setPointSize(20)
        header_font.setBold(True)
        header.setFont(header_font)
        main_layout.addWidget(header)

        # Description
        description = QLabel("Update your admin account password")
        description.setStyleSheet("color: gray; font-size: 13px;")
        main_layout.addWidget(description)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        main_layout.addSpacing(10)

        # Form container
        form_widget = QWidget()
        form_widget.setMaximumWidth(500)
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        # Current Password
        current_password_label = QLabel("Current Password")
        current_password_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        form_layout.addWidget(current_password_label)

        self.current_password_input = QLineEdit()
        self.current_password_input.setPlaceholderText("Enter current password")
        self.current_password_input.setEchoMode(QLineEdit.Password)
        self.current_password_input.setMinimumHeight(40)
        self.current_password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
        """)
        self.current_password_input.textChanged.connect(self.clear_validation_errors)
        form_layout.addWidget(self.current_password_input)

        # Current password error
        self.current_password_error = QLabel()
        self.current_password_error.setStyleSheet("color: red; font-size: 11px;")
        self.current_password_error.hide()
        form_layout.addWidget(self.current_password_error)

        # New Password
        new_password_label = QLabel("New Password")
        new_password_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        form_layout.addWidget(new_password_label)

        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("Enter new password")
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setMinimumHeight(40)
        self.new_password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
        """)
        self.new_password_input.textChanged.connect(self.clear_validation_errors)
        form_layout.addWidget(self.new_password_input)

        # New password error
        self.new_password_error = QLabel()
        self.new_password_error.setStyleSheet("color: red; font-size: 11px;")
        self.new_password_error.hide()
        form_layout.addWidget(self.new_password_error)

        # Confirm New Password
        confirm_password_label = QLabel("Confirm New Password")
        confirm_password_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        form_layout.addWidget(confirm_password_label)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Re-enter new password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setMinimumHeight(40)
        self.confirm_password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
        """)
        self.confirm_password_input.textChanged.connect(self.clear_validation_errors)
        self.confirm_password_input.returnPressed.connect(self.handle_change_password)
        form_layout.addWidget(self.confirm_password_input)

        # Confirm password error
        self.confirm_password_error = QLabel()
        self.confirm_password_error.setStyleSheet("color: red; font-size: 11px;")
        self.confirm_password_error.hide()
        form_layout.addWidget(self.confirm_password_error)

        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        main_layout.addSpacing(10)

        # Update button
        update_btn = QPushButton("Update Password")
        update_btn.setMinimumHeight(45)
        update_btn.setMaximumWidth(500)
        update_btn.setCursor(Qt.PointingHandCursor)
        update_btn.setStyleSheet("font-size: 15px; font-weight: bold;")
        update_btn.clicked.connect(self.handle_change_password)
        main_layout.addWidget(update_btn)

        # Password requirements info
        requirements = QLabel(
            "Password requirements:\n"
            "• At least 8 characters long\n"
            "• Must contain letters and numbers"
        )
        requirements.setStyleSheet("color: gray; font-size: 11px; margin-top: 10px;")
        requirements.setMaximumWidth(500)
        main_layout.addWidget(requirements)

        # Add stretch
        main_layout.addStretch()

        self.setLayout(main_layout)

    def clear_validation_errors(self):
        """Clear validation errors when user starts typing"""
        sender = self.sender()
        
        if sender == self.current_password_input:
            self.current_password_error.hide()
            self.current_password_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    font-size: 14px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                }
            """)
        elif sender == self.new_password_input:
            self.new_password_error.hide()
            self.new_password_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    font-size: 14px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                }
            """)
        elif sender == self.confirm_password_input:
            self.confirm_password_error.hide()
            self.confirm_password_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    font-size: 14px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                }
            """)

    def validate_inputs(self):
        """Validate all password inputs"""
        is_valid = True

        current_password = self.current_password_input.text().strip()
        new_password = self.new_password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()

        # Validate current password
        if not current_password:
            self.current_password_error.setText("Current password is required")
            self.current_password_error.show()
            self.current_password_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    font-size: 14px;
                    border: 1px solid red;
                    border-radius: 3px;
                    background-color: #ffe6e6;
                }
            """)
            is_valid = False

        # Validate new password
        if not new_password:
            self.new_password_error.setText("New password is required")
            self.new_password_error.show()
            self.new_password_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    font-size: 14px;
                    border: 1px solid red;
                    border-radius: 3px;
                    background-color: #ffe6e6;
                }
            """)
            is_valid = False
        elif len(new_password) < 8:
            self.new_password_error.setText("Password must be at least 8 characters")
            self.new_password_error.show()
            self.new_password_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    font-size: 14px;
                    border: 1px solid red;
                    border-radius: 3px;
                    background-color: #ffe6e6;
                }
            """)
            is_valid = False
        elif not any(c.isalpha() for c in new_password) or not any(c.isdigit() for c in new_password):
            self.new_password_error.setText("Password must contain both letters and numbers")
            self.new_password_error.show()
            self.new_password_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    font-size: 14px;
                    border: 1px solid red;
                    border-radius: 3px;
                    background-color: #ffe6e6;
                }
            """)
            is_valid = False

        # Validate confirm password
        if not confirm_password:
            self.confirm_password_error.setText("Please confirm your new password")
            self.confirm_password_error.show()
            self.confirm_password_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    font-size: 14px;
                    border: 1px solid red;
                    border-radius: 3px;
                    background-color: #ffe6e6;
                }
            """)
            is_valid = False
        elif new_password != confirm_password:
            self.confirm_password_error.setText("Passwords do not match")
            self.confirm_password_error.show()
            self.confirm_password_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    font-size: 14px;
                    border: 1px solid red;
                    border-radius: 3px;
                    background-color: #ffe6e6;
                }
            """)
            is_valid = False

        return is_valid

    def handle_change_password(self):
        """Handle password change"""
        if not self.validate_inputs():
            return

        current_password = self.current_password_input.text().strip()
        new_password = self.new_password_input.text().strip()

        # TODO: Add your actual password change logic here
        # Example: update_password(current_password, new_password)
        
        # For now, show success message
        reply = QMessageBox.question(
            self,
            "Confirm Password Change",
            "Are you sure you want to change your password?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # TODO: Call your backend function to update password
            # success = update_admin_password(current_password, new_password)
            # if success:
            
            QMessageBox.information(
                self,
                "Success",
                "Your password has been updated successfully!"
            )
            
            # Clear all fields
            self.current_password_input.clear()
            self.new_password_input.clear()
            self.confirm_password_input.clear()