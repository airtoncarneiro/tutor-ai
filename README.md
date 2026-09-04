# Adaptive SQL Tutor AI

O Adaptive SQL Tutor AI é uma aplicação local para aprender SQL com ajuda de
inteligência artificial.

Você informa o que deseja aprender, por exemplo `Quero aprender Window
Functions`. O tutor faz algumas perguntas para entender seu nível, cria um
laboratório PostgreSQL com dados de prática e acompanha sua evolução enquanto
você escreve e executa consultas SQL.

## O que você precisa

- Python 3.11 ou mais recente;
- Docker Desktop ou Docker com Docker Compose;
- uma chave de API de um provedor compatível com OpenAI.

O projeto foi desenvolvido e validado localmente com Python, PostgreSQL,
Docker e Streamlit.

## Instalação rápida

### 1. Clone o projeto

Clone o repositório:

```bash
git clone https://github.com/airtoncarneiro/tutor-ai.git
cd tutor-ai
```

### 2. Crie o ambiente Python

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
```

### 3. Configure o provedor de IA

Crie o arquivo local de configuração:

```bash
cp .env.example .env
```

Edite `.env` e informe o provedor, o modelo e a chave:

```env
LLM_PROVIDER=openrouter
LLM_BASE_URL=https://openrouter.ai/api/v1/
LLM_MODEL=modelo-llm
LLM_API_KEY=sua_chave_aqui
LLM_TIMEOUT_SECONDS=45
```

O cliente usa o SDK `openai` e o contrato compatível com OpenAI. O endpoint
configurado pode ser trocado por outro compatível, desde que ele aceite
Chat Completions, respostas JSON e chamadas de ferramentas.

Não compartilhe o arquivo `.env` nem coloque sua chave no Git.

### 4. Inicie o banco de dados

```bash
docker compose up -d
```

Esse comando inicia o PostgreSQL usado para guardar seu progresso e o
laboratório de exercícios.

### 5. Abra a aplicação

```bash
.venv/bin/streamlit run ui/streamlit_app.py
```

O Streamlit exibirá um endereço local, normalmente
`http://localhost:8501`. Abra esse endereço no navegador.

As tabelas necessárias são criadas automaticamente quando a aplicação inicia.

## Como usar

1. Digite o tema que deseja aprender no campo de conversa.
2. Responda às perguntas de diagnóstico sem preocupação em errar.
3. Aguarde o tutor criar o cenário e o laboratório.
4. Leia a explicação e execute as consultas sugeridas.
5. Escreva suas próprias consultas no editor SQL.
6. Veja os resultados ou erros do PostgreSQL.
7. Avalie a tentativa para registrar seu progresso.

O tutor não começa ensinando imediatamente. Ele primeiro identifica seus
conhecimentos e pode sugerir um caminho diferente para cada pessoa.

## Temas disponíveis

O laboratório possui cenários pedagógicos para:

- Window Functions;
- JOIN;
- CTE e CTE recursiva;
- NULL;
- subqueries;
- agregações avançadas;
- deduplicação;
- transações em consultas somente leitura;
- funções de data;
- otimização de consultas sem índices ou `EXPLAIN`.

Índices, `EXPLAIN`, modelagem e normalização não fazem parte do escopo atual.

## Parar ou reiniciar o ambiente

Para parar o PostgreSQL preservando os dados:

```bash
docker compose stop
```

Para parar e remover o container, mas preservar o volume:

```bash
docker compose down
```

Para apagar também os dados locais e começar do zero:

```bash
docker compose down -v
```

Use o último comando somente se quiser perder as sessões e o laboratório
armazenados localmente.

## Problemas comuns

### A aplicação não abre ou não encontra o PostgreSQL

Verifique se o container está ativo:

```bash
docker compose ps
```

Se necessário, inicie-o novamente:

```bash
docker compose up -d
```

### A porta 5432 já está em uso

Altere `POSTGRES_PORT` no `.env` para uma porta livre e execute novamente:

```bash
docker compose down
docker compose up -d
```

### O tutor não responde

Confira no `.env`:

- `LLM_API_KEY` preenchida;
- `LLM_BASE_URL` correto;
- `LLM_MODEL` disponível no provedor;
- `LLM_TIMEOUT_SECONDS` suficiente para o modelo.

Falhas temporárias do provedor são repetidas automaticamente dentro de um
limite. Falhas de autenticação ou configuração precisam ser corrigidas no
`.env`.

### Quero executar os testes

Com o PostgreSQL ativo, execute:

```bash
.venv/bin/pytest -q
```

A suíte cobre o fluxo da aplicação, a interface Streamlit, os cenários SQL,
execução de consultas, avaliação, persistência e recuperação de falhas.

## Para quem vai desenvolver

Os detalhes de requisitos, arquitetura, fases e decisões técnicas estão em:

- [`docs/requirements.md`](docs/requirements.md);
- [`docs/design.md`](docs/design.md);
- [`docs/tasks.md`](docs/tasks.md);
- [`AGENTS.md`](AGENTS.md).

A aplicação é local e de usuário único. Não há autenticação, multiusuário,
infraestrutura em nuvem ou arquitetura multiagente.
