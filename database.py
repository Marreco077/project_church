import sqlite3

def create_database():
    conn = sqlite3.connect("dizimos.db")
    cursor = conn.cursor()
    
    # Tabela de usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    """)
    
    # Tabela de dizimistas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dizimistas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            valor REAL NOT NULL,
            data_doacao DATE NOT NULL,
            aniversario DATE NOT NULL,
            telefone TEXT NOT NULL,
            status_atraso TEXT DEFAULT 'Em dia'
        )
    """)
    
    # Adiciona o usuário padrão, se não existir
    cursor.execute("""
        INSERT OR IGNORE INTO usuarios (usuario, senha)
        VALUES ('teste', '123')
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
