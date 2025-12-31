from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)

from app.users.create_it_staff import create_it_staff

class UserManagementPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("👤 Create IT Support User"))

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        btn = QPushButton("Create IT Staff")
        btn.clicked.connect(self.create_user)

        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(btn)

        self.setLayout(layout)

    def create_user(self):
        u = self.username.text().strip()
        p = self.password.text().strip()

        if not u or not p:
            QMessageBox.warning(self, "Error", "All fields required")
            return

        create_it_staff(u, p)
        QMessageBox.information(self, "Success", "IT Staff created")
        self.username.clear()
        self.password.clear()
