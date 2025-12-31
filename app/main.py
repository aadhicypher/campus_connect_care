from app.bootstrap.setup_admin import admin_exists, create_admin
from app.ui.login_window import start_login

if not admin_exists():
    print("=== First Time Setup ===")
    na_pwd = input("Set Network Admin password: ")
    sa_pwd = input("Set Security Admin password: ")

    create_admin("netadmin", na_pwd, "NetworkAdmin")
    create_admin("secadmin", sa_pwd, "SecurityAdmin")

    print("Admins created. Restart application.")
    exit()

start_login()
