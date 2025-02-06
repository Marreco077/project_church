import tkinter as tk
from login_screen import create_login_screen
import os
import sqlite3
import sys


def resource_path(relative_path):
    """Retorna o caminho absoluto para recursos."""
    try:
        # Quando executado como um executável
        base_path = sys._MEIPASS
    except AttributeError:
        # Quando executado como script Python
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def main():
    # Obter o diretório onde o executável está sendo executado
    if getattr(sys, "frozen", False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    db_path = os.path.join(application_path, "dizimos.db")
    conn = sqlite3.connect(db_path)
    conn.close()

    # Iniciar a interface gráfica
    root = tk.Tk()
    create_login_screen(root)
    root.mainloop()


if __name__ == "__main__":
    main()
