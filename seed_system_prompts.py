import sys
from sqlmodel import Session, select
sys.path.insert(0, "/var/www/milesync/backend")
from app.database import engine
from app.models.prompt import SystemPrompt

# Agent prompts
from app.agents.foundation_agent import FOUNDATION_SYSTEM_PROMPT
from app.agents.planning_agent import PLANNING_SYSTEM_PROMPT
from app.agents.execution_agent import EXECUTION_SYSTEM_PROMPT
from app.agents.sustainability_agent import SUSTAINABILITY_SYSTEM_PROMPT
from app.agents.support_agent import SUPPORT_SYSTEM_PROMPT
from app.agents.psychological_agent import PSYCHOLOGICAL_SYSTEM_PROMPT

# Goal Extraction prompts (manual copy as they are inside a function)
GOAL_EXTRACTION_TEMPLATE = """Based on the following goal coaching conversation, extract a structured goal with milestones and tasks.

The goal should be SMART (Specific, Measurable, Achievable, Relevant, Time-bound).
Today's date is {date}. IMPORTANT: Ensure all target dates (goal and milestones) are strictly in the future, starting after {date}.
Create 3-7 milestones that logically progress toward the goal.
Each milestone should have 2-5 specific, actionable tasks.

Conversation:
{conversation}

Extract the goal structure using the provided function."""

GOAL_EXTRACTION_SYSTEM = "You are a goal extraction assistant. Analyze conversations and extract structured goals."

PROMPTS = {
    "foundation_system_prompt": {
        "description": "System prompt for Foundation Agent (Intake & Assessment)",
        "content": FOUNDATION_SYSTEM_PROMPT
    },
    "planning_system_prompt": {
        "description": "System prompt for Planning Agent (Roadmap creation)",
        "content": PLANNING_SYSTEM_PROMPT
    },
    "execution_system_prompt": {
        "description": "System prompt for Execution Agent (Daily tracking & adjustment)",
        "content": EXECUTION_SYSTEM_PROMPT
    },
    "sustainability_system_prompt": {
        "description": "System prompt for Sustainability Agent (Habit formation)",
        "content": SUSTAINABILITY_SYSTEM_PROMPT
    },
    "support_system_prompt": {
        "description": "System prompt for Support Agent (Resources & Community)",
        "content": SUPPORT_SYSTEM_PROMPT
    },
    "psychological_system_prompt": {
        "description": "System prompt for Psychological Agent (Motivation & Mindset)",
        "content": PSYCHOLOGICAL_SYSTEM_PROMPT
    },
    "goal_extraction_template": {
        "description": "Template for goal extraction prompt (User Request)",
        "content": GOAL_EXTRACTION_TEMPLATE
    },
    "goal_extraction_system": {
        "description": "System role prompt for goal extraction",
        "content": GOAL_EXTRACTION_SYSTEM
    }
}

def seed():
    print("Connecting to database...")
    with Session(engine) as session:
        for key, data in PROMPTS.items():
            print(f"Checking {key}...")
            existing = session.exec(select(SystemPrompt).where(SystemPrompt.key == key)).first()
            if not existing:
                print(f"Creating new prompt: {key}")
                prompt = SystemPrompt(
                    key=key,
                    description=data["description"],
                    content=data["content"]
                )
                session.add(prompt)
            else:
                print(f"Prompt {key} already exists.")
        session.commit()
    print("Seeding complete.")

if __name__ == "__main__":
    seed()
