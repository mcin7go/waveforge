FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# --- NOWY KROK: Kompilacja tłumaczeń podczas budowania obrazu ---
RUN pybabel compile -d app/translations

EXPOSE 5000
CMD ["./start.sh"]
