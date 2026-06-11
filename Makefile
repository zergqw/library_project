.PHONY: help install migrate run superuser test check shell

VENV_DIR ?= venv

ifeq ($(OS),Windows_NT)
	PYTHON ?= python
	VENV_PYTHON = $(VENV_DIR)\Scripts\python.exe
else
	PYTHON ?= python3
	VENV_PYTHON = $(VENV_DIR)/bin/python
endif

MANAGE = $(VENV_PYTHON) manage.py

help:
	@echo "Доступные команды:"
	@echo "  make venv        - создать локальное виртуальное окружение"
	@echo "  make install     - установить зависимости в виртуальное окружение"
	@echo "  make migrate     - применить миграции базы данных"
	@echo "  make run         - запустить Django dev server"
	@echo "  make superuser   - создать суперпользователя"
	@echo "  make test        - запустить тесты"
	@echo "  make check       - выполнить Django system check"
	@echo "  make shell       - открыть Django shell"
	@echo "Переменные:"
	@echo "  VENV_DIR=venv    - путь к виртуальному окружению"
	@echo "  PYTHON=python3   - интерпретатор для создания venv"

venv:
	$(PYTHON) -m venv $(VENV_DIR)

install: venv
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r requirements.txt

migrate:
	$(MANAGE) migrate

run:
	$(MANAGE) runserver

superuser:
	$(MANAGE) createsuperuser

test:
	$(MANAGE) test

check:
	$(MANAGE) check

shell:
	$(MANAGE) shell
