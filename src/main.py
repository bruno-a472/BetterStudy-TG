from pathlib import Path
import database
import llm

SCRIPT_DIR = Path(__file__).resolve().parent

PROJECT_ROOT = Path(__file__).resolve().parent

DB_FILE_PATH = PROJECT_ROOT / "data" / "escola.db"

DB_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)


def main():
    print(f"Caminho do banco de dados: {DB_FILE_PATH}")

    database.initialize_db(DB_FILE_PATH)
    notas = database.get_data_grades(DB_FILE_PATH)

    if notas:
        llm.create_report_abc(notas)
    else:
        print("Nenhum dado encontrado no banco de dados para análise.")


if __name__ == "__main__":
    main()
