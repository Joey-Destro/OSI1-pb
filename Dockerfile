FROM python:3.9

# Instalace systémových závislostí pro audio
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /code

# Nejprve zkopírujeme jen requirements pro rychlejší build
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pak zkopírujeme zbytek projektu
COPY . .

# Spuštění aplikace (ujisti se, že máš v repozitáři main.py)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]