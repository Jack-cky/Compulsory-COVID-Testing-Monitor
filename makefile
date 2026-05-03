.DEFAULT_GOAL := help
.PHONY: help up down reset

AIRFLOW_DIR=airflow
ENV_FILE=$(AIRFLOW_DIR)/.env
COMPOSE=docker compose --env-file $(ENV_FILE) -f $(AIRFLOW_DIR)/docker-compose.yaml

help:
	@printf "Available targets:\n"
	@printf "  make up        # build image and start Airflow\n"
	@printf "  make down      # stop Airflow services\n"
	@printf "  make reset     # stop services and remove volumes\n"

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

reset:
	$(COMPOSE) down -v
