# Imagem base com Python
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg2 \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxss1 \
    fonts-liberation \
    libasound2 \
    xdg-utils \
    libu2f-udev \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Definir variáveis para Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos do projeto
COPY . /app

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta (Render automaticamente redireciona para 10000+)
EXPOSE 10000

# Comando para rodar o app
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
