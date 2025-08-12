VERSION ?= $(shell git describe --tags --always | sed 's/^v//')
IMAGE_TAG_BASE ?= eu.gcr.io/agentic-layer/summarizer-agent
IMG ?= $(IMAGE_TAG_BASE):$(VERSION)
PLATFORMS ?= linux/arm64,linux/amd64

ifneq (,$(wildcard ./.env))
    include .env
    export
endif

.PHONY: all
all: docker-build

.PHONY: build
build:
	uv sync

.PHONY: run
run: build
	uv run uvicorn main:app

.PHONY: docker-build
docker-build:
	docker build -t $(IMG) .

.PHONY: docker-run
docker-run: docker-build
	@echo "Agent Card URL: ${A2A_AGENT_CARD_URL}/.well-known/agent-card.json"
	docker run --rm -it -p ${UVICORN_PORT}:8000 $(IMG)

.PHONY: docker-push
docker-push:
	- docker buildx create --name agent-builder
	docker buildx use agent-builder
	docker buildx build --push --platform=$(PLATFORMS) --tag ${IMG} .
