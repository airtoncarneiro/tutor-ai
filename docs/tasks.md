# Adaptive SQL Tutor — Implementation Tasks

## Working Method

Implement tasks sequentially unless a dependency requires otherwise.

Each task has acceptance criteria.

Do not mark a task complete until:

- implementation exists;
- relevant automated tests pass;
- acceptance criteria have been verified.

---

# Phase 0 — Repository Foundation

## TASK-001 — Initialize Python project

Create:

- Python project;
- `pyproject.toml`;
- application package;
- tests structure;
- `.gitignore`;
- `.env.example`;
- initial README.

Acceptance:

- project installs successfully;
- test runner executes;
- minimal application starts.

---

## TASK-002 — Add PostgreSQL development environment

Create Docker Compose configuration for local PostgreSQL.

Acceptance:

`docker compose up -d`

starts PostgreSQL successfully.

Document connection configuration.

---

## TASK-003 — Application configuration

Implement typed configuration for:

- PostgreSQL;
- LLM provider/model;
- application environment.

Configuration secrets SHALL come from environment variables.

Acceptance:

application loads valid configuration and fails clearly for missing mandatory values.

---

# Phase 1 — Persistent Learning State

## TASK-010 — Database migration infrastructure

Introduce database migrations.

Create `tutor` schema.

Acceptance:

fresh PostgreSQL instance can be migrated from zero to current schema.

---

## TASK-011 — learning_session

Create persistence for:

`tutor.learning_session`

Required fields:

- session_id;
- topic;
- goal;
- phase;
- status;
- scenario;
- timestamps.

Acceptance:

integration test creates and retrieves a learning session.

---

## TASK-012 — learning_concept

Create:

`tutor.learning_concept`

Include:

- concept key;
- name;
- mastery;
- confidence;
- misconception.

Acceptance:

concept can be upserted within a session.

Duplicate concept keys within a session SHALL NOT create duplicate logical concepts.

---

## TASK-013 — learning_evidence

Create:

`tutor.learning_evidence`

Acceptance:

multiple evidence records can be associated with a concept and retrieved chronologically.

---

## TASK-014 — learning_event

Create:

`tutor.learning_event`

Acceptance:

application can append and retrieve learning events.

Do not implement full event sourcing.

---

## TASK-015 — Learning state service

Implement compact loading of current learning state.

Acceptance:

given a session, return:

- topic;
- goal;
- phase;
- scenario;
- concepts;
- mastery;
- confidence;
- misconceptions;
- recent evidence.

---

# Phase 2 — SQL Learning Lab

## TASK-020 — Lab schema lifecycle

Implement creation/reset of:

`lab`

Acceptance:

application can safely recreate the local `lab` schema without modifying `tutor`.

Integration test MUST verify that resetting `lab` leaves tutor metadata intact.

---

## TASK-021 — Lab provisioner

Implement execution of Lab DDL and seed SQL.

Acceptance:

given a valid Lab definition, create tables and populate data.

Return clear provisioning failures.

---

## TASK-022 — SQL executor

Implement execution of learner SQL against the Learning Lab.

Return:

- success;
- columns;
- rows;
- row count;
- error.

Acceptance:

integration tests cover:

- successful SELECT;
- empty result;
- PostgreSQL syntax error;
- runtime SQL error.

---

## TASK-023 — Lab inspector

Implement compact schema inspection.

Return at least:

- tables;
- columns;
- PostgreSQL types;
- primary keys;
- foreign keys;
- indexes when relevant.

Acceptance:

inspection accurately represents an integration-test lab.

---

## TASK-024 — Lab reset

Store enough provisioning information to restore the current lab baseline.

Acceptance:

after learner mutations, reset restores expected baseline data.

---

## TASK-025 — Lab extension

Allow incremental:

- DDL;
- DML;
- indexes;
- views.

Acceptance:

existing lab data remains available unless the extension explicitly changes it.

---

# Phase 3 — Tool Layer

