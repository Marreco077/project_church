import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
import sqlite3
import locale
from datetime import datetime, timedelta
import random


def open_dashboard():
    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

    # Definição das cores
    COR_FUNDO = "#f0f2f5"  # Cinza claro para o fundo
    COR_PRIMARIA = "#1a73e8"  # Azul para botões principais
    COR_SECUNDARIA = "#ffffff"  # Branco para cards
    COR_TEXTO = "#202124"  # Cinza escuro para texto
    COR_DESTAQUE = "#e8f0fe"  # Azul claro para hover

    global comunidade_atual
    comunidade_atual = None
    COMUNIDADES = [
        None,
        "São João",
        "São José",
        "Santos Reis",
        "Rosário",
        "Santa Terezinha",
    ]

    def sort_by_column(tree, col):
        """Ordena o conteúdo da treeview quando o cabeçalho da coluna é clicado."""
        if col == "Comunidade":
            global comunidade_atual
            # Encontra o próximo índice na lista de comunidades
            if comunidade_atual not in COMUNIDADES:
                comunidade_atual = COMUNIDADES[0]  # Começa do primeiro
            else:
                atual_index = COMUNIDADES.index(comunidade_atual)
                comunidade_atual = COMUNIDADES[(atual_index + 1) % len(COMUNIDADES)]

            # Atualiza o texto do cabeçalho
            if comunidade_atual:
                tree.heading(col, text=f"{comunidade_atual}")
            else:
                tree.heading(col, text="Comunidade")

            # Filtra os itens
            filtrar_por_comunidade()
            return

        # Código original de ordenação para outras colunas
        if not hasattr(tree, "_sort_dir"):
            tree._sort_dir = {}
        current_dir = tree._sort_dir.get(col, "")

        new_dir = "" if current_dir == "v" else "v"
        tree._sort_dir[col] = new_dir

        for column in tree["columns"]:
            if column == col:
                tree.heading(column, text=f"{column} {'↓' if new_dir == 'v' else '↑'}")
            else:
                tree.heading(column, text=column)

        items = [(tree.set(item, col), item) for item in tree.get_children("")]

        def convert_value(value):
            if col == "ID":
                return int(value)
            elif col == "Valor":
                return float(value.replace("R$", "").replace(".", "").replace(",", "."))
            elif col == "Status":
                return (value != "Faltando", value.lower())
            return value.lower()

        items.sort(key=lambda x: convert_value(x[0]), reverse=(new_dir == "v"))

        for index, (_, item) in enumerate(items):
            tree.move(item, "", index)

    def filtrar_por_comunidade():
        """Filtra os dizimistas pela comunidade selecionada"""
        for item in tabela.get_children():
            tabela.delete(item)

        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()

        if comunidade_atual:
            cursor.execute(
                """
                SELECT id, nome, valor, data_doacao, comunidade, telefone, endereco, status_atraso 
                FROM dizimistas 
                WHERE LOWER(comunidade) = LOWER(?)
            """,
                (comunidade_atual,),
            )
        else:
            cursor.execute(
                "SELECT id, nome, valor, data_doacao, comunidade, telefone, endereco, status_atraso FROM dizimistas"
            )

        rows = cursor.fetchall()
        conn.close()

        tabela.tag_configure("faltando", foreground="red")

        for row in rows:
            valor_formatado = f"R${float(row[2]):,.2f}".replace(".", ",")
            row_formatado = list(row)
            row_formatado[2] = valor_formatado
            item = tabela.insert("", "end", values=row_formatado)

            if row_formatado[7] == "Faltando":
                tabela.item(item, tags=("faltando",))

    # Estilo para botões
    def configurar_botao(botao, cor_bg=COR_PRIMARIA):
        botao.configure(
            bg=cor_bg,
            fg="white",
            relief="flat",
            activebackground=COR_DESTAQUE,
            activeforeground=COR_TEXTO,
            cursor="hand2",
            font=("Arial", 10, "bold"),
        )

    # Estilo para labels
    def configurar_label(label, size=10, bold=False):
        weight = "bold" if bold else "normal"
        label.configure(font=("Arial", size, weight), fg=COR_TEXTO, bg=COR_FUNDO)

    def mostrar_aniversariantes():
        mes_atual = datetime.now().strftime("%m")

        # Criar nova janela
        janela_aniversariantes = tk.Toplevel()
        janela_aniversariantes.title(
            f"Aniversariantes de {datetime.now().strftime('%B')}"
        )
        janela_aniversariantes.geometry("400x300")

        # Criar Treeview
        tree = ttk.Treeview(
            janela_aniversariantes, columns=("Nome", "Aniversário"), show="headings"
        )
        tree.heading("Nome", text="Nome")
        tree.heading("Aniversário", text="Aniversário")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Buscar aniversariantes
        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT nome, aniversario 
            FROM dizimistas 
            WHERE substr(aniversario, 4, 2) = ?
            ORDER BY substr(aniversario, 1, 2)
        """,
            (mes_atual,),
        )

        aniversariantes = cursor.fetchall()
        conn.close()

        for aniversariante in aniversariantes:
            tree.insert("", "end", values=aniversariante)

    def atualizar_status_pagamentos():
        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()
        data_atual = datetime.now()
        limite_atraso = data_atual - timedelta(days=30)

        cursor.execute(
            """
            UPDATE dizimistas 
            SET status_atraso = CASE 
                WHEN date(substr(data_doacao, 7, 4) || '-' || 
                         substr(data_doacao, 4, 2) || '-' || 
                         substr(data_doacao, 1, 2)) < date(?)
                THEN 'Faltando'
                ELSE 'Em dia'
            END
        """,
            (limite_atraso.strftime("%Y-%m-%d"),),
        )

        conn.commit()
        conn.close()

    def atualizar_sumarios():
        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()

        mes_atual = datetime.now().strftime("%m")
        ano_atual = datetime.now().strftime("%Y")

        cursor.execute(
            """
            SELECT 
                COALESCE(SUM(CASE WHEN substr(data_doacao, 4, 2) = ? AND substr(data_doacao, 7, 4) = ? THEN valor END), 0) as total_mes,
                COALESCE(SUM(CASE WHEN substr(data_doacao, 7, 4) = ? THEN valor END), 0) as total_ano
            FROM historico_doacoes
        """,
            (mes_atual, ano_atual, ano_atual),
        )

        total_mes, total_ano = cursor.fetchone()

        label_total_mes.config(
            text=f"Total {datetime.now().strftime('%B/%Y')}:\n{locale.currency(total_mes, grouping=True)}"
        )
        label_total_ano.config(
            text=f"Total {ano_atual}:\n{locale.currency(total_ano, grouping=True)}"
        )

        conn.close()

    def criar_tabela_mensal(frame):
        # Create a frame for the monthly table
        frame_tabela_mensal = tk.Frame(frame, bg=COR_SECUNDARIA, padx=15, pady=15)
        frame_tabela_mensal.pack(pady=20, fill="x")

        # Add title
        label_titulo = tk.Label(
            frame_tabela_mensal,
            text=f"Total Mensal {datetime.now().year}",
            font=("Arial", 12, "bold"),
            bg=COR_SECUNDARIA,
            fg=COR_TEXTO,
        )
        label_titulo.pack(pady=(0, 10))

        # Create Treeview for monthly data
        tree_mensal = ttk.Treeview(
            frame_tabela_mensal, columns=("Mes", "Total"), show="headings", height=12
        )
        tree_mensal.heading("Mes", text="Mês")
        tree_mensal.heading("Total", text="Total")

        tree_mensal.column("Mes", width=100)
        tree_mensal.column("Total", width=100)

        tree_mensal.pack(fill="x")

        return tree_mensal

    def atualizar_tabela_mensal(tree_mensal):
        # Clear existing items
        for item in tree_mensal.get_children():
            tree_mensal.delete(item)

        # Get current year
        ano_atual = datetime.now().year

        # Connect to database
        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()

        # Get monthly totals for current year
        meses = {
            "01": "Janeiro",
            "02": "Fevereiro",
            "03": "Março",
            "04": "Abril",
            "05": "Maio",
            "06": "Junho",
            "07": "Julho",
            "08": "Agosto",
            "09": "Setembro",
            "10": "Outubro",
            "11": "Novembro",
            "12": "Dezembro",
        }

        for mes_num, mes_nome in meses.items():
            cursor.execute(
                """
                SELECT COALESCE(SUM(valor), 0)
                FROM historico_doacoes
                WHERE substr(data_doacao, 4, 2) = ? 
                AND substr(data_doacao, 7, 4) = ?
            """,
                (mes_num, str(ano_atual)),
            )

            total = cursor.fetchone()[0]
            valor_formatado = locale.currency(total, grouping=True)

            tree_mensal.insert("", "end", values=(mes_nome, valor_formatado))

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

            if event.keysym != "BackSpace":
                if cursor_pos in [2, 5]:
                    cursor_pos += 1
            entry.icursor(min(cursor_pos, len(texto)))

    def formatar_valor_digitacao(event, entry):
        texto = entry.get().replace("R$", "").replace(".", "").replace(",", "").strip()

        if not texto:
            entry.delete(0, tk.END)
            entry.insert(0, "R$0,00")
            return

        try:
            valor = int(texto)
            valor_formatado = (
                f"R${valor / 100:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )
            entry.delete(0, tk.END)
            entry.insert(0, valor_formatado)
        except ValueError:
            entry.delete(0, tk.END)
            entry.insert(0, "R$0,00")

    def converter_valor_para_banco(valor):
        valor = valor.replace("R$", "").replace(".", "").replace(",", ".")
        try:
            return float(valor.strip())
        except ValueError:
            raise ValueError(f"Formato de valor inválido: {valor}")

    def filtrar_dizimistas():
        nome_filtro = entry_filtro.get().lower()

        for item in tabela.get_children():
            tabela.delete(item)

        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()

        if nome_filtro:
            cursor.execute(
                """
                SELECT id, nome, valor, data_doacao, comunidade, telefone, endereco, status_atraso 
                FROM dizimistas 
                WHERE LOWER(nome) LIKE ?
            """,
                (f"%{nome_filtro}%",),
            )
        else:
            cursor.execute(
                "SELECT id, nome, valor, data_doacao, comunidade, telefone, endereco, status_atraso FROM dizimistas"
            )

        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            valor_formatado = f"R${float(row[2]):,.2f}".replace(".", ",")
            row_formatado = list(row)
            row_formatado[2] = valor_formatado
            item = tabela.insert("", "end", values=row_formatado)

            if row_formatado[7] == "Faltando":
                tabela.item(item, tags=("faltando",))

    def cancelar_atualizacao():
        # Limpar todos os campos
        entry_nome.delete(0, tk.END)
        entry_valor.delete(0, tk.END)
        entry_valor.insert(0, "R$0,00")
        entry_aniversario.delete(0, tk.END)
        entry_telefone.delete(0, tk.END)
        entry_endereco.delete(0, tk.END)
        entry_agente.delete(0, tk.END)
        entry_comunidade.delete(0, tk.END)

        # Remove os botões de atualização e cancelar
        for widget in frame_form.grid_slaves():
            if isinstance(widget, tk.Button) and (
                widget["text"] == "Confirmar Atualização"
                or widget["text"] == "Cancelar Atualização"
            ):
                widget.destroy()

        # Restaura o botão de cadastrar
        btn_cadastrar = tk.Button(
            frame_form, text="Cadastrar", command=cadastrar_dizimista, width=20, pady=8
        )
        configurar_botao(btn_cadastrar)
        btn_cadastrar.grid(row=8, column=0, columnspan=2, pady=15)

    def atualizar_dizimista():
        selected_item = tabela.selection()
        if not selected_item:
            messagebox.showwarning(
                "Seleção", "Por favor, selecione um dizimista para atualizar."
            )
            return

        item = tabela.item(selected_item)
        dizimista_id = item["values"][0]

        # Preenche os campos do formulário com os dados atuais
        entry_nome.delete(0, tk.END)
        entry_nome.insert(0, item["values"][1])  # Nome

        entry_valor.delete(0, tk.END)
        entry_valor.insert(0, item["values"][2])  # Valor

        entry_data_doacao.delete(0, tk.END)
        entry_data_doacao.insert(0, item["values"][3])  # Data Doação

        # Buscar o aniversário do banco de dados
        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT aniversario FROM dizimistas WHERE id = ?", (dizimista_id,)
        )
        aniversario = cursor.fetchone()[0]

        entry_aniversario.delete(0, tk.END)
        entry_aniversario.insert(0, aniversario)  # Aniversário do banco

        entry_telefone.delete(0, tk.END)
        entry_telefone.insert(0, item["values"][5])  # Telefone

        entry_endereco.delete(0, tk.END)
        entry_endereco.insert(0, item["values"][6])  # Endereço

        entry_comunidade.delete(0, tk.END)
        entry_comunidade.insert(0, item["values"][4])  # Comunidade

        # Buscar o agente do banco de dados
        cursor.execute("SELECT agente FROM dizimistas WHERE id = ?", (dizimista_id,))
        agente = cursor.fetchone()[0]
        conn.close()

        entry_agente.delete(0, tk.END)
        entry_agente.insert(0, agente if agente else "")

        # Remove o botão de cadastrar existente
        for widget in frame_form.grid_slaves():
            if isinstance(widget, tk.Button) and widget["text"] == "Cadastrar":
                widget.destroy()
            elif (
                isinstance(widget, tk.Button)
                and widget["text"] == "Confirmar Atualização"
            ):
                widget.destroy()
            elif (
                isinstance(widget, tk.Button)
                and widget["text"] == "Cancelar Atualização"
            ):
                widget.destroy()

        # Adiciona o botão de confirmar atualização
        btn_confirmar_atualizacao = tk.Button(
            frame_form,
            text="Confirmar Atualização",
            command=lambda: confirmar_atualizacao(dizimista_id),
            width=20,
            pady=8,
        )
        configurar_botao(btn_confirmar_atualizacao)
        btn_confirmar_atualizacao.grid(row=8, column=0, columnspan=2, pady=15)

        # Adiciona o botão de cancelar atualização
        btn_cancelar_atualizacao = tk.Button(
            frame_form,
            text="Cancelar Atualização",
            command=cancelar_atualizacao,
            width=20,
            pady=8,
        )
        configurar_botao(
            btn_cancelar_atualizacao, cor_bg="#dc3545"
        )  # Vermelho para botão de cancelar
        btn_cancelar_atualizacao.grid(row=9, column=0, columnspan=2, pady=15)

    def confirmar_atualizacao(dizimista_id):
        nome = entry_nome.get().title()
        valor = entry_valor.get()
        aniversario = entry_aniversario.get()
        telefone = entry_telefone.get()
        endereco = entry_endereco.get().title()
        agente = entry_agente.get().title()
        comunidade = entry_comunidade.get().title()

        data_doacao = datetime.now().strftime("%d/%m/%Y")

        if not nome or not valor or not aniversario or not telefone or not endereco:
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
            return

        try:
            valor_convertido = converter_valor_para_banco(valor)
            conn = sqlite3.connect("dizimos.db")
            cursor = conn.cursor()

            # Update dizimista
            cursor.execute(
                """
                UPDATE dizimistas 
                SET nome=?, valor=?, data_doacao=?, aniversario=?, telefone=?, endereco=?, agente=?, comunidade=?
                WHERE id=?
            """,
                (
                    nome,
                    valor_convertido,
                    data_doacao,
                    aniversario,
                    telefone,
                    endereco,
                    agente,
                    comunidade,
                    dizimista_id,
                ),
            )

            # Add to historical data
            cursor.execute(
                """
                INSERT INTO historico_doacoes (dizimista_id, valor, data_doacao, agente)
                VALUES (?, ?, ?, ?)
            """,
                (dizimista_id, valor_convertido, data_doacao, agente),
            )

            conn.commit()
            conn.close()

            # Clear fields
            entry_nome.delete(0, tk.END)
            entry_valor.delete(0, tk.END)
            entry_valor.insert(0, "R$0,00")
            entry_aniversario.delete(0, tk.END)
            entry_telefone.delete(0, tk.END)
            entry_endereco.delete(0, tk.END)
            entry_agente.delete(0, tk.END)
            entry_comunidade.delete(0, tk.END)

            # Remove os botões de atualização e cancelar
            for widget in frame_form.grid_slaves():
                if isinstance(widget, tk.Button) and (
                    widget["text"] == "Confirmar Atualização"
                    or widget["text"] == "Cancelar Atualização"
                ):
                    widget.destroy()

            # Restaura o botão de cadastrar
            btn_cadastrar = tk.Button(
                frame_form,
                text="Cadastrar",
                command=cadastrar_dizimista,
                width=20,
                pady=8,
            )
            configurar_botao(btn_cadastrar)
            btn_cadastrar.grid(row=8, column=0, columnspan=2, pady=15)

            carregar_dizimistas()
            messagebox.showinfo("Sucesso", "Dizimista atualizado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar: {e}")

    def carregar_dizimistas():
        atualizar_status_pagamentos()

        # Add this function to ensure the column exists
        def adicionar_coluna_endereco():
            conn = sqlite3.connect("dizimos.db")
            cursor = conn.cursor()

            conn.close()

        # Call the function to add the column if it doesn't exist
        adicionar_coluna_endereco()

        for item in tabela.get_children():
            tabela.delete(item)

        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nome, valor, data_doacao, comunidade, telefone, endereco, status_atraso, agente FROM dizimistas"
        )
        rows = cursor.fetchall()
        conn.close()

        tabela.tag_configure("faltando", foreground="red")

        for row in rows:
            valor_formatado = f"R${float(row[2]):,.2f}".replace(".", ",")
            row_formatado = list(row)
            row_formatado[2] = valor_formatado
            item = tabela.insert("", "end", values=row_formatado)

            if row_formatado[7] == "Faltando":
                tabela.item(item, tags=("faltando",))

        atualizar_sumarios()
        atualizar_tabela_mensal(tree_mensal)

    def cadastrar_dizimista():
        nome = entry_nome.get().title()
        valor = entry_valor.get()
        aniversario = entry_aniversario.get()
        telefone = entry_telefone.get()
        endereco = entry_endereco.get().title()
        agente = entry_agente.get().title()
        comunidade = entry_comunidade.get().title()

        data_doacao = datetime.now().strftime("%d/%m/%Y")

        if not nome or not valor or not aniversario or not telefone or not endereco:
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
            return

        try:
            valor_convertido = converter_valor_para_banco(valor)
            conn = sqlite3.connect("dizimos.db")
            cursor = conn.cursor()

            # Inserir dizimista
            cursor.execute(
                """
                INSERT INTO dizimistas (nome, valor, data_doacao, aniversario, telefone, endereco, agente, comunidade)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    nome,
                    valor_convertido,
                    data_doacao,
                    aniversario,
                    telefone,
                    endereco,
                    agente,
                    comunidade,
                ),
            )

            dizimista_id = cursor.lastrowid

            # Inserir no histórico
            cursor.execute(
                """
                INSERT INTO historico_doacoes (dizimista_id, valor, data_doacao, agente)
                VALUES (?, ?, ?, ?)
            """,
                (dizimista_id, valor_convertido, data_doacao, agente),
            )

            conn.commit()
            conn.close()

            # Limpar campos
            entry_nome.delete(0, tk.END)
            entry_valor.delete(0, tk.END)
            entry_valor.insert(0, "R$0,00")
            entry_data_doacao.delete(0, tk.END)
            entry_aniversario.delete(0, tk.END)
            entry_telefone.delete(0, tk.END)
            entry_endereco.delete(0, tk.END)
            entry_agente.delete(0, tk.END)
            entry_comunidade.delete(0, tk.END)

            carregar_dizimistas()
            messagebox.showinfo("Sucesso", "Dizimista cadastrado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar: {e}")

    def deletar_dizimista():
        selected_item = tabela.selection()
        if not selected_item:
            messagebox.showwarning(
                "Seleção", "Por favor, selecione um dizimista para excluir."
            )
            return

        if messagebox.askyesno(
            "Confirmar",
            "Tem certeza que deseja excluir este dizimista? Isso também removerá todo o histórico de doações.",
        ):
            item = tabela.item(selected_item)
            dizimista_id = item["values"][0]

            try:
                conn = sqlite3.connect("dizimos.db")
                cursor = conn.cursor()

                # Primeiro, excluir todos os registros do histórico relacionados ao dizimista
                cursor.execute(
                    "DELETE FROM historico_doacoes WHERE dizimista_id = ?",
                    (dizimista_id,),
                )

                # Depois, excluir o dizimista
                cursor.execute("DELETE FROM dizimistas WHERE id = ?", (dizimista_id,))

                conn.commit()
                conn.close()

                carregar_dizimistas()  # Isso já atualiza a tabela mensal e os sumários
                messagebox.showinfo(
                    "Sucesso", "Dizimista e seu histórico foram excluídos com sucesso!"
                )
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {e}")

    def sortear_dizimista():
        global janela_selecao, frame_botoes

        # Criar janela de seleção
        janela_selecao = Toplevel()
        janela_selecao.title("Selecionar Comunidade para Sorteio")
        janela_selecao.geometry("400x500")
        janela_selecao.configure(bg=COR_FUNDO)
        janela_selecao.resizable(False, False)
        janela_selecao.grab_set()

        # Centralizar a janela
        janela_selecao.update_idletasks()
        width = janela_selecao.winfo_width()
        height = janela_selecao.winfo_height()
        x = (janela_selecao.winfo_screenwidth() // 2) - (width // 2)
        y = (janela_selecao.winfo_screenheight() // 2) - (height // 2)
        janela_selecao.geometry(f"{width}x{height}+{x}+{y}")

        # Frame para os botões
        frame_botoes = tk.Frame(janela_selecao, bg=COR_FUNDO)
        frame_botoes.pack(expand=True, fill="both", padx=20, pady=20)

        # Label de instrução
        label_instrucao = tk.Label(
            frame_botoes,
            text="Selecione a comunidade para o sorteio:",
            font=("Arial", 12, "bold"),
            bg=COR_FUNDO,
            fg=COR_TEXTO,
        )
        label_instrucao.pack(pady=10)

        comunidades = [
            "São João",
            "Santa Terezinha",
            "São José",
            "Santos Reis",
            "Rosário",
            "Todos",
        ]

        # Criar botões para cada comunidade
        for comunidade in comunidades:
            btn = tk.Button(
                frame_botoes,
                text=comunidade,
                font=("Arial", 12),
                width=20,
                command=lambda c=comunidade: realizar_sorteio(c),
            )
            btn.pack(pady=5)

    def realizar_sorteio(comunidade=None):
        global janela_selecao

        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()

        if comunidade and comunidade != "Todos":
            cursor.execute(
                """
                SELECT id, nome, telefone, endereco 
                FROM dizimistas 
                WHERE comunidade = ?
            """,
                (comunidade,),
            )
        else:
            cursor.execute("SELECT id, nome, telefone, endereco FROM dizimistas")

        dizimistas = cursor.fetchall()
        conn.close()

        if not dizimistas:
            messagebox.showwarning(
                "Aviso", "Não há dizimistas cadastrados nesta comunidade!"
            )
            return

        sorteado = random.choice(dizimistas)

        # Fechar janela de seleção
        if janela_selecao:
            janela_selecao.destroy()

        # Criar janela do resultado
        popup = Toplevel()
        popup.title("Resultado do Sorteio")
        popup.geometry("400x300")
        popup.configure(bg=COR_SECUNDARIA)
        popup.resizable(False, False)
        popup.grab_set()

        # Centralizar a janela de resultado
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")

        # Texto do vencedor
        comunidade_texto = (
            f"\nComunidade {comunidade}" if comunidade and comunidade != "Todos" else ""
        )
        mensagem = f"""O vencedor do sorteio da {comunidade_texto}:
        
    Nome: {sorteado[1]}
    Telefone: {sorteado[2]}
    Endereço: {sorteado[3]}"""

        label = tk.Label(
            popup,
            text=mensagem,
            font=("Arial", 14, "bold"),
            bg=COR_SECUNDARIA,
            fg=COR_TEXTO,
            wraplength=350,
            justify="center",
        )
        label.pack(pady=20)

        button = tk.Button(
            popup, text="OK", command=popup.destroy, width=10, font=("Arial", 12)
        )
        button.pack(pady=10)

    def mostrar_ficha_dizimista():
        selected_item = tabela.selection()
        if not selected_item:
            messagebox.showwarning(
                "Seleção", "Por favor, selecione um dizimista para ver a ficha."
            )
            return

        item = tabela.item(selected_item)
        dizimista_dados = item["values"]

        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT aniversario FROM dizimistas WHERE id = ?", (dizimista_dados[0],)
        )
        aniversario = cursor.fetchone()[0]
        conn.close()

        ficha_window = tk.Toplevel()
        ficha_window.title(f"Ficha do Dizimista - {dizimista_dados[1]}")
        ficha_window.geometry("800x800")
        ficha_window.configure(bg=COR_FUNDO)

        frame_info = tk.Frame(ficha_window, bg=COR_SECUNDARIA, padx=20, pady=20)
        frame_info.pack(expand=False, fill="x", padx=20, pady=20)

        # Atualizado para mostrar os campos corretos com seus respectivos índices
        informacoes = [
            ("ID:", dizimista_dados[0]),
            ("Nome:", dizimista_dados[1]),
            ("Comunidade:", dizimista_dados[4]),
            ("Aniversário:", aniversario),
            ("Telefone:", dizimista_dados[5]),
            ("Endereço:", dizimista_dados[6]),
            ("Status de Pagamento:", dizimista_dados[7]),
        ]
        for i, (label_text, valor) in enumerate(informacoes):
            label_nome = tk.Label(
                frame_info,
                text=label_text,
                font=("Arial", 12, "bold"),
                bg=COR_SECUNDARIA,
                fg=COR_TEXTO,
            )
            label_nome.grid(row=i, column=0, sticky="w", pady=5)

            label_valor = tk.Label(
                frame_info,
                text=str(valor),
                font=("Arial", 12),
                bg=COR_SECUNDARIA,
                fg=COR_TEXTO,
            )
            label_valor.grid(row=i, column=1, sticky="w", pady=5, padx=10)

        frame_historico = tk.Frame(ficha_window, bg=COR_SECUNDARIA, padx=20, pady=20)
        frame_historico.pack(expand=True, fill="both", padx=20, pady=20)

        label_historico = tk.Label(
            frame_historico,
            text="Histórico de Doações",
            font=("Arial", 14, "bold"),
            bg=COR_SECUNDARIA,
            fg=COR_TEXTO,
        )
        label_historico.pack(pady=10)

        tree_historico = ttk.Treeview(
            frame_historico, columns=("Data", "Valor", "Agente"), show="headings"
        )
        tree_historico.heading("Data", text="Data da Doação")
        tree_historico.heading("Valor", text="Valor")
        tree_historico.heading("Agente", text="Agente")

        tree_historico.column("Data", width=150)
        tree_historico.column("Valor", width=150)
        tree_historico.column("Agente", width=150)

        tree_historico.pack(fill="both", expand=True)

        conn = sqlite3.connect("dizimos.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT data_doacao, valor, agente 
            FROM historico_doacoes 
            WHERE dizimista_id = ? 
            ORDER BY date(substr(data_doacao, 7, 4) || '-' || substr(data_doacao, 4, 2) || '-' || substr(data_doacao, 1, 2)) DESC
        """,
            (dizimista_dados[0],),
        )

        historico = cursor.fetchall()
        conn.close()

        total_doacoes = 0
        for data, valor, agente in historico:
            valor_formatado = f"R${float(valor):,.2f}".replace(".", ",")
            tree_historico.insert(
                "", "end", values=(data, valor_formatado, agente or "Nenhum")
            )
            total_doacoes += valor

        total_formatado = f"R${float(total_doacoes):,.2f}".replace(".", ",")
        label_total = tk.Label(
            frame_historico,
            text=f"Total de Doações: {total_formatado}",
            font=("Arial", 12, "bold"),
            bg=COR_SECUNDARIA,
            fg=COR_TEXTO,
        )
        label_total.pack(pady=10)

        btn_fechar = tk.Button(
            ficha_window, text="Fechar", command=ficha_window.destroy, width=20
        )
        configurar_botao(btn_fechar)
        btn_fechar.pack(pady=20)

    dashboard = tk.Tk()
    dashboard.title("Gerenciador de Dízimos")
    dashboard.configure(bg=COR_FUNDO)

    # Configuração do tamanho e posição
    largura = 1600
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
        bd=0,
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
        bd=0,
    )
    label_total_ano.pack(pady=20)

    tree_mensal = criar_tabela_mensal(frame_right)
    # Botão de aniversariantes estilizado
    btn_aniversariantes = tk.Button(
        frame_right,
        text="Aniversariantes do Mês",
        command=mostrar_aniversariantes,
        width=20,
        pady=8,
    )
    configurar_botao(btn_aniversariantes)
    btn_aniversariantes.pack(pady=10)

    # Frame do formulário com fundo branco
    frame_form = tk.Frame(frame_left, bg=COR_SECUNDARIA, padx=15, pady=15)
    frame_form.pack(pady=10)

    # Estilização dos campos do formulário
    for i, texto in enumerate(
        [
            "Nome:",
            "Valor:",
            "Data Doação:",
            "Aniversário:",
            "Telefone:",
            "Endereço:",
            "Agente:",
            "Comunidade:",
        ]
    ):
        label = tk.Label(frame_form, text=texto, bg=COR_SECUNDARIA)
        configurar_label(label)
        label.grid(row=i, column=0, padx=8, pady=8, sticky="e")

    # Entradas do formulário
    entries = [
        ("entry_nome", None),
        ("entry_valor", lambda e: formatar_valor_digitacao(e, entry_valor)),
        ("entry_data_doacao", None),
        ("entry_aniversario", lambda e: formatar_data_digitacao(e, entry_aniversario)),
        ("entry_telefone", None),
        ("entry_endereco", None),
        ("entry_agente", None),
        ("entry_comunidade", None),
    ]

    for i, (nome, comando) in enumerate(entries):
        entry = tk.Entry(frame_form, width=25, font=("Arial", 10), state="normal")
        entry.grid(row=i, column=1, padx=8, pady=8)
        if comando:
            entry.bind("<KeyRelease>", comando)
        globals()[nome] = entry

    entry_data_doacao.delete(0, tk.END)
    entry_data_doacao.insert(0, datetime.now().strftime("%d/%m/%Y"))
    entry_data_doacao.configure(state="readonly")

    entry_valor.insert(0, "R$0,00")

    # Botão de cadastro estilizado
    btn_cadastrar = tk.Button(
        frame_form, text="Cadastrar", command=cadastrar_dizimista, width=20, pady=8
    )
    configurar_botao(btn_cadastrar)
    btn_cadastrar.grid(row=8, column=0, columnspan=2, pady=15)

    # Frame de filtro estilizado
    frame_filtro = tk.Frame(frame_center, bg=COR_SECUNDARIA, padx=15, pady=15)
    frame_filtro.pack(pady=15, fill="x")

    label_filtro = tk.Label(frame_filtro, text="Filtrar por nome:", bg=COR_SECUNDARIA)
    configurar_label(label_filtro)
    label_filtro.pack(side="left", padx=8)

    entry_filtro = tk.Entry(frame_filtro, width=25, font=("Arial", 10))
    entry_filtro.pack(side="left", padx=8)

    btn_filtrar = tk.Button(
        frame_filtro, text="Filtrar", command=filtrar_dizimistas, width=10
    )
    configurar_botao(btn_filtrar)
    btn_filtrar.pack(side="left", padx=8)

    btn_limpar = tk.Button(
        frame_filtro, text="Limpar Filtro", command=carregar_dizimistas, width=12
    )
    configurar_botao(btn_limpar, cor_bg="#6c757d")  # Cinza para botão secundário
    btn_limpar.pack(side="left", padx=8)

    # Estilo para a tabela
    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "Treeview",
        background=COR_SECUNDARIA,
        foreground=COR_TEXTO,
        rowheight=25,
        fieldbackground=COR_SECUNDARIA,
    )
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
    style.map("Treeview", background=[("selected", COR_PRIMARIA)])

    tabela = ttk.Treeview(
        frame_center,
        columns=(
            "ID",
            "Nome",
            "Valor",
            "Data Doação",
            "Comunidade",
            "Telefone",
            "Endereço",
            "Status",
        ),
        show="headings",
    )
    tabela.tag_configure("faltando", foreground="red")
    tabela.pack(fill="both", expand=True, padx=10, pady=10)

    for col in [
        "ID",
        "Nome",
        "Valor",
        "Data Doação",
        "Comunidade",
        "Telefone",
        "Endereço",
        "Status",
    ]:
        tabela.heading(col, text=col, command=lambda c=col: sort_by_column(tabela, c))

    tabela.column("ID", width=25)
    tabela.column("Nome", width=160)
    tabela.column("Valor", width=80)
    tabela.column("Data Doação", width=100)
    tabela.column("Comunidade", width=100)
    tabela.column("Telefone", width=100)
    tabela.column("Endereço", width=200)
    tabela.column("Status", width=80)

    # Botão de atualizar estilizado
    btn_atualizar = tk.Button(
        frame_center, text="Atualizar Dizimista", command=atualizar_dizimista, width=20
    )
    configurar_botao(btn_atualizar, cor_bg="#28a745")  # Verde para botão de atualizar
    btn_atualizar.pack(pady=15)
    # Botão de deletar estilizado
    btn_deletar = tk.Button(
        frame_center, text="Deletar Dizimista", command=deletar_dizimista, width=20
    )
    configurar_botao(btn_deletar, cor_bg="#dc3545")  # Vermelho para botão de deletar
    btn_deletar.pack(pady=15)

    btn_sortear = tk.Button(
        frame_center, text="Sortear Dizimista", command=sortear_dizimista, width=20
    )
    configurar_botao(btn_sortear, cor_bg="#6f42c1")  # Roxo para botão de sorteio
    btn_sortear.pack(pady=15)

    btn_ficha = tk.Button(
        frame_center, text="Ficha Dizimista", command=mostrar_ficha_dizimista, width=20
    )
    configurar_botao(btn_ficha, cor_bg="#17a2b8")  # Azul claro para o botão de ficha
    btn_ficha.pack(pady=15)

    carregar_dizimistas()
    atualizar_sumarios()

    dashboard.mainloop()
