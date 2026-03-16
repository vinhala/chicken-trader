.PHONY: build-local deploy-local deploy-prod

ENV_FILE := .env

# Check if the .env file exists, and include it if it does
ifneq ("$(wildcard $(ENV_FILE))","")
include $(ENV_FILE)
endif

STACK_NAME ?= chicken-trader

INFRA_DIR := infrastructure
NETWORK_FILE := $(INFRA_DIR)/docker-compose.network.yml
APP_FILE := $(INFRA_DIR)/docker-compose.app.yml
URLS_LOCAL_FILE := $(INFRA_DIR)/docker-compose.urls-local.yml
URLS_PROD_FILE := $(INFRA_DIR)/docker-compose.urls-prod.yml

build-local:
	docker build -t chicken-trader-backend:latest ./backend
	docker build -t chicken-trader-frontend:latest ./frontend

deploy-local:
	docker swarm init 2>/dev/null || true
	STACK_NAME=$(STACK_NAME) docker stack deploy -c $(NETWORK_FILE) $(STACK_NAME)
	STACK_NAME=$(STACK_NAME) docker stack deploy -c $(NETWORK_FILE) -c $(APP_FILE) -c $(URLS_LOCAL_FILE) $(STACK_NAME)

deploy-prod:
	docker swarm init 2>/dev/null || true
	STACK_NAME=$(STACK_NAME) docker stack deploy -c $(NETWORK_FILE) $(STACK_NAME)
	STACK_NAME=$(STACK_NAME) APP_HOST=$(APP_HOST) API_HOST=$(API_HOST) docker stack deploy -c $(NETWORK_FILE) -c $(APP_FILE) -c $(URLS_PROD_FILE) $(STACK_NAME)

down:
	docker stack rm $(STACK_NAME)