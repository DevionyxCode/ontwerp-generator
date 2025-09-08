FROM python:3.11-slim

WORKDIR /src

COPY requirements.txt /src/requirements.txt
COPY src/ /src/

RUN pip install --no-cache-dir -r /src/requirements.txt

# Zet poort 8090 open binnen de container
EXPOSE 8090

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090"]
