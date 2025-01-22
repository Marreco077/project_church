import tkinter as tk 
from tkinter import ttk, messagebox
import sqlite3
import locale
from datetime import datetime, timedelta

def open_dashboard():
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    
    def atualizar_status_pagamentos():
        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()
        data_atual = datetime.now()
        limite_atraso = data_atual - timedelta(days=30)
        
        # Update status_atraso for all records
        cursor.execute("""
            UPDATE dizimistas 
            SET status_atraso = CASE 
                WHEN strftime('%Y-%m-%d', data_doacao) < ? THEN 'Faltando'
                ELSE 'Em dia'
            END
        """, (limite_atraso.strftime('%Y-%m-%d'),))
        
        conn.commit()
        conn.close()
    
    def atualizar_sumarios():
        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT SUM(valor) FROM dizimistas 
            WHERE strftime('%m', data_doacao) = '01' 
            AND strftime('%Y', data_doacao) = '2025'
        """)
        
        total_mes = cursor.fetchone()[0] or 0
        label_total_mes.config(text=f"Total Janeiro/2025:\n{locale.currency(total_mes, grouping=True)}")
        
        cursor.execute("""
            SELECT SUM(valor) FROM dizimistas 
            WHERE strftime('%Y', data_doacao) = '2025'
        """)
        
        total_ano = cursor.fetchone()[0] or 0
        label_total_ano.config(text=f"Total 2025:\n{locale.currency(total_ano, grouping=True)}")
        
        conn.close()

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

    def formatar_valor_digitacao(event, entry):
        texto = entry.get().replace("R$", "").replace(",", "").replace(".", "").strip()
        
        if not texto:
            entry.delete(0, tk.END)
            entry.insert(0, "R$0,00")
            return
            
        if texto.isdigit():
            valor = float(texto) / 100
            texto_formatado = f"R${valor:,.2f}".replace(".", ",")
            
            entry.delete(0, tk.END)
            entry.insert(0, texto_formatado)

    def converter_data_para_banco(data):
        if "/" in data:
            dia, mes, ano = data.split("/")
            return f"{dia}-{mes}-{ano}"
        return data

    def converter_valor_para_banco(valor):
        return float(valor.replace("R$", "").replace(".", "").replace(",", "."))

    def filtrar_dizimistas():
        nome_filtro = entry_filtro.get().lower()
        
        for item in tabela.get_children():
            tabela.delete(item)
        
        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()
        
        if nome_filtro:
            cursor.execute("""
                SELECT id, nome, valor, data_doacao, aniversario, telefone, status_atraso 
                FROM dizimistas 
                WHERE LOWER(nome) LIKE ?
            """, (f"%{nome_filtro}%",))
        else:
            cursor.execute("SELECT id, nome, valor, data_doacao, aniversario, telefone, status_atraso FROM dizimistas")
            
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            valor_formatado = f"R${float(row[2]):,.2f}".replace(".", ",")
            row_formatado = list(row)
            row_formatado[2] = valor_formatado
            tabela.insert("", "end", values=row_formatado)

    def carregar_dizimistas():
        atualizar_status_pagamentos()
        for item in tabela.get_children():
            tabela.delete(item)
        
        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, valor, data_doacao, aniversario, telefone, status_atraso FROM dizimistas")
        rows = cursor.fetchall()
        conn.close()
        
        # Configure tag before adding items
        tabela.tag_configure('faltando', foreground='red')
        
        for row in rows:
            valor_formatado = f"R${float(row[2]):,.2f}".replace(".", ",")
            row_formatado = list(row)
            row_formatado[2] = valor_formatado
            item = tabela.insert("", "end", values=row_formatado)
            
            # Apply tag based on status_atraso
            if row_formatado[6] == 'Faltando':
                tabela.item(item, tags=('faltando',))
        
        atualizar_sumarios()

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
            valor_convertido = converter_valor_para_banco(valor)
            conn = sqlite3.connect("dizimos.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT MIN(t1.id + 1) FROM dizimistas t1 WHERE NOT EXISTS (SELECT 1 FROM dizimistas t2 WHERE t2.id = t1.id + 1)")
            proximo_id = cursor.fetchone()[0]
            
            if not proximo_id:
                cursor.execute("SELECT COALESCE(MAX(id) + 1, 1) FROM dizimistas")
                proximo_id = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO dizimistas (id, nome, valor, data_doacao, aniversario, telefone)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (proximo_id, nome, valor_convertido, data_doacao, aniversario, telefone))
            
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
    dashboard.geometry("1200x700")
    
    largura = 1200
    altura = 700
    screen_width = dashboard.winfo_screenwidth()
    screen_height = dashboard.winfo_screenheight()
    pos_x = (screen_width // 2) - (largura // 2)
    pos_y = (screen_height // 2) - (altura // 2)
    dashboard.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
    
    frame_left = tk.Frame(dashboard)
    frame_left.pack(side="left", padx=10, fill="y")
    
    frame_right = tk.Frame(dashboard)
    frame_right.pack(side="right", padx=10, fill="y")
    
    frame_center = tk.Frame(dashboard)
    frame_center.pack(expand=True, fill="both")

    label_total_mes = tk.Label(frame_left, font=("Arial", 12, "bold"), relief="solid", padx=10, pady=10)
    label_total_mes.pack(pady=20)
    
    label_total_ano = tk.Label(frame_right, font=("Arial", 12, "bold"), relief="solid", padx=10, pady=10)
    label_total_ano.pack(pady=20)
    
    frame_form = tk.Frame(frame_left)
    frame_form.pack(pady=10)

    tk.Label(frame_form, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
    entry_nome = tk.Entry(frame_form, width=25)
    entry_nome.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_form, text="Valor:").grid(row=1, column=0, padx=5, pady=5)
    entry_valor = tk.Entry(frame_form, width=25)
    entry_valor.grid(row=1, column=1, padx=5, pady=5)
    entry_valor.insert(0, "R$0,00")
    entry_valor.bind('<KeyRelease>', lambda e: formatar_valor_digitacao(e, entry_valor))

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

    # Frame para filtro
    frame_filtro = tk.Frame(frame_center)
    frame_filtro.pack(pady=10)
    
    tk.Label(frame_filtro, text="Filtrar por nome:").pack(side="left", padx=5)
    entry_filtro = tk.Entry(frame_filtro, width=25)
    entry_filtro.pack(side="left", padx=5)
    tk.Button(frame_filtro, text="Filtrar", command=filtrar_dizimistas).pack(side="left", padx=5)
    tk.Button(frame_filtro, text="Limpar Filtro", command=carregar_dizimistas).pack(side="left", padx=5)

    tabela = ttk.Treeview(frame_center, columns=("ID", "Nome", "Valor", "Data Doação", "Aniversário", "Telefone", "Status"), show="headings")
    tabela.tag_configure('faltando', foreground='red')
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

    tk.Button(frame_center, text="Deletar Dizimista", command=deletar_dizimista, width=20).pack(pady=10)

    carregar_dizimistas()
    atualizar_sumarios()

    dashboard.mainloop()