ARG PYTHON_VERSION=3.10.13
FROM python:${PYTHON_VERSION}-slim as base

WORKDIR /ctn_monitor

RUN apt-get update && \
    apt-get install -y fontconfig fonts-noto-cjk && \
    fc-cache -fv && \
    rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip \
   --mount=type=bind,source=requirements.txt,target=requirements.txt \
   python -m pip install -r requirements.txt

COPY . .

CMD python src/Pipeline.py