## TASK-030 — Tool contracts

Create validated Pydantic input/output models for:

- create_lab;
- execute_sql;
- inspect_lab;
- extend_lab;
- reset_lab;
- load_learning_state;
- save_learning_evidence.

Acceptance:

invalid tool input is rejected with useful validation errors.

---

## TASK-031 — Tool registry

Implement deterministic mapping:

`tool name → Python implementation`

Acceptance:

known tool dispatch succeeds.

Unknown tool names fail explicitly.

---

## TASK-032 — Lab tools

Connect:

- create_lab;
- execute_sql;
- inspect_lab;
- extend_lab;
- reset_lab

to Lab services.

Acceptance:

tool-level integration tests pass against PostgreSQL.

---

## TASK-033 — Learning tools

Connect:

- load_learning_state;
- save_learning_evidence

to persistence services.

Acceptance:

round-trip persistence test passes.

---

# Phase 4 — LLM Integration

## Current implementation status

The Phase 4 boundary is implemented and validated with a real Gemini API call. The configured route is Google AI Studio's OpenAI-compatible endpoint, accessed with the `openai` Python SDK. The implementation uses Chat Completions, JSON structured responses and local function tool calls. The API key is loaded from `LLM_API_KEY` and must not be committed.

## TASK-040 — Prompt loader

Load:

`prompts/adaptive_sql_tutor.md`

The prompt SHALL not be hardcoded across application modules.

Acceptance:

prompt can be loaded and supplied to the LLM client.

---

## TASK-041 — LLM abstraction

Create a minimal LLM client boundary.

Do not build a generic provider framework.

Acceptance:

application can send:

- system prompt;
- current learning state;
- learner message;
- available tool definitions.

---

## TASK-042 — Structured tutor response

Create validated structured models for tutor responses/tool calls.

Acceptance:

application does not parse arbitrary prose to determine tool execution.

Malformed structured output produces an observable error.

---

## TASK-043 — Tool-call loop

Implement:

```text
LLM
 ↓
tool request
 ↓
Python tool
 ↓
tool result
 ↓
LLM
```

Continue until the tutor produces a learner-facing response or a configured maximum iteration count is reached.

Acceptance:

integration/fake-LLM test demonstrates at least two sequential tool calls before final response.

---

# Phase 5 — Diagnostic Learning Flow

## TASK-050 — Start learning request

Support:

`Quero aprender [topic]`

Create learning session.

Initial phase:

`INTENT` or `PROBE`

depending on whether intent clarification is required.

Acceptance:

the application SHALL NOT immediately provision the lab.

---

## TASK-051 — PROBE orchestration

Allow the LLM to conduct adaptive diagnostic questioning.

Acceptance:

diagnostic interaction can span multiple learner turns.

No lab is required yet.

---

## TASK-052 — Diagnostic evidence persistence

Persist relevant PROBE evidence.

Acceptance:

answers can produce evidence for multiple prerequisite concepts.

---

## TASK-053 — Initial learner baseline

After sufficient diagnostic evidence, create initial concept mastery/confidence state.

Acceptance:

learner state clearly differentiates:

- mastered;
- partial;
- insufficient;
- unknown.

---

# Phase 6 — Scenario and Planning

## TASK-060 — Learning Scenario creation

After PROBE completion, generate and persist a structured scenario.

Include:

- topic;
- goal;
- level;
- target capabilities;
- strengths;
- gaps;
- strategy;
- lab requirements.

Acceptance:

scenario is persisted in `learning_session`.

---

## TASK-061 — Contextual Knowledge Graph

Represent relevant concept dependencies for the scenario.

Avoid universal SQL graph generation.

Acceptance:

graph can represent at least:

`prerequisite → concept`

and can evolve later.

---

## TASK-062 — Short-horizon Learning Path

Represent:

- current;
- next candidates;
- near-future candidates.

Acceptance:

path is not a mandatory complete syllabus.

---

# Phase 7 — Dynamic Lab Generation

