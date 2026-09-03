# Adaptive SQL Tutor — Requirements

## 1. Purpose

Build a local adaptive SQL learning application capable of diagnosing a learner, constructing a contextual learning scenario, dynamically creating an executable PostgreSQL environment, evaluating real SQL execution, and adapting subsequent instruction based on evidence.

## 2. Product Scope

V1 SHALL support:

- one local learner;
- one active local application;
- SQL learning only;
- PostgreSQL as the SQL dialect and execution engine;
- dynamic Learning Lab creation;
- LLM-driven adaptive tutoring;
- persistent learning state.
- a local graphical interface implemented with Streamlit.

V1 SHALL NOT require:

- authentication;
- multi-user isolation;
- cloud infrastructure;
- distributed processing;
- multi-agent orchestration.
- a separate frontend/backend deployment.

The graphical interface SHALL allow the learner to enter a learning request,
interact through multiple turns, answer diagnostic questions, write and
execute SQL, see results/errors, and see scenario, path and mastery.

The integrated application SHALL connect the graphical interface, tutor
orchestrator, learning state, tools and evaluation into one continuous learner
experience. Each learner turn SHALL update the persisted session and return the
next tutor action without manual service orchestration.

## 6.2 V1 robustness

The application SHALL provide specific tool schemas, preserve tool results in
the next tutor context, make failures observable, and enforce appropriate
statement, transaction, timeout and result-size controls for learner SQL.

---

# 3. Core Learning Lifecycle

The system SHALL implement:

`INTENT → PROBE → DIAGNOSE → PLAN → CREATE LAB → TEACH → PRACTICE → EXECUTE → EVALUATE → ADAPT → REVIEW → APPLY → TRANSFER TEST`

The application SHALL autonomously manage transitions between learning phases.

The learner SHALL NOT be required to manually select every phase.

---

# 4. Learning Request

The system SHALL accept natural-language requests such as:

`Quero aprender Window Functions`

`Quero aprender JOIN`

`Quero aprender CTE`

`Quero aprender otimização de queries`

The requested subject SHALL be interpreted as an initial learning intent rather than a predefined course.

---

# 5. Intent Discovery

The system SHOULD determine the learner's objective when the topic alone is insufficient.

Possible objectives include:

- conceptual understanding;
- practical query writing;
- analytics;
- Data Engineering;
- query optimization;
- interview preparation;
- advanced mastery.

Intent discovery SHOULD use the minimum number of questions necessary.

The Learning Lab SHALL NOT be created during initial intent discovery.

---

# 6. PROBE

The system SHALL diagnose the learner before teaching the requested topic.

The PROBE SHOULD use approximately 5–12 questions, but SHALL terminate earlier when sufficient evidence exists.

Questions MAY include:

- concepts;
- query interpretation;
- predicted query results;
- query comparison;
- debugging;
- small query construction;
- practical problems.

Difficulty SHALL adapt according to previous answers.

The system SHALL investigate prerequisites when weaknesses are detected.

The tutor SHALL NOT teach answers during the diagnostic phase.

---

# 7. Learner Model

The system SHALL maintain knowledge state by concept.

Each concept SHALL support at least:

- `mastery`
- `confidence`
- `misconception`

Mastery SHALL use a normalized range:

`0.00–1.00`

Approximate interpretation:

`>= 0.80` operational mastery

`0.50–0.79` partial mastery

`< 0.50` insufficient mastery

Confidence SHALL represent evidence strength and SHALL support:

- low;
- medium;
- high.

A single correct answer SHALL NOT automatically establish mastery.

---

# 8. Learning Evidence

Mastery changes SHALL be based on evidence.

Evidence MAY originate from:

- diagnostic answers;
- conceptual explanations;
- query interpretation;
- query construction;
- execution;
- debugging;
- result interpretation;
- Apply;
- Transfer Test.

Evidence SHOULD capture:

- concept;
- evidence type;
- difficulty;
- correctness;
- reasoning quality;
- number of attempts;
- assistance received;
- raw contextual evidence where useful.

---

# 9. Learning Scenario

After sufficient diagnostic evidence exists, the system SHALL create an initial Learning Scenario.

The scenario SHALL contain or represent:

- requested topic;
- learning objective;
- initial level;
- target capability;
- mastered prerequisites;
- partial knowledge;
- gaps;
- misconceptions;
- relevant concepts;
- pedagogical strategy;
- initial difficulty;
- required exercise types;
- required SQL environment.

The scenario SHALL be mutable.

New evidence MAY cause the scenario to evolve.

---

# 10. Knowledge Dependency Graph

