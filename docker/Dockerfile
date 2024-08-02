ARG PYTHON_VERSION=3.10.14

FROM python:${PYTHON_VERSION}-slim as base

WORKDIR /ctn_monitor

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "src/Pipeline.py"]
