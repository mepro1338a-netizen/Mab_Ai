from openai import OpenAI

from config import (
    OPENAI_API_KEY,
    OPENAI_TEXT_MODEL,
)

from database import (
    get_project,
    list_project_memory,
    save_project_memory,
    create_automation_run,
)


client = OpenAI(api_key=OPENAI_API_KEY)


# =========================================================
# HELPERS
# =========================================================

def project_context(project_id):

    project = get_project(project_id)

    if not project:
        return "Kein Projekt gefunden."

    memories = list_project_memory(project_id)

    memory_text = ""

    for memory in memories[:20]:

        memory_text += f"""
[{memory.get('memory_type')}]

{memory.get('content')}
"""

    return f"""
PROJEKT:
{project.get('title')}

WORKSPACE:
{project.get('workspace')}

BESCHREIBUNG:
{project.get('description')}

MEMORY:
{memory_text}
"""


def ai_generate(system_prompt, user_prompt):

    if not OPENAI_API_KEY:
        return "OPENAI_API_KEY fehlt."

    response = client.chat.completions.create(
        model=OPENAI_TEXT_MODEL,
        temperature=0.7,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    return response.choices[0].message.content


# =========================================================
# FOOTBALL CONTENT AGENT
# =========================================================

def football_content_agent(automation, project):

    trigger = automation.get("trigger_text", "")

    prompt = f"""
{project_context(project.get('id'))}

AUFGABE:
{trigger}

Erstelle:

1. Match Analyse
2. Viral Hook
3. TikTok Reel Script
4. Caption
5. Hashtags
6. Posting Strategie
7. Shortform Content Ideen
"""

    result = ai_generate(
        system_prompt="""
Du bist ein professioneller Football Content AI Agent.
Du arbeitest wie ein Elite Social Media + Football Analyst.
""",
        user_prompt=prompt,
    )

    save_project_memory(
        project_id=project.get("id"),
        username=project.get("username"),
        workspace=project.get("workspace"),
        memory_type="football_agent_output",
        content=result,
    )

    return result


# =========================================================
# CONTENT REPURPOSE AGENT
# =========================================================

def content_repurpose_agent(automation, project):

    trigger = automation.get("trigger_text", "")

    prompt = f"""
{project_context(project.get('id'))}

AUFGABE:
{trigger}

Erstelle:
- Twitter/X Thread
- TikTok Hook
- Instagram Caption
- LinkedIn Version
- Newsletter Idee
"""

    result = ai_generate(
        system_prompt="""
Du bist ein Content Repurpose AI Agent.
Du wandelst Inhalte in mehrere Plattform-Formate um.
""",
        user_prompt=prompt,
    )

    save_project_memory(
        project_id=project.get("id"),
        username=project.get("username"),
        workspace=project.get("workspace"),
        memory_type="repurpose_output",
        content=result,
    )

    return result


# =========================================================
# DEVELOPER REPORT AGENT
# =========================================================

def developer_report_agent(automation, project):

    trigger = automation.get("trigger_text", "")

    prompt = f"""
{project_context(project.get('id'))}

AUFGABE:
{trigger}

Erstelle:
- Dev Summary
- Architektur Analyse
- Verbesserungsvorschläge
- Security Hinweise
- Skalierungsplan
"""

    result = ai_generate(
        system_prompt="""
Du bist ein Senior AI Software Architect.
Du analysierst Systeme professionell.
""",
        user_prompt=prompt,
    )

    save_project_memory(
        project_id=project.get("id"),
        username=project.get("username"),
        workspace=project.get("workspace"),
        memory_type="developer_report",
        content=result,
    )

    return result


# =========================================================
# CREATIVE AGENT
# =========================================================

def creative_asset_agent(automation, project):

    trigger = automation.get("trigger_text", "")

    prompt = f"""
{project_context(project.get('id'))}

AUFGABE:
{trigger}

Erstelle:
- Branding Ideen
- Image Prompts
- Visual Direction
- Color Direction
- Creative Concepts
"""

    result = ai_generate(
        system_prompt="""
Du bist ein Creative Director AI Agent.
Du arbeitest modern, hochwertig und markenorientiert.
""",
        user_prompt=prompt,
    )

    save_project_memory(
        project_id=project.get("id"),
        username=project.get("username"),
        workspace=project.get("workspace"),
        memory_type="creative_output",
        content=result,
    )

    return result


# =========================================================
# MAIN EXECUTOR
# =========================================================

def run_automation(automation):

    project = get_project(
        automation.get("project_id"),
        username=automation.get("username"),
    )

    if not project:

        return {
            "success": False,
            "result": "Projekt nicht gefunden.",
        }

    agent_type = automation.get("automation_type")

    try:

        if agent_type == "football_content_agent":

            result = football_content_agent(
                automation,
                project,
            )

        elif agent_type == "content_repurpose_agent":

            result = content_repurpose_agent(
                automation,
                project,
            )

        elif agent_type == "developer_report_agent":

            result = developer_report_agent(
                automation,
                project,
            )

        elif agent_type == "creative_asset_agent":

            result = creative_asset_agent(
                automation,
                project,
            )

        else:

            result = "Unbekannter Agent."

        run_id = create_automation_run(
            automation_id=automation.get("id"),
            username=automation.get("username"),
            status="success",
            result=result[:4000],
        )

        return {
            "success": True,
            "run_id": run_id,
            "result": result,
        }

    except Exception as e:

        create_automation_run(
            automation_id=automation.get("id"),
            username=automation.get("username"),
            status="failed",
            result=str(e),
        )

        return {
            "success": False,
            "result": str(e),
        }