The system SHALL represent relevant knowledge as dependencies between concepts.

The graph SHALL be contextual to the Learning Scenario.

The system SHALL NOT require creation of a complete universal SQL knowledge graph before learning begins.

New concepts and dependencies MAY be introduced when learning evidence exposes previously unidentified prerequisites.

---

# 11. Learning Path

The Learning Path SHALL be derived from:

`Learning Scenario + Knowledge Graph + Learner Model`

The path SHALL NOT be treated as a fixed course.

Planning SHOULD prioritize a short horizon:

- current;
- next;
- near future.

New evidence SHALL be capable of changing the next learning action.

Mastered concepts SHOULD be skipped or reduced.

Partial concepts SHOULD receive additional practice.

Insufficient prerequisites SHOULD trigger remediation.

---

# 12. SQL Learning Lab

After the initial Learning Scenario is created, the system SHALL create an executable PostgreSQL Learning Lab when executable practice is pedagogically useful.

The lab SHALL use the PostgreSQL schema:

`lab`

The Learning Lab MAY contain:

- tables;
- constraints;
- primary keys;
- foreign keys;
- indexes;
- views;
- sequences;
- data.

The lab SHALL initially contain only structures needed by the current learning horizon.

---

# 13. Pedagogical Dataset Requirements

Learning Lab data SHALL NOT be meaningless random data.

Dataset design SHALL intentionally support the concepts being taught.

Examples:

### Window Functions

Dataset SHOULD contain:

- multiple records per partition;
- temporal ordering;
- ties;
- different partition sizes.

### Ranking

Dataset SHALL contain ties when teaching differences among:

- `ROW_NUMBER`;
- `RANK`;
- `DENSE_RANK`.

### LAG / LEAD

Dataset SHOULD contain meaningful temporal sequences.

### JOIN

Dataset SHOULD include:

- matching rows;
- unmatched rows;
- appropriate relationship cardinalities.

### NULL semantics

Dataset SHALL intentionally contain NULL values.

### Deduplication

Dataset SHALL contain controlled duplicate records.

### Recursive CTE

Dataset SHALL contain hierarchical relationships.

### Performance

Dataset volume and distribution SHALL be sufficient to demonstrate the targeted planner/execution behavior.

---

# 14. Learning Lab Evolution

The Learning Lab SHALL be mutable.

The tutor MAY request:

- new tables;
- new columns;
- new relationships;
- new indexes;
- additional data;
- new edge cases;
- changed data distributions.

Lab evolution SHALL be driven by pedagogical need.

The system SHOULD avoid unnecessary lab complexity.

---

# 15. Executable Practice

The system SHALL support four primary exercise modes.

## Execute

Tutor provides SQL.

Learner executes and interprets the result.

## Build

Tutor provides a requirement.

Learner writes and executes SQL.

## Debug

Learner diagnoses and fixes incorrect SQL.

## Modify

Learner modifies working SQL to satisfy a changed requirement.

Exercise difficulty SHALL adapt to the Learner Model.

---

# 16. SQL Execution

Learner SQL SHALL execute against the real local PostgreSQL Learning Lab.

Execution SHALL return at least:

- success/failure;
- columns;
- rows;
- row count;
- PostgreSQL error when applicable.

The tutor SHALL receive the actual execution result when evaluating an executable exercise.

---

# 17. Evaluation

Evaluation SHALL distinguish:

- syntax;
- execution;
- semantics;
- logical correctness;
- requirement satisfaction;
- reasoning quality.

Successful execution SHALL NOT automatically imply a correct solution.

Correct output SHALL NOT automatically imply mastery.

---

# 18. Adaptation

After relevant evaluation, the system SHALL update learning evidence and learner state.

Adaptation MAY modify:

- mastery;
- confidence;
- misconception state;
- current concept;
- next concept;
- exercise difficulty;
- teaching strategy;
- Knowledge Graph;
- Learning Scenario;
- Learning Path;
- Learning Lab.

Persistent errors SHOULD trigger prerequisite investigation.

---

# 19. Socratic Correction

When pedagogically appropriate, incorrect answers SHOULD follow:

`ERROR → SOCRATIC QUESTION → SELF-CORRECTION → HINT → RETRY → EXPLANATION`

The tutor SHOULD use actual query results to encourage self-correction.

The tutor SHOULD avoid revealing the complete answer prematurely.

---

# 20. Review

The system SHALL periodically revisit previously learned concepts.

Review SHOULD mix:

- current concepts;
- previous concepts;
- relationships;
- new problems.

Review SHALL test retrieval rather than simple recognition.

Evidence of forgetting SHALL be capable of returning concepts to the active Learning Path.

