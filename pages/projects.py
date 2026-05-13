import streamlit as st
import pandas as pd

from database import (
    create_project,
    list_projects,
    get_project,
    save_project_memory,
    list_project_memory,
)


# =========================================================
# HELPERS
# =========================================================

def current_user():
    return st.session_state.get("user")


def open_project(project_id):
    st.session_state.active_project_id = int(project_id)
    st.rerun()


# =========================================================
# CREATE PROJECT
# =========================================================

def render_create_project():

    st.subheader("🚀 Create New Project")

    with st.container(border=True):

        title = st.text_input(
            "Project Name",
            placeholder="e.g. Arsenal Content Campaign",
        )

        description = st.text_area(
            "Description",
            height=120,
            placeholder="Describe your workflow, campaign or project...",
        )

        workspace = st.selectbox(
            "Primary Workspace",
            [
                "general",
                "football",
                "content_engine",
                "developer_os",
                "creative_workspace",
                "media_studio",
                "automation_lab",
            ],
        )

        if st.button("✨ Create Project", use_container_width=True):

            if not title:
                st.warning("Please enter a project title.")
                return

            project_id = create_project(
                username=current_user(),
                title=title,
                description=description,
                workspace=workspace,
            )

            st.session_state.active_project_id = project_id

            st.success("Project created.")
            st.rerun()


# =========================================================
# PROJECT LIST
# =========================================================

def render_project_list():

    st.subheader("📂 Your Projects")

    projects = list_projects(current_user())

    if not projects:
        st.info("No projects yet.")
        return

    for project in projects:

        with st.container(border=True):

            st.markdown(f"### 🚀 {project.get('title')}")

            st.caption(project.get("workspace", "general"))

            st.write(project.get("description", ""))

            c1, c2, c3 = st.columns(3)

            with c1:
                st.write(f"Created: {project.get('created_at', '')[:16]}")

            with c2:
                st.write(f"Updated: {project.get('updated_at', '')[:16]}")

            with c3:
                if st.button(
                    "Open",
                    key=f"open_project_{project.get('id')}",
                    use_container_width=True,
                ):
                    open_project(project.get("id"))


# =========================================================
# PROJECT MEMORY
# =========================================================

def render_project_memory(project_id):

    project = get_project(project_id)

    if not project:
        st.error("Project not found.")
        return

    st.subheader(f"🧠 Workspace Memory — {project.get('title')}")

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
            ],
        )

        content = st.text_area(
            "Memory Content",
            height=180,
        )

        if st.button("💾 Save Memory", use_container_width=True):

            if not content:
                st.warning("Please enter content.")
                return

            save_project_memory(
                project_id=project_id,
                username=current_user(),
                workspace=project.get("workspace", "general"),
                memory_type=memory_type,
                content=content,
            )

            st.success("Memory saved.")
            st.rerun()

    st.divider()

    memories = list_project_memory(project_id)

    if not memories:
        st.info("No workspace memory yet.")
        return

    for memory in memories:

        with st.container(border=True):

            st.markdown(
                f"### 🧠 {memory.get('memory_type', 'memory').title()}"
            )

            st.caption(memory.get("created_at", "")[:16])

            st.write(memory.get("content", ""))


# =========================================================
# MAIN
# =========================================================

def render_projects():

    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    st.title("🛰️ Projects Workspace")
    st.caption(
        "Persistent AI workflows, workspace memory and project intelligence."
    )

    left, right = st.columns([1, 1])

    with left:
        render_create_project()

    with right:
        render_project_list()

    active_project = st.session_state.get("active_project_id")

    if active_project:

        st.divider()

        render_project_memory(active_project)