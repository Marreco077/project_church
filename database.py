import sqlite3

def create_database():
    conn = sqlite3.connect("dizimos.db")
    cursor = conn.cursor()
    
    # Tabela de dizimistas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dizimistas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            valor REAL NOT NULL,
            data_doacao DATE NOT NULL,
            aniversario DATE NOT NULL,
            telefone TEXT NOT NULL,
            endereco TEXT,
            status_atraso TEXT DEFAULT 'Em dia',
            agente TEXT DEFAULT "Nenhum"
        )
    """)
    
    # Tabela de histórico de doações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_doacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dizimista_id INTEGER,
            valor REAL NOT NULL,
            data_doacao DATE NOT NULL,
            agente TEXT DEFAULT "Nenhum",
            FOREIGN KEY (dizimista_id) REFERENCES dizimistas(id)
        )
    """)
    
    # Verificar se já existem registros na tabela de histórico
    cursor.execute("SELECT COUNT(*) FROM historico_doacoes")
    count = cursor.fetchone()[0]
    
    # Se não houver registros no histórico, copiar dados existentes dos dizimistas
    if count == 0:
        cursor.execute("SELECT id, valor, data_doacao, agente FROM dizimistas")
        doacoes_existentes = cursor.fetchall()
        
        for doacao in doacoes_existentes:
            cursor.execute("""
                INSERT INTO historico_doacoes (dizimista_id, valor, data_doacao, agente)
                VALUES (?, ?, ?, ?)
            """, doacao)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()