---

# 21. Apply

After essential concepts reach operational mastery, the system SHALL create a realistic multi-concept problem.

The learner SHOULD:

`ANALYZE → PROPOSE → JUSTIFY → IMPLEMENT → EXECUTE → VALIDATE → CRITIQUE`

The initial solution SHALL NOT be provided.

---

# 22. Transfer Test

After Apply, the system SHALL present a different context requiring substantially the same underlying principles.

The test SHOULD avoid superficial reuse of identical tables, names and values.

Failure SHALL identify concepts requiring further learning.

---

# 23. Persistence

The application SHALL persist sufficient state to continue learning without depending exclusively on conversational history.

At minimum persist:

- learning session;
- concepts;
- mastery;
- confidence;
- misconceptions;
- evidence;
- learning events.

---

# 24. Application Database Separation

The PostgreSQL instance SHALL contain logically separate schemas.

## `tutor`

Persistent application and learning metadata.

## `lab`

Dynamic executable learning environment.

Dynamic lab operations SHALL target `lab`.

The tutor SHALL NOT dynamically modify the internal `tutor` schema.

---

# 25. LLM Integration

The application SHALL use structured LLM outputs for application actions.

Application behavior SHALL NOT depend on parsing arbitrary prose to identify tool calls.

LLM/tool boundaries SHOULD use validated structured models.

## 25.1 LLM resilience

The LLM client SHALL load a configurable per-request timeout from
`LLM_TIMEOUT_SECONDS` in the environment configuration.

The LLM client SHALL use bounded retries with exponential backoff for transient
provider failures, including HTTP `429`, `500`, `502`, `503` and `504`.

The retry policy SHALL:

- have a finite maximum number of attempts;
- respect the configured request timeout;
- avoid retrying malformed requests, invalid credentials or structured-output
  validation failures;
- expose a sanitized, actionable error when all attempts fail;
- never log API keys or complete learner prompts/responses.

The application SHALL remain responsive while an LLM request is pending and
the GUI SHALL distinguish a transient provider failure from an invalid learner
input or an application failure.

The initial tool set SHALL support:

- create lab;
- execute SQL;
- inspect lab;
- extend lab;
- reset lab;
- load learning state;
- save learning evidence.

Tool execution resilience:

- `create_lab` SHALL validate all DDL and seed SQL in a rollback-only
  PostgreSQL transaction before replacing `lab`;
- `extend_lab` SHALL validate its DDL/DML in a rollback-only transaction before
  applying the extension;
- validation and execution failures SHALL be returned to the tutor as
  structured results containing success status and a sanitized error;
- malformed tool arguments SHALL be observable by the tutor and SHALL NOT
  terminate the learner turn;
- the orchestrator SHALL stop repeated identical tool calls and SHALL return a
  controlled learner-facing response when its iteration limit is reached.

---

# 26. Adaptive Acceptance Scenario

Given:

`Quero aprender Window Functions`

the system SHALL:

1. begin diagnosis rather than teaching;
2. collect prerequisite evidence;
3. create an initial Learner Model;
4. create a contextual Learning Scenario;
5. create a relevant Knowledge Graph;
6. determine the initial Learning Path;
7. create and populate a suitable PostgreSQL Learning Lab;
8. provide executable practice;
9. execute learner SQL;
10. evaluate actual execution results;
11. record evidence;
12. update mastery;
13. select subsequent learning actions based on evidence.

The system SHALL demonstrate at least two divergent paths.

Example:

Learner A demonstrates strong aggregation and granularity knowledge.

Expected:

`proceed toward Window Functions`

Learner B demonstrates weak aggregation/granularity knowledge.

Expected:

`remediate prerequisite → reassess → proceed toward Window Functions`

This divergence is a core V1 acceptance criterion.

---

# 27. Non-Functional Requirements

The V1 SHOULD favor:

- simplicity;
- observability;
- testability;
- deterministic tool execution;
- explicit contracts;
- reproducibility.

The application SHALL run locally.

The application SHOULD be startable with a small number of documented commands.

Failures from PostgreSQL or LLM calls SHALL be observable and diagnosable.

---

# 28. V1 Success Criteria

V1 is successful when it proves that:

1. diagnosis affects learning;
2. learning creates its own executable environment;
3. SQL practice uses real PostgreSQL execution;
4. execution produces learning evidence;
5. evidence changes subsequent learning behavior;
6. the environment itself can evolve as learning evolves.

Future evolution MAY include richer Gemini capabilities, browser testing,
stronger observability and additional SQL scenarios. These are outside the
local single-user V1.