## TASK-070 — Lab Specification model

Create structured representation containing:

- purpose;
- tables;
- relationships;
- data requirements;
- pedagogical invariants.

Acceptance:

model can represent a Window Functions lab.

---

## TASK-071 — Generate Window Functions lab

From a diagnosed Window Functions scenario, generate an initial lab.

Suggested domain:

e-commerce.

Possible tables:

- customers;
- orders.

Dataset MUST support:

- multiple orders per customer;
- temporal ordering;
- different partition sizes;
- tied values.

Acceptance:

actual PostgreSQL data satisfies the required pedagogical invariants.

---

## TASK-072 — Automatic lab provisioning

Connect scenario planning to:

`create_lab`

Acceptance:

after PROBE/scenario creation, the application can automatically create the Learning Lab.

---

# Phase 8 — Executable Learning

## TASK-080 — Tutor-provided query execution

Support flow:

```text
Tutor provides SQL
Learner executes
Application returns result
Tutor asks learner to interpret
```

Acceptance:

real PostgreSQL result participates in subsequent tutor interaction.

---

## TASK-081 — Learner-written query execution

Support flow:

```text
Tutor gives requirement
Learner writes SQL
Application executes SQL
Tutor receives SQL + result/error
Tutor evaluates
```

Acceptance:

evaluation has access to both submitted SQL and actual execution output.

---

## TASK-082 — Debug exercises

Support incorrect-query debugging.

Acceptance:

PostgreSQL error can be used by tutor without immediately revealing the solution.

---

## TASK-083 — Modify exercises

Support requirement changes applied to existing working SQL.

Acceptance:

learner can modify, execute and receive evaluation of the modified solution.

---

# Phase 9 — Evaluation and Mastery

## TASK-090 — Evaluation evidence model

Ensure evaluation distinguishes:

- syntax;
- execution;
- semantics;
- requirement satisfaction;
- reasoning.

Acceptance:

successful execution alone cannot automatically generate maximum correctness/mastery.

---

## TASK-091 — Mastery engine V1

Implement a simple deterministic and replaceable mastery calculation.

Inputs SHOULD include:

- previous mastery;
- correctness;
- difficulty;
- reasoning quality;
- independence/assistance;
- evidence count.

Acceptance:

unit tests demonstrate:

- repeated strong evidence increases mastery;
- weak evidence does not immediately establish mastery;
- incorrect evidence can reduce confidence/mastery appropriately.

Document the formula.

---

## TASK-092 — Adapt next learning action

After evidence/mastery update, reassess the next concept/action.

Acceptance:

different evidence can result in different next actions.

---

# Phase 10 — Adaptive Lab Evolution

## TASK-100 — Detect lab extension need

Allow tutor to determine that the next learning action requires additional lab capabilities.

Acceptance:

scenario can request lab extension without full reset.

---

## TASK-101 — Extend lab during learning

Execute requested extension and return updated lab state to tutor.

Acceptance:

learning continues using the extended environment.

---

# Phase 11 — Review, Apply and Transfer

## TASK-110 — Review flow

Introduce cumulative retrieval practice.

Acceptance:

previous concepts can return to active practice.

---

## TASK-111 — Apply flow

Generate realistic multi-concept SQL problem.

Acceptance:

learner must analyze, write, execute and validate SQL.

---

## TASK-112 — Transfer Test

Generate a different context requiring the same principles.

Acceptance:

test does not merely rename the previous exercise.

Failure can reactivate relevant concepts.

---

# Phase 12 — End-to-End Acceptance

## TASK-120 — Window Functions strong-prerequisite scenario

Simulate learner with strong:

- GROUP BY;
- aggregation;
- row granularity.

Expected:

system progresses toward Window Functions without unnecessary prerequisite teaching.

---

## TASK-121 — Window Functions weak-prerequisite scenario

Simulate learner with weak understanding of aggregation/granularity.

Expected:

system introduces prerequisite remediation before progressing.

