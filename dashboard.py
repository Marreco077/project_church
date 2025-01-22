import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def open_dashboard():
    def formatar_data_digitacao(event, entry):
        texto = entry.get().replace("/", "")
        cursor_pos = entry.index(tk.INSERT)
        
        if len(texto) > 8:
            texto = texto[:8]
        
        if texto.isdigit():
            if len(texto) >= 2:
                texto = texto[:2] + "/" + texto[2:]
            if len(texto) >= 5:
                texto = texto[:5] + "/" + texto[5:]
                
            entry.delete(0, tk.END)
            entry.insert(0, texto)
            
            if event.keysym != 'BackSpace':
                if cursor_pos in [2, 5]:
                    cursor_pos += 1
            entry.icursor(min(cursor_pos, len(texto)))

    def converter_data_para_banco(data):
        if "/" in data:
            dia, mes, ano = data.split("/")
            return f"{ano}-{mes}-{dia}"
        return data

    def carregar_dizimistas():
        for item in tabela.get_children():
            tabela.delete(item)
        
        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, valor, data_doacao, aniversario, telefone, status_atraso FROM dizimistas")
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            tabela.insert("", "end", values=row)
    
    def cadastrar_dizimista():
        nome = entry_nome.get()
        valor = entry_valor.get()
        data_doacao = converter_data_para_banco(entry_data_doacao.get())
        aniversario = converter_data_para_banco(entry_aniversario.get())
        telefone = entry_telefone.get()
        
        if not nome or not valor or not data_doacao or not aniversario or not telefone:
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
            return
        
        try:
            conn = sqlite3.connect("dizimos.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO dizimistas (nome, valor, data_doacao, aniversario, telefone)
                VALUES (?, ?, ?, ?, ?)
            """, (nome, float(valor), data_doacao, aniversario, telefone))
            conn.commit()
            conn.close()
            carregar_dizimistas()
            messagebox.showinfo("Sucesso", "Dizimista cadastrado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar: {e}")
    
    def deletar_dizimista():
        selected_item = tabela.selection()
        if not selected_item:
            messagebox.showwarning("Seleção", "Por favor, selecione um dizimista para excluir.")
            return
        
        item = tabela.item(selected_item)
        dizimista_id = item['values'][0]
        
        try:
            conn = sqlite3.connect("dizimos.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM dizimistas WHERE id = ?", (dizimista_id,))
            conn.commit()
            conn.close()
            carregar_dizimistas()
            messagebox.showinfo("Sucesso", "Dizimista excluído com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir: {e}")
    
    dashboard = tk.Tk()
    dashboard.title("Gerenciador de Dízimos")
    dashboard.geometry("800x600")
    
    largura = 800
    altura = 600
    screen_width = dashboard.winfo_screenwidth()
    screen_height = dashboard.winfo_screenheight()
    pos_x = (screen_width // 2) - (largura // 2)
    pos_y = (screen_height // 2) - (altura // 2)
    dashboard.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
    
    frame_form = tk.Frame(dashboard)
    frame_form.pack(pady=10)

    tk.Label(frame_form, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
    entry_nome = tk.Entry(frame_form, width=25)
    entry_nome.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_form, text="Valor:").grid(row=1, column=0, padx=5, pady=5)
    entry_valor = tk.Entry(frame_form, width=25)
    entry_valor.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame_form, text="Data Doação:").grid(row=2, column=0, padx=5, pady=5)
    entry_data_doacao = tk.Entry(frame_form, width=25)
    entry_data_doacao.grid(row=2, column=1, padx=5, pady=5)
    entry_data_doacao.bind('<KeyRelease>', lambda e: formatar_data_digitacao(e, entry_data_doacao))

    tk.Label(frame_form, text="Aniversário:").grid(row=3, column=0, padx=5, pady=5)
    entry_aniversario = tk.Entry(frame_form, width=25)
    entry_aniversario.grid(row=3, column=1, padx=5, pady=5)
    entry_aniversario.bind('<KeyRelease>', lambda e: formatar_data_digitacao(e, entry_aniversario))

    tk.Label(frame_form, text="Telefone:").grid(row=4, column=0, padx=5, pady=5)
    entry_telefone = tk.Entry(frame_form, width=25)
    entry_telefone.grid(row=4, column=1, padx=5, pady=5)

    tk.Button(frame_form, text="Cadastrar", command=cadastrar_dizimista).grid(row=5, column=0, columnspan=2, pady=10)

    tabela = ttk.Treeview(dashboard, columns=("ID", "Nome", "Valor", "Data Doação", "Aniversário", "Telefone", "Status"), show="headings")
    tabela.pack(fill="both", expand=True, padx=10, pady=10)

    tabela.heading("ID", text="ID")
    tabela.heading("Nome", text="Nome")
    tabela.heading("Valor", text="Valor")
    tabela.heading("Data Doação", text="Data Doação")
    tabela.heading("Aniversário", text="Aniversário")
    tabela.heading("Telefone", text="Telefone")
    tabela.heading("Status", text="Status")

    tabela.column("ID", width=30)
    tabela.column("Nome", width=150)
    tabela.column("Valor", width=70)
    tabela.column("Data Doação", width=100)
    tabela.column("Aniversário", width=100)
    tabela.column("Telefone", width=100)
    tabela.column("Status", width=80)

    tk.Button(dashboard, text="Deletar Dizimista", command=deletar_dizimista, width=20).pack(pady=10)

    carregar_dizimistas()

    dashboard.mainloop()