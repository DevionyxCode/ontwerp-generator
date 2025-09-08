FROM python:3.11-slim

WORKDIR /src

COPY requirements.txt /src/requirements.txt
COPY src/ /src/

RUN pip install --no-cache-dir -r /src/requirements.txt

# Geef aan dat poort 8090 gebruikt wordt
EXPOSE 8090

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090"]
