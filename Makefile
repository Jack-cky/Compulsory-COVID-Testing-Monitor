.PHONY: help airflow down

AIRFLOW_DIR=airflow
ENV_FILE=$(AIRFLOW_DIR)/.env
COMPOSE=docker compose --env-file $(ENV_FILE) -f $(AIRFLOW_DIR)/compose.yaml

help:
	@echo "Available targets:"
	@echo "  make help       # Show available targets"
	@echo "  make airflow    # Start the Airflow services in detached mode using existing images"
	@echo "  make down       # Stop and remove services defined in airflow/compose.yaml"

airflow:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down
