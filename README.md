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
.venv/bin/adaptive-sql-tutor-migrate
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

## Comandos de desenvolvimento

```bash
# iniciar PostgreSQL
docker compose up -d

# aplicar migrações
.venv/bin/adaptive-sql-tutor-migrate

# executar aplicação
.venv/bin/adaptive-sql-tutor

# executar testes
.venv/bin/pytest

# parar PostgreSQL (preserva dados)
docker compose down

# resetar PostgreSQL local (remove o volume e os dados locais)
docker compose down -v
```

## Estado atual da V1

Implementados: persistência do estado de aprendizagem, diagnóstico, cenário contextual, trilha de curto horizonte, laboratório PostgreSQL dinâmico, exercícios executáveis, avaliação/mastery, evolução do lab, Apply/Transfer e integração Gemini.

Limitações conhecidas: o fluxo ainda é uma base local de desenvolvimento; o orquestrador LLM não possui ainda uma interface de aplicação completa para todos os turnos do aluno, e a cobertura end-to-end usa o cenário Window Functions como prova principal. Não há autenticação, multiusuário, infraestrutura cloud ou isolamento entre usuários.
