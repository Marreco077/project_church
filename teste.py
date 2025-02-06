import os
import sqlite3
from database import create_database


def reset_database():
    # Nome do arquivo do banco de dados
    db_file = "dizimos.db"

    # Verifica se o arquivo existe antes de tentar deletar
    if os.path.exists(db_file):
        try:
            # Fecha todas as conexões com o banco de dados
            conn = sqlite3.connect(db_file)
            conn.close()

            # Remove o arquivo
            os.remove(db_file)
            print(f"Banco de dados antigo removido com sucesso.")

            # Cria um novo banco de dados
            create_database()
            print(f"Novo banco de dados criado com sucesso.")

        except Exception as e:
            print(f"Erro ao resetar o banco de dados: {e}")
    else:
        print("Banco de dados não encontrado. Criando um novo...")
        create_database()
        print("Novo banco de dados criado com sucesso.")


if __name__ == "__main__":
    reset_database()
