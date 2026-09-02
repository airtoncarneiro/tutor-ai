# Adaptive SQL Tutor

Tutor local e adaptativo de SQL, com um laboratório executável em PostgreSQL e um LLM responsável pelo raciocínio pedagógico.

## Requisitos

- Python 3.11+
- Docker e Docker Compose

## Configuração e execução

```bash
cp .env.example .env
# preencha LLM_MODEL e LLM_API_KEY com os dados do Google AI Studio
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
docker compose up -d
.venv/bin/pytest
.venv/bin/adaptive-sql-tutor
```

O PostgreSQL é exposto em `localhost:5432` por padrão. A integração atual usa o endpoint OpenAI-compatible do Google Gemini através do SDK `openai`. O modelo e a chave são carregados exclusivamente do `.env`.

Configuração esperada:

```env
LLM_PROVIDER=gemini
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
LLM_MODEL=gemma-4-26b-a4b-it
LLM_API_KEY=sua_chave_do_google_ai_studio
```

O cliente usa Chat Completions, respostas JSON estruturadas e tool calls. A camada de compatibilidade do Gemini não garante suporte a todos os recursos específicos da OpenAI; recursos avançados devem ser verificados na documentação do Google antes de serem adicionados.
