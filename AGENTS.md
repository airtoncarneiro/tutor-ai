# AGENTS.md

## Project

Adaptive SQL Tutor.

A local Python application that uses an LLM to provide adaptive SQL learning with an executable PostgreSQL learning environment created dynamically according to the learner's diagnosed needs.

## Primary Objective

Implement a V1 capable of:

1. receiving a request such as `Quero aprender Window Functions`;
2. diagnosing the learner before teaching;
3. creating a learner model;
4. creating a contextual learning scenario;
5. creating an initial adaptive learning path;
6. dynamically designing and provisioning a PostgreSQL Learning Lab;
7. allowing the learner to execute SQL provided by the tutor;
8. allowing the learner to write and execute their own SQL;
9. evaluating the SQL together with its actual execution result;
10. recording learning evidence;
11. updating mastery;
12. adapting the next learning action.

## Source of Truth

Before implementing or modifying behavior, read:

1. `docs/requirements.md`
2. `docs/design.md`
3. `docs/tasks.md`

Priority in case of conflict:

1. requirements;
2. design;
3. tasks;
4. existing implementation.

Do not silently change requirements to accommodate an implementation decision.

## V1 Scope

The application is:

- local;
- single-user;
- SQL-only;
- PostgreSQL-only;
- Python-based;
- backed by one local PostgreSQL instance;
- powered by one primary LLM tutor with tools.
- includes a local graphical interface implemented with Streamlit.

Do not introduce multi-agent architecture in V1.

Do not introduce:

- authentication;
- authorization;
- multi-tenancy;
- cloud infrastructure;
- Kubernetes;
- distributed execution;
- separate databases per learner;
- vector databases unless a later requirement explicitly needs one;
- message brokers unless a later requirement explicitly needs one.

The V1 user interface is a local Streamlit application. It exposes the
learning conversation, diagnostic questions, SQL execution, results/errors,
learning path and concept mastery. Keep UI code thin; pedagogical reasoning
remains with the LLM and deterministic behavior remains in application services.

Prefer the simplest implementation satisfying the requirements.

## Architecture Principle

Use:

`Python application + LLM Tutor + Tools + PostgreSQL`

The LLM owns pedagogical reasoning.

Python owns deterministic execution.

PostgreSQL owns persistent state and the executable SQL Learning Lab.

Tools form the contract between the LLM and deterministic application services.

## Responsibility Boundary

### LLM

Responsible for:

- INTENT;
- PROBE;
- DIAGNOSE;
- Learning Scenario;
- contextual Knowledge Graph;
- pedagogical strategy;
- TEACH;
- PRACTICE;
- EVALUATE;
- ADAPT;
- REVIEW;
- APPLY;
- TRANSFER TEST;
- determining when the Learning Lab needs to evolve.

### Python

Responsible for:

- application orchestration;
- tool execution;
- PostgreSQL connectivity;
- persistence;
- schema inspection;
- SQL execution;
- Learning Lab provisioning;
- structured-output validation;
- deterministic mastery calculations where defined;
- returning tool results to the LLM.

### PostgreSQL

Contains two logically separate environments:

`schema tutor`

Persistent learning metadata.

`schema lab`

Disposable and dynamically evolving SQL practice environment.

Never allow dynamically generated Learning Lab SQL to modify the `tutor` schema.

## Adaptive Learning Principle

Never assume that a requested subject directly defines the learning path.

The required lifecycle is:

`INTENT → PROBE → DIAGNOSE → SCENARIO → GRAPH → PATH → LAB → LEARN`

During learning:

`TEACH → PRACTICE → EXECUTE → EVALUATE → EVIDENCE → ADAPT`

ADAPT may modify:

- learner model;
- learning scenario;
- knowledge graph;
- learning path;
- exercise difficulty;
- SQL Learning Lab.

The Learning Scenario is a hypothesis and may evolve.

The Learning Path must use a short planning horizon rather than becoming a static course.

## Critical Rule

When receiving:

`Quero aprender [SQL topic]`

the application MUST NOT immediately begin teaching.

It must first obtain sufficient diagnostic evidence.

Only after diagnosis may it create the initial Learning Scenario and Learning Lab.

## SQL Learning Lab

The Learning Lab must be pedagogically designed.

Do not populate it with meaningless random data.

Data must deliberately contain cases required by the learning scenario.

Examples:

- ties for ranking exercises;
- temporal sequences for LAG/LEAD;
- NULLs for NULL semantics;
- unmatched rows for JOIN;
- duplicates for deduplication;
- different group cardinalities for aggregation;
- hierarchical relationships for recursive CTE;
- sufficient volume/distribution for performance exercises.

Start with the smallest useful lab.

Extend it only when pedagogically necessary.

## SQL Execution

Never assume a query is correct because it parses or executes.

