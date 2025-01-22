import tkinter as tk
from tkinter import messagebox
import sqlite3
from dashboard import open_dashboard
from PIL import Image, ImageTk

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
root.title("Sistema de Gestão Paroquial")

# Definir o tamanho da janela de login
largura = 800
altura = 600

# Calcular a posição central
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
pos_x = (screen_width // 2) - (largura // 2)
pos_y = (screen_height // 2) - (altura // 2)

# Configurar a janela para abrir no centro
root.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
root.resizable(False, False)

# Carregar e redimensionar a imagem de fundo
image = Image.open("church.jpg")  # Certifique-se de que o arquivo está no mesmo diretório
image = image.resize((largura, altura))
bg_image = ImageTk.PhotoImage(image)

# Criar um label com a imagem de fundo
background_label = tk.Label(root, image=bg_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Frame semi-transparente para o formulário de login
login_frame = tk.Frame(root, bg='white')
login_frame.place(relx=0.7, rely=0.5, anchor="center")

# Título do sistema
titulo = tk.Label(login_frame, 
                 text="Bem-vindo\nSistema Dizimista Bom Pastor",
                 font=("Arial", 16, "bold"),
                 bg='white',
                 justify="center")
titulo.pack(pady=20)

# Widgets de login com estilo aprimorado
style = {'font': ("Arial", 12),
         'bg': 'white',
         'fg': '#333333'}

tk.Label(login_frame, text="Usuário:", **style).pack(pady=5)
entry_usuario = tk.Entry(login_frame, width=30, font=("Arial", 12))
entry_usuario.pack(pady=5)

tk.Label(login_frame, text="Senha:", **style).pack(pady=5)
entry_senha = tk.Entry(login_frame, show="*", width=30, font=("Arial", 12))
entry_senha.pack(pady=5)

# Botão de login estilizado
login_button = tk.Button(login_frame,
                        text="Entrar",
                        command=login,
                        width=15,
                        font=("Arial", 12, "bold"),
                        bg="#4CAF50",
                        fg="white",
                        cursor="hand2")
login_button.pack(pady=20)

# Adicionar padding ao frame de login
for child in login_frame.winfo_children():
    child.pack_configure(padx=30)

root.mainloop()