---

## TASK-122 — Verify path divergence

Compare TASK-120 and TASK-121.

Acceptance:

learning actions are meaningfully different because of diagnostic evidence.

This is mandatory for V1 completion.

---

## TASK-123 — Full executable scenario

Demonstrate:

```text
Quero aprender Window Functions
        ↓
PROBE
        ↓
DIAGNOSE
        ↓
SCENARIO
        ↓
LAB CREATED
        ↓
TEACH
        ↓
BUILD EXERCISE
        ↓
LEARNER SQL
        ↓
POSTGRES EXECUTION
        ↓
EVALUATION
        ↓
EVIDENCE
        ↓
MASTERY UPDATE
        ↓
ADAPTED NEXT STEP
```

Acceptance:

the complete workflow executes without manual database preparation.

---

# Phase 13 — Documentation and Operational Readiness

## TASK-130 — README

Document:

- prerequisites;
- installation;
- configuration;
- PostgreSQL startup;
- migrations;
- application startup;
- tests;
- example learning session.

---

## TASK-131 — Development commands

Provide simple commands for:

- start PostgreSQL;
- stop PostgreSQL;
- migrate;
- run application;
- run tests;
- reset local environment.

---

## TASK-132 — Final V1 validation

Verify every requirement marked SHALL in `docs/requirements.md`.

Document any known limitation.

V1 SHALL NOT be declared complete if adaptive path divergence has not been demonstrated.

---

# V1 Definition of Done

The project is V1-complete when:

- local application starts reproducibly;
- PostgreSQL starts reproducibly;
- tutor state persists;
- PROBE occurs before teaching;
- diagnosis creates a contextual scenario;
- scenario creates its own SQL Lab;
- learner executes real PostgreSQL SQL;
- tutor evaluates actual results;
- evidence updates mastery;
- mastery changes subsequent learning;
- Learning Lab can evolve;
- strong and weak prerequisite learners follow demonstrably different paths;
- automated tests cover critical deterministic behavior;
- end-to-end Window Functions scenario passes.

# Phase 14 — Graphical Interface

## TASK-140 — Streamlit application shell

Create a local Streamlit entrypoint and document how to start it.

Acceptance: the application starts locally, accepts a learning request and
preserves the active session across reruns.

## TASK-141 — Tutor conversation interface

Connect the interface to the orchestration service and support multiple
learner turns, including diagnostic questions.

## TASK-142 — SQL practice interface

Add a SQL editor and execution controls. Display rows, columns, row count and
PostgreSQL errors, keeping submitted SQL and actual output available for
evaluation.

## TASK-143 — Learning progress panel

Display scenario, short-horizon path, concepts, mastery, confidence and recent
evidence, distinguishing remediation, practice and advancement.

## TASK-144 — GUI end-to-end validation

Validate the Window Functions flow and ensure strong/weak prerequisite path
divergence remains observable in the interface.

# Phase 15 — Integrated Pedagogical Application

## TASK-150 — Application/session service

Create one application boundary that loads state, invokes the tutor, dispatches
tools, persists events and returns the learner-facing response. The GUI must
not assemble domain services directly.

## TASK-151 — Complete diagnostic transition

Connect PROBE turns to evidence, baseline, scenario, path and automatic lab
provisioning. The lab must not be created before sufficient diagnosis.

## TASK-152 — Evaluated SQL interaction

Connect learner SQL to evaluation, evidence persistence, mastery updates and
the adapted next action. The evaluator must receive requirement, SQL and real
result/error.

## TASK-153 — Adaptive multi-turn continuation

Ensure newly persisted evidence changes subsequent teaching, remediation,
practice, review, Apply or Transfer actions. Strong and weak learners must
diverge through the same application path.

## TASK-154 — Full application acceptance

Validate the complete Window Functions journey through the GUI without manual
service orchestration or database preparation. V1 must not be declared complete
if the path divergence is not demonstrated through the integrated application.
