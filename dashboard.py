import tkinter as tk 
from tkinter import ttk, messagebox
import sqlite3
import locale
from datetime import datetime, timedelta

def open_dashboard():
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    
    # Definição das cores
    COR_FUNDO = "#f0f2f5"  # Cinza claro para o fundo
    COR_PRIMARIA = "#1a73e8"  # Azul para botões principais
    COR_SECUNDARIA = "#ffffff"  # Branco para cards
    COR_TEXTO = "#202124"  # Cinza escuro para texto
    COR_DESTAQUE = "#e8f0fe"  # Azul claro para hover
    
    def sort_by_column(tree, col):
        """Ordena o conteúdo da treeview quando o cabeçalho da coluna é clicado."""
        # Obtém a direção atual da ordenação (^ para ascendente, v para descendente)
        if not hasattr(tree, '_sort_dir'):
            tree._sort_dir = {}
        current_dir = tree._sort_dir.get(col, '')
        
        # Alterna a direção
        new_dir = '' if current_dir == 'v' else 'v'
        tree._sort_dir[col] = new_dir
        
        # Atualiza o texto do cabeçalho com a seta de direção
        for column in tree['columns']:
            if column == col:
                tree.heading(column, text=f"{column} {'↓' if new_dir == 'v' else '↑'}")
            else:
                tree.heading(column, text=column)
        
        # Obtém todos os itens da árvore
        items = [(tree.set(item, col), item) for item in tree.get_children('')]
        
        # Define a função de ordenação baseada no tipo de coluna
        def convert_value(value):
            if col == "ID":
                return int(value)
            elif col == "Valor":
                return float(value.replace("R$", "").replace(".", "").replace(",", "."))
            elif col == "Status":
                return (value != "Faltando", value.lower())  # Mantém "Faltando" sempre no topo
            return value.lower()  # Para outras colunas, converte para minúsculo
        
        # Ordena os itens
        items.sort(key=lambda x: convert_value(x[0]), reverse=(new_dir == 'v'))
        
        # Reorganiza os itens nas posições ordenadas
        for index, (_, item) in enumerate(items):
            tree.move(item, '', index)

    # Estilo para botões
    def configurar_botao(botao, cor_bg=COR_PRIMARIA):
        botao.configure(
            bg=cor_bg,
            fg="white",
            relief="flat",
            activebackground=COR_DESTAQUE,
            activeforeground=COR_TEXTO,
            cursor="hand2",
            font=("Arial", 10, "bold")
        )
    
    # Estilo para labels
    def configurar_label(label, size=10, bold=False):
        weight = "bold" if bold else "normal"
        label.configure(
            font=("Arial", size, weight),
            fg=COR_TEXTO,
            bg=COR_FUNDO
        )
    
    def mostrar_aniversariantes():
        mes_atual = datetime.now().strftime('%m')
        
        # Criar nova janela
        janela_aniversariantes = tk.Toplevel()
        janela_aniversariantes.title(f"Aniversariantes de {datetime.now().strftime('%B')}")
        janela_aniversariantes.geometry("400x300")
        
        # Criar Treeview
        tree = ttk.Treeview(janela_aniversariantes, columns=("Nome", "Aniversário"), show="headings")
        tree.heading("Nome", text="Nome")
        tree.heading("Aniversário", text="Aniversário")
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Buscar aniversariantes
        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nome, aniversario 
            FROM dizimistas 
            WHERE substr(aniversario, 4, 2) = ?
            ORDER BY substr(aniversario, 1, 2)
        """, (mes_atual,))
        
        aniversariantes = cursor.fetchall()
        conn.close()
        
        for aniversariante in aniversariantes:
            tree.insert("", "end", values=aniversariante)
    
    def atualizar_status_pagamentos():
        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()
        data_atual = datetime.now()
        limite_atraso = data_atual - timedelta(days=30)
        
        cursor.execute("""
            UPDATE dizimistas 
            SET status_atraso = CASE 
                WHEN date(substr(data_doacao, 7, 4) || '-' || 
                         substr(data_doacao, 4, 2) || '-' || 
                         substr(data_doacao, 1, 2)) < date(?)
                THEN 'Faltando'
                ELSE 'Em dia'
            END
        """, (limite_atraso.strftime('%Y-%m-%d'),))
        
        conn.commit()
        conn.close()
    
    def atualizar_sumarios():
        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()
        
        mes_atual = datetime.now().strftime('%m')
        ano_atual = datetime.now().strftime('%Y')
        
        cursor.execute("""
            SELECT COALESCE(SUM(valor), 0) FROM dizimistas 
            WHERE substr(data_doacao, 4, 2) = ? 
            AND substr(data_doacao, 7, 4) = ?
        """, (mes_atual, ano_atual))
        
        total_mes = cursor.fetchone()[0]
        label_total_mes.config(text=f"Total {datetime.now().strftime('%B/%Y')}:\n{locale.currency(total_mes, grouping=True)}")
        
        cursor.execute("""
            SELECT COALESCE(SUM(valor), 0) FROM dizimistas 
            WHERE substr(data_doacao, 7, 4) = ?
        """, (ano_atual,))
        
        total_ano = cursor.fetchone()[0]
        label_total_ano.config(text=f"Total {ano_atual}:\n{locale.currency(total_ano, grouping=True)}")
        
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
            item = tabela.insert("", "end", values=row_formatado)
            
            if row_formatado[6] == 'Faltando':
                tabela.item(item, tags=('faltando',))


    def atualizar_dizimista():
        selected_item = tabela.selection()
        if not selected_item:
            messagebox.showwarning("Seleção", "Por favor, selecione um dizimista para atualizar.")
            return
        
        item = tabela.item(selected_item)
        dizimista_id = item['values'][0]
        
        # Preenche os campos do formulário com os dados atuais
        entry_nome.delete(0, tk.END)
        entry_nome.insert(0, item['values'][1])
        
        entry_valor.delete(0, tk.END)
        entry_valor.insert(0, item['values'][2])
        
        entry_data_doacao.delete(0, tk.END)
        entry_data_doacao.insert(0, item['values'][3])
        
        entry_aniversario.delete(0, tk.END)
        entry_aniversario.insert(0, item['values'][4])
        
        entry_telefone.delete(0, tk.END)
        entry_telefone.insert(0, item['values'][5])
        
        # Cria um botão de confirmação de atualização
        btn_confirmar_atualizacao = tk.Button(
            frame_form, 
            text="Confirmar Atualização", 
            command=lambda: confirmar_atualizacao(dizimista_id), 
            width=20, 
            pady=8
        )
        configurar_botao(btn_confirmar_atualizacao)
        btn_confirmar_atualizacao.grid(row=5, column=0, columnspan=2, pady=15)
        
    def confirmar_atualizacao(dizimista_id):
        nome = entry_nome.get()
        valor = entry_valor.get()
        data_doacao = entry_data_doacao.get()
        aniversario = entry_aniversario.get()
        telefone = entry_telefone.get()
        
        if not nome or not valor or not data_doacao or not aniversario or not telefone:
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
            return
        
        try:
            valor_convertido = converter_valor_para_banco(valor)
            conn = sqlite3.connect("dizimos.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE dizimistas 
                SET nome=?, valor=?, data_doacao=?, aniversario=?, telefone=?
                WHERE id=?
            """, (nome, valor_convertido, data_doacao, aniversario, telefone, dizimista_id))
            
            conn.commit()
            conn.close()
            
            # Limpa os campos e recarrega a tabela
            entry_nome.delete(0, tk.END)
            entry_valor.delete(0, tk.END)
            entry_valor.insert(0, "R$0,00")
            entry_data_doacao.delete(0, tk.END)
            entry_aniversario.delete(0, tk.END)
            entry_telefone.delete(0, tk.END)
            
            # Remove o botão de confirmação
            btn_confirmar_atualizacao = frame_form.grid_slaves(row=5, column=0)[0]
            btn_confirmar_atualizacao.grid_forget()
            
            carregar_dizimistas()
            messagebox.showinfo("Sucesso", "Dizimista atualizado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar: {e}")

    def carregar_dizimistas():
        atualizar_status_pagamentos()
        for item in tabela.get_children():
            tabela.delete(item)
        
        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, valor, data_doacao, aniversario, telefone, status_atraso FROM dizimistas")
        rows = cursor.fetchall()
        conn.close()
        
        tabela.tag_configure('faltando', foreground='red')
        
        for row in rows:
            valor_formatado = f"R${float(row[2]):,.2f}".replace(".", ",")
            row_formatado = list(row)
            row_formatado[2] = valor_formatado
            item = tabela.insert("", "end", values=row_formatado)
            
            if row_formatado[6] == 'Faltando':
                tabela.item(item, tags=('faltando',))
        
        atualizar_sumarios()

    def cadastrar_dizimista():
        nome = entry_nome.get()
        valor = entry_valor.get()
        data_doacao = entry_data_doacao.get()
        aniversario = entry_aniversario.get()
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
            
            entry_nome.delete(0, tk.END)
            entry_valor.delete(0, tk.END)
            entry_valor.insert(0, "R$0,00")
            entry_data_doacao.delete(0, tk.END)
            entry_aniversario.delete(0, tk.END)
            entry_telefone.delete(0, tk.END)
            
            carregar_dizimistas()
            messagebox.showinfo("Sucesso", "Dizimista cadastrado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar: {e}")

    def deletar_dizimista():
        selected_item = tabela.selection()
        if not selected_item:
            messagebox.showwarning("Seleção", "Por favor, selecione um dizimista para excluir.")
            return
        
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este dizimista?"):
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
    dashboard.configure(bg=COR_FUNDO)
    
    # Configuração do tamanho e posição
    largura = 1400
    altura = 800
    screen_width = dashboard.winfo_screenwidth()
    screen_height = dashboard.winfo_screenheight()
    pos_x = (screen_width // 2) - (largura // 2)
    pos_y = (screen_height // 2) - (altura // 2)
    dashboard.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
    
    # Frames principais com cores
    frame_left = tk.Frame(dashboard, bg=COR_FUNDO)
    frame_left.pack(side="left", padx=20, fill="y")
    
    frame_right = tk.Frame(dashboard, bg=COR_FUNDO)
    frame_right.pack(side="right", padx=20, fill="y")
    
    frame_center = tk.Frame(dashboard, bg=COR_FUNDO)
    frame_center.pack(expand=True, fill="both", padx=20)

    # Card para totais com sombra e cantos arredondados
    label_total_mes = tk.Label(
        frame_left,
        font=("Arial", 14, "bold"),
        relief="solid",
        padx=20,
        pady=20,
        bg=COR_SECUNDARIA,
        fg=COR_TEXTO,
        bd=0
    )
    label_total_mes.pack(pady=20)
    
    label_total_ano = tk.Label(
        frame_right,
        font=("Arial", 14, "bold"),
        relief="solid",
        padx=20,
        pady=20,
        bg=COR_SECUNDARIA,
        fg=COR_TEXTO,
        width=20,
        bd=0
    )
    label_total_ano.pack(pady=20)
    
    # Botão de aniversariantes estilizado
    btn_aniversariantes = tk.Button(
        frame_right,
        text="Aniversariantes do Mês",
        command=mostrar_aniversariantes,
        width=20,
        pady=8
    )
    configurar_botao(btn_aniversariantes)
    btn_aniversariantes.pack(pady=10)
    
    # Frame do formulário com fundo branco
    frame_form = tk.Frame(frame_left, bg=COR_SECUNDARIA, padx=15, pady=15)
    frame_form.pack(pady=10)

    # Estilização dos campos do formulário
    for i, texto in enumerate(["Nome:", "Valor:", "Data Doação:", "Aniversário:", "Telefone:"]):
        label = tk.Label(frame_form, text=texto, bg=COR_SECUNDARIA)
        configurar_label(label)
        label.grid(row=i, column=0, padx=8, pady=8, sticky="e")

    # Entradas do formulário
    entries = [
        ("entry_nome", None),
        ("entry_valor", lambda e: formatar_valor_digitacao(e, entry_valor)),
        ("entry_data_doacao", lambda e: formatar_data_digitacao(e, entry_data_doacao)),
        ("entry_aniversario", lambda e: formatar_data_digitacao(e, entry_aniversario)),
        ("entry_telefone", None)
    ]

    for i, (nome, comando) in enumerate(entries):
        entry = tk.Entry(frame_form, width=25, font=("Arial", 10))
        entry.grid(row=i, column=1, padx=8, pady=8)
        if comando:
            entry.bind('<KeyRelease>', comando)
        globals()[nome] = entry

    entry_valor.insert(0, "R$0,00")

    # Botão de cadastro estilizado
    btn_cadastrar = tk.Button(frame_form, text="Cadastrar", command=cadastrar_dizimista, width=20, pady=8)
    configurar_botao(btn_cadastrar)
    btn_cadastrar.grid(row=5, column=0, columnspan=2, pady=15)

    # Frame de filtro estilizado
    frame_filtro = tk.Frame(frame_center, bg=COR_SECUNDARIA, padx=15, pady=15)
    frame_filtro.pack(pady=15, fill="x")
    
    label_filtro = tk.Label(frame_filtro, text="Filtrar por nome:", bg=COR_SECUNDARIA)
    configurar_label(label_filtro)
    label_filtro.pack(side="left", padx=8)
    
    entry_filtro = tk.Entry(frame_filtro, width=25, font=("Arial", 10))
    entry_filtro.pack(side="left", padx=8)
    
    btn_filtrar = tk.Button(frame_filtro, text="Filtrar", command=filtrar_dizimistas, width=10)
    configurar_botao(btn_filtrar)
    btn_filtrar.pack(side="left", padx=8)
    
    btn_limpar = tk.Button(frame_filtro, text="Limpar Filtro", command=carregar_dizimistas, width=12)
    configurar_botao(btn_limpar, cor_bg="#6c757d")  # Cinza para botão secundário
    btn_limpar.pack(side="left", padx=8)

    # Estilo para a tabela
    style = ttk.Style()
    style.theme_use('default')
    style.configure(
        "Treeview",
        background=COR_SECUNDARIA,
        foreground=COR_TEXTO,
        rowheight=25,
        fieldbackground=COR_SECUNDARIA
    )
    style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
    style.map('Treeview', background=[('selected', COR_PRIMARIA)])

    tabela = ttk.Treeview(frame_center, columns=("ID", "Nome", "Valor", "Data Doação", "Aniversário", "Telefone", "Status"), show="headings")
    tabela.tag_configure('faltando', foreground='red')
    tabela.pack(fill="both", expand=True, padx=10, pady=10)

    for col in ["ID", "Nome", "Valor", "Data Doação", "Aniversário", "Telefone", "Status"]:
        tabela.heading(col, text=col, command=lambda c=col: sort_by_column(tabela, c))

    tabela.column("ID", width=30)
    tabela.column("Nome", width=150)
    tabela.column("Valor", width=70)
    tabela.column("Data Doação", width=100)
    tabela.column("Aniversário", width=100)
    tabela.column("Telefone", width=100)
    tabela.column("Status", width=80)


    # Botão de atualizar estilizado
    btn_atualizar = tk.Button(frame_center, text="Atualizar Dizimista", command=atualizar_dizimista, width=20)
    configurar_botao(btn_atualizar, cor_bg="#28a745")  # Verde para botão de atualizar
    btn_atualizar.pack(pady=15)
    # Botão de deletar estilizado
    btn_deletar = tk.Button(frame_center, text="Deletar Dizimista", command=deletar_dizimista, width=20)
    configurar_botao(btn_deletar, cor_bg="#dc3545")  # Vermelho para botão de deletar
    btn_deletar.pack(pady=15)

    carregar_dizimistas()
    atualizar_sumarios()

    dashboard.mainloop()