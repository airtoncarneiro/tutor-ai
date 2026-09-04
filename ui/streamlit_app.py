"""Local graphical interface for the Adaptive SQL Tutor AI."""

import streamlit as st
from uuid import UUID

from app.config import Settings
from app.lab.service import LabService
from app.application.session_service import ApplicationSessionService
from app.llm.client import OpenAIClient
from app.llm.prompt_loader import load_prompt
from app.persistence.database import Database
from app.persistence.repositories import LearningRepository
from app.learning.state_service import LearningStateService
from app.tools.factory import create_registry
from app.tutor.orchestrator import TutorOrchestrator


@st.cache_resource
def services():
    settings = Settings()
    database = Database(settings.postgres_dsn)
    database.migrate()
    repository = LearningRepository(database)
    return settings, database, repository


def main() -> None:
    st.set_page_config(page_title="Adaptive SQL Tutor AI", layout="wide")
    st.title("Adaptive SQL Tutor AI")
    settings, database, repository = services()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        raw_session_id = st.query_params.get("session_id")
        try:
            restored_id = UUID(raw_session_id) if raw_session_id else None
            st.session_state.session_id = restored_id if restored_id and repository.get_session(restored_id) else None
        except ValueError:
            st.session_state.session_id = None
        if st.session_state.session_id:
            for event in repository.events(st.session_state.session_id):
                if event.event_type == "LEARNER_MESSAGE":
                    st.session_state.messages.append({"role": "user", "content": event.payload.get("message", "")})
                elif event.event_type == "TUTOR_RESPONSE":
                    st.session_state.messages.append({"role": "assistant", "content": event.payload.get("message", "")})
    if "last_sql" not in st.session_state:
        st.session_state.last_sql = None
    if "last_sql_result" not in st.session_state:
        st.session_state.last_sql_result = None

    with st.sidebar:
        st.header("Aprendizagem")
        if st.session_state.session_id:
            try:
                state = ApplicationSessionService(database, repository, OpenAIClient(settings.llm_model, settings.llm_api_key.get_secret_value(), settings.llm_base_url, settings.llm_timeout_seconds), load_prompt()).state(st.session_state.session_id)
            except Exception as exc:
                st.error(f"Falha ao carregar o estado: {exc}")
                state = None
            if state:
                st.write(f"**Sessão:** `{str(st.session_state.session_id)[:8]}`")
                st.write(f"**Tópico:** {state['topic']}")
                st.write(f"**Fase:** {state['phase']}")
                st.write(f"**Objetivo:** {state['goal'] or 'a definir pelo diagnóstico'}")
                scenario = state.get("scenario") or {}
                if scenario:
                    st.subheader("Cenário")
                    st.json({key: scenario[key] for key in ("level", "target_capabilities", "strengths", "gaps") if key in scenario})
                    path = scenario.get("learning_path")
                    if path:
                        st.subheader("Próximas ações")
                        st.write(f"Atual: **{path.get('current') or 'nenhuma'}**")
                        st.json({"next": path.get("next", []), "near_future": path.get("near_future", [])})
                st.subheader("Domínio por conceito")
                for concept in state["concepts"]:
                    st.metric(concept["name"], f"{concept['mastery']:.0%}", concept["confidence"])
                if state["recent_evidence"]:
                    st.subheader("Evidências recentes")
                    st.dataframe(state["recent_evidence"], use_container_width=True, hide_index=True)
                if st.button("Nova sessão"):
                    st.session_state.session_id = None
                    st.session_state.messages = []
                    st.query_params.pop("session_id", None)
                    st.rerun()
        else:
            st.info("Inicie uma sessão para ver seu progresso.")

    if not st.session_state.session_id:
        st.subheader("Comece seu aprendizado")
        st.write("Informe o tema de SQL que você quer aprender. O tutor fará algumas perguntas antes de criar seu plano de estudos.")
        initial_topic = st.text_input("O que você quer aprender?", placeholder="Ex.: Window Functions")
        if st.button("Iniciar aprendizado", type="primary"):
            if not initial_topic.strip():
                st.warning("Informe um tema para começar.")
            else:
                try:
                    client = OpenAIClient(settings.llm_model, settings.llm_api_key.get_secret_value(), settings.llm_base_url, settings.llm_timeout_seconds)
                    service = ApplicationSessionService(database, repository, client, load_prompt())
                    st.session_state.session_id, response = service.turn(initial_topic, None)
                    st.session_state.messages.extend([
                        {"role": "user", "content": initial_topic},
                        {"role": "assistant", "content": response.message or "O tutor iniciou o diagnóstico."},
                    ])
                    st.query_params["session_id"] = str(st.session_state.session_id)
                    st.rerun()
                except Exception as exc:
                    st.error(f"Não foi possível iniciar o aprendizado: {exc}")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.session_id and (prompt := st.chat_input("Continue sua conversa com o tutor")):
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            client = OpenAIClient(settings.llm_model, settings.llm_api_key.get_secret_value(), settings.llm_base_url, settings.llm_timeout_seconds)
            service = ApplicationSessionService(database, repository, client, load_prompt())
            st.session_state.session_id, response = service.turn(prompt, st.session_state.session_id)
            st.query_params["session_id"] = str(st.session_state.session_id)
            answer = response.message or "O tutor solicitou uma ação de aprendizagem."
        except Exception as exc:
            answer = f"Não foi possível processar esta interação: {exc}"
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

    if not st.session_state.session_id:
        st.info("O laboratório SQL aparecerá depois que você iniciar uma sessão de aprendizado.")
        return

    st.divider()
    st.subheader("Laboratório SQL")
    if st.button("Preparar cenário e laboratório"):
        try:
            service = ApplicationSessionService(database, repository, OpenAIClient(settings.llm_model, settings.llm_api_key.get_secret_value(), settings.llm_base_url, settings.llm_timeout_seconds), load_prompt())
            service.prepare_learning(st.session_state.session_id)
            st.success("Cenário e laboratório preparados.")
            st.rerun()
        except Exception as exc:
            st.error(f"Falha ao preparar o laboratório: {exc}")

    state = LearningStateService(repository).load(st.session_state.session_id)
    exercises = (state.get("scenario") or {}).get("initial_exercises", [])
    if exercises:
        st.subheader("Exercício atual")
        for exercise in exercises:
            st.markdown(f"**Enunciado:** {exercise['instruction']}")
            if exercise.get("requirement"):
                st.caption(f"Requisito: {exercise['requirement']}")
    else:
        st.info("O tutor ainda está preparando o primeiro exercício.")

    sql = st.text_area("Escreva uma consulta SQL", height=150, key="sql_editor")
    concepts = []
    if st.session_state.session_id:
        concepts = LearningStateService(repository).load(st.session_state.session_id)["concepts"]
    concept_key = st.selectbox("Conceito avaliado", [c["concept_key"] for c in concepts] or ["window_semantics"])
    semantics = st.slider("Semântica correta", 0.0, 1.0, 0.0, 0.1)
    requirement = st.slider("Atendimento ao requisito", 0.0, 1.0, 0.0, 0.1)
    reasoning = st.slider("Qualidade do raciocínio", 0.0, 1.0, 0.0, 0.1)
    if st.button("Executar SQL"):
        if not st.session_state.session_id:
            st.warning("Inicie uma sessão antes de executar SQL.")
        elif not sql.strip():
            st.warning("Digite uma consulta SQL.")
        else:
            result = LabService(database).execute(sql)
            st.session_state.last_sql = sql
            st.session_state.last_sql_result = result.model_dump(mode="json")

    if st.session_state.last_sql_result:
        stored_result = st.session_state.last_sql_result
        if stored_result["success"]:
            st.dataframe([dict(zip(stored_result["columns"], row)) for row in stored_result["rows"]], use_container_width=True)
            st.caption(f"{stored_result['row_count']} linha(s)")
        else:
            st.error(stored_result["error"])
        st.caption("A consulta e o resultado permanecem disponíveis nesta sessão para avaliação do tutor.")
        if stored_result["success"] and st.session_state.session_id and st.button("Avaliar esta tentativa"):
            try:
                service = ApplicationSessionService(database, repository, OpenAIClient(settings.llm_model, settings.llm_api_key.get_secret_value(), settings.llm_base_url, settings.llm_timeout_seconds), load_prompt())
                evaluation = service.submit_sql(st.session_state.session_id, st.session_state.last_sql, concept_key, requirement, semantics, reasoning)
                st.success(f"Avaliação registrada. Próxima ação: {evaluation['next_action']}")
            except Exception as exc:
                st.error(f"Falha ao avaliar: {exc}")


if __name__ == "__main__":
    main()
