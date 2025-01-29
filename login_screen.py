import tkinter as tk
from tkinter import messagebox
import sqlite3
from dashboard import open_dashboard
from PIL import Image, ImageTk
import os
import sys

def resource_path(relative_path):
    """Obtém o caminho absoluto do recurso"""
    try:
        # PyInstaller cria um diretório temp e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def create_login_screen(root):
    def login():
        usuario = entry_usuario.get()
        senha = entry_senha.get()
        
        conn = sqlite3.connect(resource_path("dizimos.db"))
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

    def on_enter_entry(event):
        event.widget.config(bg="#ffe0f0", highlightbackground="#FF80FF")

    def on_leave_entry(event):
        event.widget.config(bg="white", highlightbackground="#CCCCCC")

    # Configuração da janela principal
    root.title("Sistema de Gestão Paroquial")
    largura = 1200
    altura = 700
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    pos_x = (screen_width // 2) - (largura // 2)
    pos_y = (screen_height // 2) - (altura // 2)
    root.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
    root.resizable(False, False)

    # Carregar e redimensionar a imagem de fundo
    try:
        image = Image.open(resource_path("church.jpeg"))
        image = image.resize((largura, altura))
        bg_image = ImageTk.PhotoImage(image)
        background_label = tk.Label(root, image=bg_image)
        background_label.image = bg_image  # Manter referência!
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
    except Exception as e:
        print(f"Erro ao carregar a imagem: {e}")
        background_label = tk.Label(root, bg='#f0f0f0')
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Frame de login
    login_frame = tk.Frame(root, bg='white', bd=10, relief="ridge", 
                          highlightbackground="#2196F3", highlightthickness=2)
    login_frame.place(x=750, y=50)

    # Título
    titulo = tk.Label(login_frame, 
                     text="Sistema Dizimista Bom Pastor",
                     font=("Helvetica", 18, "bold"),
                     bg='white',
                     fg="#2196F3",
                     justify="center")
    titulo.grid(row=0, column=0, pady=20, padx=20)

    style_label = {'font': ("Helvetica", 12),
                   'bg': 'white',
                   'fg': '#333333'}

    # Campo de usuário
    tk.Label(login_frame, text="Usuário:", **style_label).grid(row=1, column=0, pady=5)
    entry_usuario = tk.Entry(login_frame, 
                           font=("Helvetica", 12), 
                           bg="white", 
                           fg="#333333", 
                           relief="flat", 
                           width=30,
                           highlightthickness=2,
                           highlightbackground="#CCCCCC",
                           highlightcolor="#2196F3")
    entry_usuario.grid(row=2, column=0, pady=5)
    entry_usuario.bind("<FocusIn>", on_enter_entry)
    entry_usuario.bind("<FocusOut>", on_leave_entry)

    # Campo de senha
    tk.Label(login_frame, text="Senha:", **style_label).grid(row=3, column=0, pady=5)
    entry_senha = tk.Entry(login_frame, 
                         show="*", 
                         font=("Helvetica", 12), 
                         bg="white", 
                         fg="#333333", 
                         relief="flat", 
                         width=30,
                         highlightthickness=2,
                         highlightbackground="#CCCCCC",
                         highlightcolor="#2196F3")
    entry_senha.grid(row=4, column=0, pady=5)
    entry_senha.bind("<FocusIn>", on_enter_entry)
    entry_senha.bind("<FocusOut>", on_leave_entry)

    # Botão de login
    login_button = tk.Button(login_frame,
                           text="Entrar",
                           command=login,
                           width=20,
                           font=("Helvetica", 14, "bold"),
                           bg="#FF66B2",
                           fg="white",
                           activebackground="#FF3385",
                           activeforeground="white",
                           cursor="hand2",
                           relief="flat",
                           bd=5)
    login_button.grid(row=5, column=0, pady=20)

    # Ajustar padding
    for child in login_frame.winfo_children():
        child.grid_configure(padx=20)