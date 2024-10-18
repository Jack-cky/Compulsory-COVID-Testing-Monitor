ARG PYTHON_IMAGE=python:3.10.14-slim

FROM ${PYTHON_IMAGE} AS builder

COPY requirements.txt .

RUN pip install --no-cache-dir --target=packages -r requirements.txt

FROM ${PYTHON_IMAGE}

COPY --from=builder packages /usr/local/lib/python3.10/site-packages

WORKDIR /ctn-monitor

COPY . .

CMD ["python", "main.py"]
