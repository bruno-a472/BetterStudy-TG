FROM python:3.11-bookworm

RUN apt-get update && \
    apt-get install -y --no-install-recommends chromium chromium-driver && \
    rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["gunicorn", "--timeout", "300", "--bind", "0.0.0.0:10000", "app:app"]