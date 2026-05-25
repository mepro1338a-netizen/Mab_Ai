# MaByte production — Railway MUST use this CMD (not streamlit run main.py)
FROM python:3.11-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_INTERNAL_PORT=8502

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway sets PORT at runtime; gateway.py listens on 0.0.0.0:$PORT
EXPOSE 8080

CMD ["python", "gateway.py"]
