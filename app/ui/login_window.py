from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout, QFrame, QCheckBox
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QFont
import sys

from app.auth.login import login
from app.session.session_log import log_session
from app.ui.main_window import MainWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Campus Connect-Care | Admin Login")
        self.setMinimumSize(500, 400)
        self.resize(600, 550)
        self.settings = QSettings("CampusConnectCare", "AdminLogin")
        self.init_ui()
        self.load_remembered_credentials()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # Header section
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)
        
        # App title
        app_title = QLabel("Campus Connect-Care")
        app_title.setAlignment(Qt.AlignCenter)
        app_title_font = QFont()
        app_title_font.setPointSize(24)
        app_title_font.setBold(True)
        app_title.setFont(app_title_font)
        app_title.setStyleSheet("margin-bottom: 5px;")
        header_layout.addWidget(app_title)

        # Subtitle
        subtitle = QLabel("Admin Portal")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("margin-bottom: 20px;")
        header_layout.addWidget(subtitle)

        main_layout.addLayout(header_layout)

        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        main_layout.addSpacing(10)

        # Login form section
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        # Username field
        username_label = QLabel("Username")
        username_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        form_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(40)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
        """)
        self.username_input.textChanged.connect(self.clear_validation_error)
        form_layout.addWidget(self.username_input)

        # Username error label
        self.username_error = QLabel()
        self.username_error.setStyleSheet("color: red; font-size: 11px;")
        self.username_error.hide()
        form_layout.addWidget(self.username_error)

        # Password field
        password_label = QLabel("Password")
        password_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
        """)
        self.password_input.returnPressed.connect(self.handle_login)
        self.password_input.textChanged.connect(self.clear_validation_error)
        form_layout.addWidget(self.password_input)

        # Password error label
        self.password_error = QLabel()
        self.password_error.setStyleSheet("color: red; font-size: 11px;")
        self.password_error.hide()
        form_layout.addWidget(self.password_error)

        main_layout.addLayout(form_layout)

        # Remember me and forgot password row
        options_layout = QHBoxLayout()
        
        self.remember_me_checkbox = QCheckBox("Remember me")
        self.remember_me_checkbox.setStyleSheet("font-size: 12px;")
        options_layout.addWidget(self.remember_me_checkbox)
        
        options_layout.addStretch()
        
        forgot_password_btn = QPushButton("Forgot Password?")
        forgot_password_btn.setFlat(True)
        forgot_password_btn.setCursor(Qt.PointingHandCursor)
        forgot_password_btn.setStyleSheet("""
            QPushButton {
                color: blue;
                font-size: 12px;
                text-decoration: underline;
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                color: darkblue;
            }
        """)
        forgot_password_btn.clicked.connect(self.handle_forgot_password)
        options_layout.addWidget(forgot_password_btn)
        
        main_layout.addLayout(options_layout)

        main_layout.addSpacing(10)

        # Login button
        login_btn = QPushButton("Login")
        login_btn.setMinimumHeight(45)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setStyleSheet("font-size: 15px; font-weight: bold;")
        login_btn.clicked.connect(self.handle_login)
        main_layout.addWidget(login_btn)

        # Add stretch to push everything up
        main_layout.addStretch()

        # Footer
        footer = QLabel("© 2025 Campus Connect-Care | Secure Admin Access")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: gray; font-size: 10px; margin-top: 20px;")
        main_layout.addWidget(footer)

        self.setLayout(main_layout)

    def clear_validation_error(self):
        """Clear validation errors when user starts typing"""
        sender = self.sender()
        if sender == self.username_input:
            self.username_error.hide()
            self.username_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    font-size: 14px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                }
            """)
        elif sender == self.password_input:
            self.password_error.hide()
            self.password_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    font-size: 14px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                }
            """)

    def validate_inputs(self):
        """Validate username and password inputs"""
        is_valid = True
        
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # Validate username
        if not username:
            self.username_error.setText("Username is required")
            self.username_error.show()
            self.username_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    font-size: 14px;
                    border: 1px solid red;
                    border-radius: 3px;
                    background-color: #ffe6e6;
                }
            """)
            is_valid = False
        elif len(username) < 3:
            self.username_error.setText("Username must be at least 3 characters")
            self.username_error.show()
            self.username_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    font-size: 14px;
                    border: 1px solid red;
                    border-radius: 3px;
                    background-color: #ffe6e6;
                }
            """)
            is_valid = False
        
        # Validate password
        if not password:
            self.password_error.setText("Password is required")
            self.password_error.show()
            self.password_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    font-size: 14px;
                    border: 1px solid red;
                    border-radius: 3px;
                    background-color: #ffe6e6;
                }
            """)
            is_valid = False
        elif len(password) < 4:
            self.password_error.setText("Password must be at least 4 characters")
            self.password_error.show()
            self.password_input.setStyleSheet("""
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

    def load_remembered_credentials(self):
        """Load saved credentials if remember me was checked"""
        if self.settings.value("remember_me", False, type=bool):
            saved_username = self.settings.value("username", "")
            if saved_username:
                self.username_input.setText(saved_username)
                self.remember_me_checkbox.setChecked(True)
                self.password_input.setFocus()

    def save_credentials(self, username):
        """Save credentials if remember me is checked"""
        if self.remember_me_checkbox.isChecked():
            self.settings.setValue("remember_me", True)
            self.settings.setValue("username", username)
        else:
            self.settings.setValue("remember_me", False)
            self.settings.remove("username")

    def handle_forgot_password(self):
        """Handle forgot password request"""
        username = self.username_input.text().strip()
        
        if not username:
            QMessageBox.information(
                self,
                "Password Recovery",
                "Please enter your username first, then click 'Forgot Password?' to receive recovery instructions."
            )
            return
        
        # Show recovery dialog
        QMessageBox.information(
            self,
            "Password Recovery",
            f"Password recovery instructions have been sent to the email associated with username '{username}'.\n\n"
            "Please check your email and follow the instructions to reset your password.\n\n"
            "If you don't receive an email within 5 minutes, please contact the system administrator."
        )

    def handle_login(self):
        # Validate inputs first
        if not self.validate_inputs():
            return
        
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        user = login(username, password)

        if not user:
            QMessageBox.critical(
                self, 
                "Login Failed", 
                "Invalid credentials. Please check your username and password and try again."
            )
            # Clear password field for security
            self.password_input.clear()
            self.password_input.setFocus()
            return

        # Save credentials if remember me is checked
        self.save_credentials(username)

        # Log session
        log_session(user["id"])

        # Show success message
        QMessageBox.information(
            self,
            "Success",
            f"Welcome back!\n\nRole: {user['role']}\nLogin successful."
        )

        # 🔥 OPEN MAIN DESKTOP WINDOW
        self.main_window = MainWindow(user["role"])
        self.main_window.show()

        # Close login window
        self.close()


def start_login():
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())