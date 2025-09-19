from flask import Flask, request, jsonify
import llm  

app = Flask(__name__)


@app.route("/")
def health_check():
    return jsonify(
        {
            "status": "ok",
            "message": "Serviço de IA para Análise de Desempenho está online!",
        }
    )


@app.route("/analise", methods=["POST"])
def gerar_relatorio_api():
    """
    Endpoint principal que recebe os dados do aluno e retorna a análise.
    """
    print("Recebida requisição para gerar relatório de desempenho...")
    dados_recebidos = request.get_json()

    if not dados_recebidos or (
        "parciais" not in dados_recebidos and "historicas" not in dados_recebidos
    ):
        return jsonify(
            {"erro": "A requisição deve conter as chaves 'parciais' e/ou 'historicas'."}
        ), 400

    disciplinas_parciais = dados_recebidos.get("parciais", [])
    disciplinas_historicas = dados_recebidos.get("historicas", [])
    todas_as_disciplinas = disciplinas_historicas + disciplinas_parciais

    if not todas_as_disciplinas:
        return jsonify({"erro": "Nenhuma disciplina foi fornecida para análise."}), 400

    report_content, status_code = llm.generate_ollama_report(todas_as_disciplinas)

    if status_code == 200:
        return jsonify({"relatorio_desempenho": report_content}), 200
    else:
        return jsonify({"erro": report_content}), status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
