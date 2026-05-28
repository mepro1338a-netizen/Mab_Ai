import streamlit as st

from database import (
    list_projects,
    create_automation,
    list_automations,
    list_automation_runs,
)

from agent_runner import run_automation


def current_user():
    return st.session_state.get("user")


def project_options():
    projects = list_projects(current_user())
    options = {"Kein Projekt": 0}

    for p in projects:
        options[f"{p.get('title')} · {p.get('workspace')}"] = p.get("id")

    return options


def render_agent_card(icon, title, desc, agent_type):
    with st.container(border=True):
        st.markdown(f"### {icon} {title}")
        st.caption(desc)

        if st.button(
            "Agent auswählen",
            key=f"agent_{agent_type}",
            width="stretch",
        ):
            st.session_state.selected_agent_type = agent_type
            st.success(f"{title} ausgewählt")


def render_create_automation():
    st.subheader("Workflow erstellen")

    options = project_options()

    with st.container(border=True):
        name = st.text_input(
            "Workflow Name",
            placeholder="z.B. Football Match â†’ Reel Package",
        )

        project_label = st.selectbox("Projekt", list(options.keys()))
        project_id = options[project_label]

        selected_agent = st.session_state.get(
            "selected_agent_type",
            "football_content_agent",
        )

        agent_options = [
            "football_content_agent",
            "content_repurpose_agent",
            "developer_report_agent",
            "creative_asset_agent",
            "social_posting_agent",
        ]

        default_index = (
            agent_options.index(selected_agent)
            if selected_agent in agent_options
            else 0
        )

        automation_type = st.selectbox(
            "Agent Type",
            agent_options,
            index=default_index,
            format_func=lambda x: x.replace("_", " ").title(),
        )

        source = st.selectbox(
            "Source Workspace",
            [
                "football",
                "content_engine",
                "developer_os",
                "creative_workspace",
                "media_studio",
                "ai_assistant",
            ],
        )

        target = st.selectbox(
            "Target Workspace",
            [
                "content_engine",
                "automation_lab",
                "media_studio",
                "projects",
                "ai_assistant",
            ],
        )

        from ui.prompt_ui import prompt_text_area
        trigger = prompt_text_area(
            placeholder="Trigger und Anweisung beschreiben…",
            label="Automation",
            key="auto_lab_trigger",
            height=140,
        )

        if st.button("Automation erstellen", width="stretch"):
            if not name or not trigger:
                st.warning("Bitte Name und Trigger ausfüllen.")
                return

            if project_id == 0:
                st.warning("Bitte ein Projekt auswählen.")
                return

            automation_id = create_automation(
                username=current_user(),
                project_id=project_id,
                name=name,
                automation_type=automation_type,
                source_workspace=source,
                target_workspace=target,
                trigger_text=trigger,
            )

            st.success(f"Automation erstellt: #{automation_id}")
            st.rerun()


def render_automations():
    st.subheader("Aktive Automations")

    automations = list_automations(current_user())

    if not automations:
        st.info("Noch keine Automationen vorhanden.")
        return

    for item in automations:
        with st.container(border=True):
            st.markdown(f"### {item.get('name')}")
            st.caption(
                f"{item.get('source_workspace')} -> {item.get('target_workspace')}"
            )
            st.write(item.get("trigger_text", ""))

            c1, c2, c3 = st.columns(3)

            with c1:
                st.write(f"Type: {item.get('automation_type')}")

            with c2:
                st.write(f"Status: {item.get('status')}")

            with c3:
                if st.button(
                    "Agent starten",
                    key=f"run_{item.get('id')}",
                    width="stretch",
                ):
                    with st.spinner("Agent läuft..."):
                        result = run_automation(item)

                    if result.get("success"):
                        st.success(
                            f"Agent Run abgeschlossen: #{result.get('run_id')}"
                        )
                    else:
                        st.error(result.get("result"))

                    st.rerun()


def render_runs():
    st.subheader("Automation Runs")

    runs = list_automation_runs(current_user(), limit=50)

    if not runs:
        st.info("Noch keine Runs vorhanden.")
        return

    for run in runs:
        with st.container(border=True):
            st.markdown(f"### Run #{run.get('id')}")
            st.caption(run.get("created_at", "")[:16])
            st.write(f"Automation ID: {run.get('automation_id')}")
            st.write(f"Status: {run.get('status')}")
            st.write(run.get("result", ""))


def render_automation_lab():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    st.title("Automation Lab")
    st.caption("AI Agents, Workflow Chains und Cross-Workspace Intelligence.")

    k1, k2, k3 = st.columns(3)

    with k1:
        st.metric("Agent Engine", "Ready")

    with k2:
        st.metric("Workflow Router", "Online")

    with k3:
        st.metric("Cross-Workspace", "Enabled")

    st.divider()

    st.subheader("AI Agents")

    a, b, c = st.columns(3)

    with a:
        render_agent_card(
            "FB",
            "Football Content Agent",
            "Match Analysis -> Reels, Shorts, Threads und Commentary.",
            "football_content_agent",
        )

    with b:
        render_agent_card(
            "CE",
            "Content Repurpose Agent",
            "Aus einem Output mehrere Social Formate erstellen.",
            "content_repurpose_agent",
        )

    with c:
        render_agent_card(
            "DEV",
            "Developer Report Agent",
            "Code-Änderungen analysieren und Reports erstellen.",
            "developer_report_agent",
        )

    st.divider()

    left, right = st.columns([1, 1], gap="large")

    with left:
        render_create_automation()

    with right:
        render_automations()

    st.divider()

    render_runs()
