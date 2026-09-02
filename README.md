# Adaptive SQL Tutor

Tutor local e adaptativo de SQL, com um laboratório executável em PostgreSQL e um LLM responsável pelo raciocínio pedagógico.

## Requisitos

- Python 3.11+
- Docker e Docker Compose

## Configuração e execução

```bash
cp .env.example .env
# preencha LLM_MODEL e LLM_API_KEY quando a integração do LLM for habilitada
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
docker compose up -d
.venv/bin/pytest
.venv/bin/adaptive-sql-tutor
```

O PostgreSQL é exposto em `localhost:5432` por padrão. A aplicação ainda está na fundação da Fase 0; migrações, laboratório e integração com o LLM serão implementados nas fases seguintes.

