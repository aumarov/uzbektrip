.PHONY: help setup run migrate superuser shell docker-up docker-down docker-logs clean

help:
	@echo "Available commands:"
	@echo "  make setup      — create venv, install deps, run migrations, create superuser"
	@echo "  make run        — start local dev server (SQLite)"
	@echo "  make migrate    — apply database migrations"
	@echo "  make superuser  — create admin superuser"
	@echo "  make shell      — open Django shell"
	@echo "  make docker-up  — start full stack with docker-compose"
	@echo "  make docker-down — stop docker-compose"
	@echo "  make docker-logs — tail logs"
	@echo "  make clean      — remove __pycache__ and .pyc files"

setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	cp -n .env.example .env || true
	DJANGO_SETTINGS_MODULE=config.settings.local .venv/bin/python manage.py migrate
	DJANGO_SETTINGS_MODULE=config.settings.local .venv/bin/python manage.py setup_site
	@echo ""
	@echo "Run 'make superuser' then 'make run'"
	@echo "Site:  http://localhost:8000/"
	@echo "Admin: http://localhost:8000/cms/"

run:
	DJANGO_SETTINGS_MODULE=config.settings.local .venv/bin/python manage.py runserver

migrate:
	DJANGO_SETTINGS_MODULE=config.settings.local .venv/bin/python manage.py migrate

superuser:
	DJANGO_SETTINGS_MODULE=config.settings.local .venv/bin/python manage.py createsuperuser

shell:
	DJANGO_SETTINGS_MODULE=config.settings.local .venv/bin/python manage.py shell

docker-up:
	docker-compose up -d
	@echo "App running at http://localhost:8000"
	@echo "Wagtail admin at http://localhost:8000/cms/"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f web

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
