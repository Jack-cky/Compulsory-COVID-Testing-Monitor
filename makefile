.PHONY: create_env install run clean init

SHELL := /bin/bash
PYTHON_VERSION=3.10
ENV_NAME=ctn-monitor
CONDA_PATH=$(shell which conda)

create_env:
	conda create -n $(ENV_NAME) python=$(PYTHON_VERSION) -y

install:
	$(CONDA_PATH) init bash
	source $$(conda info --base)/etc/profile.d/conda.sh && \
	conda activate $(ENV_NAME) && \
	pip install -r requirements.txt

init: create_env install

run:
	source $$(conda info --base)/etc/profile.d/conda.sh && \
	conda activate $(ENV_NAME) && \
	python src/Pipeline.py

clean:
	source $$(conda info --base)/etc/profile.d/conda.sh && \
	conda deactivate && \
	conda env remove -n $(ENV_NAME)
