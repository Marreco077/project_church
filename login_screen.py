import tkinter as tk
from tkinter import messagebox
import sqlite3
from dashboard import open_dashboard

def login():
    usuario = entry_usuario.get()
    senha = entry_senha.get()
    
    conn = sqlite3.connect("dizimos.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        messagebox.showinfo("Login", "Login bem-sucedido!")
        root.destroy()
        open_dashboard()
    else:
        messagebox.showerror("Erro", "Usuário ou senha inválidos!")

# Tela de login
root = tk.Tk()
root.title("Login - Gerenciador de Dízimos")

# Definir o tamanho da janela de login
largura = 400
altura = 300

# Calcular a posição central
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
pos_x = (screen_width // 2) - (largura // 2)
pos_y = (screen_height // 2) - (altura // 2)

# Configurar a janela para abrir no centro
root.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
root.resizable(False, False)  # Impede redimensionamento

# Frame para centralizar os widgets
frame = tk.Frame(root)
frame.place(relx=0.5, rely=0.5, anchor="center")  # Centraliza o frame na janela

# Widgets de login
tk.Label(frame, text="Usuário:", font=("Arial", 12)).pack(pady=5)
entry_usuario = tk.Entry(frame, width=30, font=("Arial", 12))
entry_usuario.pack(pady=5)

tk.Label(frame, text="Senha:", font=("Arial", 12)).pack(pady=5)
entry_senha = tk.Entry(frame, show="*", width=30, font=("Arial", 12))
entry_senha.pack(pady=5)

tk.Button(frame, text="Entrar", command=login, width=15, font=("Arial", 12)).pack(pady=20)

root.mainloop()
