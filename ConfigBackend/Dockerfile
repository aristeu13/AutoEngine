FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "configbackend.main:app", "-b", "0.0.0.0:8000", "--worker-class", "uvicorn.workers.UvicornWorker"]
