# TG - Sistema de Notas

Este projeto contém dois diretórios principais:

- `backend`: API em Python/Flask
- `frontend`: Aplicação web em Angular

## Passos para configuração após clonar o repositório

### 1. Backend (Flask)

```bash
cd backend
python -m venv venv
# Ativação do ambiente virtual (Windows)
venv\Scripts\activate
# Instalação das dependências
pip install -r requirements.txt
```

Para rodar o backend:

```bash
python app.py
```

### 2. Frontend (Angular)

```bash
cd frontend
npm install
```

Para rodar o frontend:

```bash
ng serve
```

Iniciar o docker:

```bash
docker compose -f docker-compose.dev.yml up      
```

Após o início, instalar o modelo do chat dentro do container:

```bash
docker exec -it betterstudy-tg-ollama-1 ollama pull gemma2:2b
```

Buildar para confirmar se está tudo correto:
```bash
docker compose -f docker-compose.dev.yml up  --build
```

Acesse o frontend em [http://localhost:4200](http://localhost:4200).

---

**Observações:**
- Certifique-se de ter o Python 3 e o Node.js instalados.
- O backend roda por padrão em `http://localhost:5000` (ou conforme configurado).
- O frontend roda por padrão em `http://localhost:4200`.

