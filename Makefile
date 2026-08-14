.PHONY: help run celery db-upgrade db-downgrade db-revision
.DEFAULT_GOAL := help

export PYTHONPATH := src

help: ## Показать список доступных команд с описанием
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-14s\033[0m %s\n", $$1, $$2}'

run: ## Запустить сервер разработки FastAPI (uvicorn) с автоперезагрузкой
	uvicorn src.main:app --reload

celery: ## Запустить воркер Celery для обработки фоновых задач
	celery --app=tasks.celery_app:celery_instance worker --loglevel=INFO

db-upgrade: ## Обновить базу данных до последней миграции
	alembic upgrade head

db-downgrade: ## Откатить последнюю применённую миграцию базы данных
	alembic downgrade -1

db-revision: ## Создать новую миграцию автоматически (использование: make db-revision m="текст сообщения")
	alembic revision --autogenerate -m "$(m)"