Evaluation must distinguish:

- syntax correctness;
- execution success;
- semantic correctness;
- result correctness;
- requirement satisfaction;
- reasoning quality.

The real PostgreSQL execution result must be available to the tutor when evaluating executable exercises.

## Tooling

Initial tool contract should include:

- `create_lab`
- `execute_sql`
- `inspect_lab`
- `extend_lab`
- `reset_lab`
- `load_learning_state`
- `save_learning_evidence`

Do not create an agent for operations that can be deterministic Python functions.

## Development Rules

Use Python.

Use PostgreSQL SQL.

Prefer:

- explicit types;
- Pydantic models at LLM/tool boundaries;
- small services with clear responsibilities;
- dependency injection where it materially improves testability;
- migrations for the `tutor` schema;
- automated tests.

## Current LLM implementation

The current local configuration uses OpenRouter through its OpenAI-compatible
endpoint and the Python `openai` SDK. The same client boundary can point to
Google AI Studio's compatible endpoint when explicitly configured.

Configuration is loaded from `.env`:

- `LLM_PROVIDER=openrouter`;
- `LLM_BASE_URL=https://openrouter.ai/api/v1/`;
- `LLM_MODEL=@preset/preset-free` (or another model explicitly supported by the endpoint);
- `LLM_API_KEY` contains the provider key and must never be logged or committed.
- `LLM_TIMEOUT_SECONDS` controls the per-request timeout and is configured in
  `.env` (the local default is 45 seconds).

The client uses Chat Completions, JSON structured output and local tool calls. Do not assume that every OpenAI-specific API, parameter or hosted tool is supported by Gemini's compatibility layer. Provider-specific behavior belongs in `src/app/llm/client.py`; the tutor orchestrator must depend on the internal `LLMClient` contract.

LLM calls must be resilient to transient provider failures. The client SHALL
apply bounded retries with exponential backoff for transient `429`, `500`,
`502`, `503` and `504` responses, while respecting the configured timeout and
never retrying malformed requests or validation failures. The UI SHALL expose a
clear retryable error when the provider remains unavailable. Retries must not
log the API key or complete learner payloads.

Lab tool failures are part of the tutor context. `create_lab` and `extend_lab`
must validate generated SQL in a rollback-only PostgreSQL transaction before
changing the real `lab` schema. Provisioning or extension errors must be
returned as structured tool results so the LLM can repair them. Tool argument
validation errors must also return to the LLM instead of terminating the
learner turn. The orchestrator must stop repeated identical tool calls and
return a learner-facing response after the configured iteration limit.

Avoid speculative abstractions.

Do not create generic frameworks before a second concrete use case requires them.

## Implementation Process

Work incrementally according to `docs/tasks.md`.

For each task:

1. read the relevant requirements;
2. inspect the existing implementation;
3. implement only the requested scope;
4. add or update tests;
5. run relevant tests;
6. fix failures;
7. verify acceptance criteria;
8. update task status only after verification.

Do not implement future milestones opportunistically unless required to complete the current task.

## Testing Philosophy

Test behavior rather than implementation details.

The most important end-to-end scenario is:

`Quero aprender Window Functions`

The system must eventually demonstrate that different diagnostic evidence can produce different learning paths.

Example:

Learner A:

`GROUP BY mastery high → proceed toward Window Functions`

Learner B:

`GROUP BY/granularity weak → remediate prerequisite → later proceed toward Window Functions`

If both learners always receive essentially the same path, the adaptive requirement has not been satisfied.

## Definition of Done — V1

V1 is complete only when an end-to-end flow demonstrates:

1. learning request;
2. adaptive PROBE;
3. diagnosis;
4. learner baseline;
5. Learning Scenario;
6. contextual Knowledge Graph;
7. initial Learning Path;
8. dynamic PostgreSQL Lab creation;
9. executable tutor-provided SQL;
10. executable learner-written SQL;
11. evaluation using actual execution results;
12. evidence persistence;
13. mastery update;
14. next-step adaptation;
15. at least one demonstrated path divergence caused by learner evidence.

## Phase 15 and 16 boundary

The integrated pedagogical application service is implemented and is the
single boundary used by the Streamlit GUI to coordinate diagnosis, planning,
tools, evaluation and persistence across learner turns. Phase 16 hardening is
also implemented for the local Window Functions V1 scope, including GUI SQL
evaluation, concrete tool schemas, adaptive diagnosis, SQL safeguards, failure
recovery and automated strong/weak path divergence validation.

Do not expand this result into multi-user, cloud or multi-agent behavior. The
remaining post-V1 work is tracked in Phase 17.

Phase 17 is reserved for post-V1 evolution: richer diagnosis, native Gemini SDK
assessment, browser tests, observability and additional SQL scenarios.
