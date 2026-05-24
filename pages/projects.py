import streamlit as st

from database import (
    create_project,
    list_projects,
    get_project,
    save_project_memory,
    list_project_memory,
)


def current_user():
    return st.session_state.get("user")


def open_page(page):
    st.session_state.page = page
    st.rerun()


def open_project(project_id):
    st.session_state.active_project_id = int(project_id)
    st.rerun()


def workspace_label(workspace):
    labels = {
        "general": "ðŸ›°ï¸ General",
        "football": "âš½ Football Intelligence",
        "content_engine": "ðŸ“£ Content Engine",
        "developer_os": "ðŸ’» Developer OS",
        "creative_workspace": "ðŸŽ¨ Creative Workspace",
        "media_studio": "ðŸŽ¬ Media Studio",
        "automation_lab": "ðŸ§ª Automation Lab",
    }

    return labels.get(workspace, workspace)


def render_create_project():
    st.subheader("ðŸš€ Neues Projekt")

    with st.container(border=True):
        title = st.text_input(
            "Projektname",
            placeholder="z.B. Arsenal Content Campaign",
        )

        description = st.text_area(
            "Beschreibung",
            height=120,
            placeholder="Beschreibe Ziel, Workflow oder Kampagne...",
        )

        workspace = st.selectbox(
            "PrimÃ¤rer Workspace",
            [
                "general",
                "football",
                "content_engine",
                "developer_os",
                "creative_workspace",
                "media_studio",
                "automation_lab",
            ],
            format_func=workspace_label,
        )

        if st.button("âœ¨ Projekt erstellen", width="stretch"):
            if not title:
                st.warning("Bitte Projektnamen eingeben.")
                return

            project_id = create_project(
                username=current_user(),
                title=title,
                description=description,
                workspace=workspace,
            )

            st.session_state.active_project_id = project_id
            st.success("Projekt erstellt.")
            st.rerun()


def render_project_card(project):
    project_id = project.get("id")
    title = project.get("title", "Untitled")
    workspace = project.get("workspace", "general")

    with st.container(border=True):
        st.markdown(f"### ðŸš€ {title}")
        st.caption(workspace_label(workspace))
        st.write(project.get("description", ""))

        c1, c2 = st.columns(2)

        with c1:
            st.caption(f"Created: {project.get('created_at', '')[:16]}")

        with c2:
            st.caption(f"Updated: {project.get('updated_at', '')[:16]}")

        c3, c4, c5 = st.columns(3)

        with c3:
            if st.button("Ã–ffnen", key=f"open_project_{project_id}", width="stretch"):
                open_project(project_id)

        with c4:
            if st.button("AI Chat", key=f"chat_project_{project_id}", width="stretch"):
                st.session_state.active_project_id = int(project_id)
                open_page("chat")

        with c5:
            if st.button("Automation", key=f"auto_project_{project_id}", width="stretch"):
                st.session_state.active_project_id = int(project_id)
                open_page("automation_lab")


def render_project_list():
    st.subheader("ðŸ“‚ Deine Projekte")

    projects = list_projects(current_user())

    if not projects:
        st.info("Noch keine Projekte vorhanden.")
        return

    for project in projects:
        render_project_card(project)


def render_project_memory(project_id):
    project = get_project(project_id, username=current_user())

    if not project:
        st.error("Projekt nicht gefunden.")
        return

    st.subheader(f"ðŸ§  Workspace Memory â€” {project.get('title')}")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("ðŸ§  Mit AI Ã¶ffnen", width="stretch"):
            open_page("chat")

    with c2:
        if st.button("ðŸ§ª Automation bauen", width="stretch"):
            open_page("automation_lab")

    with c3:
        if project.get("workspace") == "football":
            if st.button("âš½ Football Ã¶ffnen", width="stretch"):
                open_page("football")
        else:
            st.button("âš¡ Workspace aktiv", width="stretch", disabled=True)

    with st.container(border=True):
        memory_type = st.selectbox(
            "Memory Type",
            [
                "notes",
                "strategy",
                "prompt",
                "workflow",
                "analysis",
                "content",
                "brand",
                "target_audience",
                "agent_instruction",
            ],
        )

        content = st.text_area(
            "Memory Content",
            height=180,
            placeholder="Speichere Kontext, Ziele, Stil, Strategie oder Agent-Anweisungen...",
        )

        if st.button("ðŸ’¾ Memory speichern", width="stretch"):
            if not content:
                st.warning("Bitte Inhalt eingeben.")
                return

            save_project_memory(
                project_id=project_id,
                username=current_user(),
                workspace=project.get("workspace", "general"),
                memory_type=memory_type,
                content=content,
            )

            st.success("Memory gespeichert.")
            st.rerun()

    st.divider()

    memories = list_project_memory(project_id)

    if not memories:
        st.info("Noch keine Workspace Memory gespeichert.")
        return

    for memory in memories:
        with st.container(border=True):
            st.markdown(f"### ðŸ§  {memory.get('memory_type', 'memory').title()}")
            st.caption(memory.get("created_at", "")[:16])
            st.write(memory.get("content", ""))


def render_projects():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    st.title("ðŸ›°ï¸ Projects")
    st.caption("Persistent AI workflows, Workspace Memory und Project Intelligence.")

    left, right = st.columns([1, 1.2], gap="large")

    with left:
        render_create_project()

    with right:
        render_project_list()

    active_project = st.session_state.get("active_project_id")

    if active_project:
        st.divider()
        render_project_memory(active_project)
