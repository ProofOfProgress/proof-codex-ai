FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m playwright install chromium --with-deps || true

COPY . .
RUN mkdir -p data

EXPOSE 8080
CMD ["python3", "-m", "shorts_bot.web"]
