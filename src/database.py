import sqlite3


def initialize_db(db_path: str):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY,
            aluno TEXT,
            atividade TEXT,
            custo REAL,
            nota REAL
        )
        """)

        cursor.execute("SELECT COUNT(*) FROM notas")
        if cursor.fetchone()[0] == 0:
            print("Banco de dados vazio. Inserindo dados de exemplo...")
            template_data = [
                ("Ana", "Prova Matemática", 50, 8.5),
                ("Ana", "Trabalho História", 30, 9.0),
                ("João", "Prova Matemática", 50, 7.0),
                ("João", "Trabalho História", 30, 8.0),
                ("Maria", "Prova Matemática", 50, 6.5),
                ("Maria", "Trabalho História", 30, 7.5),
            ]
            cursor.executemany(
                "INSERT INTO notas (aluno, atividade, custo, nota) VALUES (?, ?, ?, ?)",
                template_data,
            )
            print("Dados inseridos com sucesso.")


def get_data_grades(db_path: str) -> list:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT aluno, atividade, custo, nota FROM notas")
        return cursor.fetchall()
