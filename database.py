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


def create_database():
    db_path = resource_path("dizimos.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Tabela de usuários
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    """
    )

    # Inserir usuários padrão se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        usuarios = [("secretario", "admin123"), ("teste", "123")]
        cursor.executemany(
            """
            INSERT INTO usuarios (usuario, senha)
            VALUES (?, ?)
        """,
            usuarios,
        )

    # Tabela de dizimistas com novo campo comunidade
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS dizimistas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            valor REAL NOT NULL,
            data_doacao DATE NOT NULL,
            aniversario DATE NOT NULL,
            telefone TEXT NOT NULL,
            endereco TEXT,
            status_atraso TEXT DEFAULT 'Em dia',
            agente TEXT DEFAULT "Nenhum",
            comunidade TEXT DEFAULT "Nenhuma"
        )
    """
    )

    # Tabela de histórico de doações
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS historico_doacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dizimista_id INTEGER,
            valor REAL NOT NULL,
            data_doacao DATE NOT NULL,
            agente TEXT DEFAULT "Nenhum",
            FOREIGN KEY (dizimista_id) REFERENCES dizimistas(id)
        )
    """
    )

    # Verificar se já existem registros na tabela de histórico
    cursor.execute("SELECT COUNT(*) FROM historico_doacoes")
    count = cursor.fetchone()[0]

    # Se não houver registros no histórico, copiar dados existentes dos dizimistas
    if count == 0:
        cursor.execute("SELECT id, valor, data_doacao, agente FROM dizimistas")
        doacoes_existentes = cursor.fetchall()

        for doacao in doacoes_existentes:
            cursor.execute(
                """
                INSERT INTO historico_doacoes (dizimista_id, valor, data_doacao, agente)
                VALUES (?, ?, ?, ?)
            """,
                doacao,
            )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()
