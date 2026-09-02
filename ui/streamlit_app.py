"""Local graphical interface for the Adaptive SQL Tutor."""

import streamlit as st

from app.config import Settings
from app.lab.service import LabService
from app.learning.diagnostic import DiagnosticService
from app.learning.state_service import LearningStateService
from app.llm.client import OpenAIClient
from app.llm.prompt_loader import load_prompt
from app.persistence.database import Database
from app.persistence.repositories import LearningRepository
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
    st.set_page_config(page_title="Adaptive SQL Tutor", layout="wide")
    st.title("Adaptive SQL Tutor")
    settings, database, repository = services()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "last_sql" not in st.session_state:
        st.session_state.last_sql = None
    if "last_sql_result" not in st.session_state:
        st.session_state.last_sql_result = None

    with st.sidebar:
        st.header("Aprendizagem")
        if st.session_state.session_id:
            try:
                state = LearningStateService(repository).load(st.session_state.session_id)
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
                    st.rerun()
        else:
            st.info("Inicie uma sessão para ver seu progresso.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("O que você quer aprender?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            if st.session_state.session_id is None:
                session = DiagnosticService(repository).start(prompt)
                st.session_state.session_id = session.session_id
            state = LearningStateService(repository).load(st.session_state.session_id)
            client = OpenAIClient(settings.llm_model, settings.llm_api_key.get_secret_value(), settings.llm_base_url)
            response = TutorOrchestrator(client, create_registry(database), load_prompt(), max_iterations=8).respond(prompt, state)
            answer = response.message or "O tutor solicitou uma ação de aprendizagem."
        except Exception as exc:
            answer = f"Não foi possível processar esta interação: {exc}"
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

    st.divider()
    st.subheader("Laboratório SQL")
    sql = st.text_area("Escreva uma consulta SQL", height=150, key="sql_editor")
    if st.button("Executar SQL"):
        if not st.session_state.session_id:
            st.warning("Inicie uma sessão antes de executar SQL.")
        elif not sql.strip():
            st.warning("Digite uma consulta SQL.")
        else:
            result = LabService(database).execute(sql)
            st.session_state.last_sql = sql
            st.session_state.last_sql_result = result.model_dump(mode="json")
            if result.success:
                st.dataframe([dict(zip(result.columns, row)) for row in result.rows], use_container_width=True)
                st.caption(f"{result.row_count} linha(s)")
            else:
                st.error(result.error)
            st.caption("A consulta e o resultado permanecem disponíveis nesta sessão para avaliação do tutor.")


if __name__ == "__main__":
    main()
