"""AI service for OpenAI chat completions and goal extraction."""

import json
from typing import List, Optional

from openai import OpenAI

from app.config import settings
from app.schemas.goal import AIGoalGeneration, AIMilestoneGeneration, AITaskGeneration

# Default model for all AI conversations
AI_MODEL = "gpt-4o-mini"

# System prompt for the AI goal coach
SYSTEM_PROMPT = """You are an AI goal coach for MileSync. Your role is to help users define SMART goals
(Specific, Measurable, Achievable, Relevant, Time-bound), understand their motivations,
identify potential obstacles, and create actionable plans.

Guidelines:
1. Ask clarifying questions to deeply understand the user's goal before suggesting a roadmap
2. Help break down large goals into manageable milestones
3. Be encouraging but realistic about timelines and effort required
4. Identify potential obstacles and suggest strategies to overcome them
5. When the conversation feels complete, summarize the goal and key milestones

Keep responses concise but helpful. Use a friendly, supportive tone."""


def get_openai_client() -> Optional[OpenAI]:
    """
    Get OpenAI client instance.

    Returns:
        OpenAI client if API key is configured, None otherwise
    """
    if not settings.OPENAI_API_KEY:
        return None
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def format_messages_for_openai(
    messages: List[dict],
    include_system: bool = True
) -> List[dict]:
    """
    Format chat messages for OpenAI API.

    Args:
        messages: List of message dicts with 'role' and 'content'
        include_system: Whether to include system prompt

    Returns:
        Formatted messages list for OpenAI
    """
    formatted = []

    if include_system:
        formatted.append({
            "role": "system",
            "content": SYSTEM_PROMPT
        })

    for msg in messages:
        formatted.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    return formatted


async def generate_chat_response(
    messages: List[dict],
    model: str = AI_MODEL
) -> str:
    """
    Generate AI response for chat messages.

    Args:
        messages: List of message dicts with 'role' and 'content'
        model: OpenAI model to use (default: gpt-4o-mini for cost efficiency)

    Returns:
        AI-generated response text

    Raises:
        ValueError: If OpenAI API key is not configured
        Exception: If OpenAI API call fails
    """
    client = get_openai_client()

    if not client:
        raise ValueError("OpenAI API key not configured")

    formatted_messages = format_messages_for_openai(messages)

    response = client.chat.completions.create(
        model=model,
        messages=formatted_messages,
        max_tokens=1000,
        temperature=0.7,
    )

    return response.choices[0].message.content or ""


def generate_initial_message() -> str:
    """
    Generate the initial greeting message for a new chat session.

    Returns:
        Welcome message string
    """
    return (
        "Hi! I'm your AI goal coach. Tell me about a goal you'd like to achieve. "
        "It could be a New Year resolution, a short-term target, or a long-term dream. "
        "What's on your mind?"
    )


async def summarize_conversation(messages: List[dict]) -> str:
    """
    Generate a summary/title for a conversation.

    Args:
        messages: List of message dicts

    Returns:
        Short summary suitable for session title
    """
    client = get_openai_client()

    if not client:
        # Reason: Fallback when OpenAI not configured
        return "Goal Discussion"

    # Build context from messages
    context = "\n".join([f"{m['role']}: {m['content'][:200]}" for m in messages[:5]])

    response = client.chat.completions.create(
        model=AI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Summarize this goal coaching conversation in 5 words or less. Just return the title, nothing else."
            },
            {
                "role": "user",
                "content": context
            }
        ],
        max_tokens=20,
        temperature=0.3,
    )

    return response.choices[0].message.content or "Goal Discussion"


# OpenAI tool/function definition for goal extraction
GOAL_EXTRACTION_TOOL = {
    "type": "function",
    "function": {
        "name": "create_goal_roadmap",
        "description": "Extract a structured goal with milestones and tasks from the conversation",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "A concise, action-oriented title for the goal (e.g., 'Learn Spanish to conversational level')"
                },
                "description": {
                    "type": "string",
                    "description": "A 1-2 sentence description of the goal and why it matters"
                },
                "category": {
                    "type": "string",
                    "enum": ["health", "career", "education", "finance", "personal", "other"],
                    "description": "The category that best fits this goal"
                },
                "target_date": {
                    "type": "string",
                    "description": "Target completion date in YYYY-MM-DD format"
                },
                "milestones": {
                    "type": "array",
                    "description": "3-7 major checkpoints to achieve the goal",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Milestone title"
                            },
                            "description": {
                                "type": "string",
                                "description": "Brief description of what this milestone involves"
                            },
                            "target_date": {
                                "type": "string",
                                "description": "Target date for this milestone in YYYY-MM-DD format"
                            },
                            "tasks": {
                                "type": "array",
                                "description": "2-5 specific, actionable tasks for this milestone",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {
                                            "type": "string",
                                            "description": "Task title - should be specific and actionable"
                                        },
                                        "description": {
                                            "type": "string",
                                            "description": "Optional details about the task"
                                        },
                                        "priority": {
                                            "type": "string",
                                            "enum": ["low", "medium", "high"],
                                            "description": "Task priority level"
                                        }
                                    },
                                    "required": ["title"]
                                }
                            }
                        },
                        "required": ["title", "tasks"]
                    }
                }
            },
            "required": ["title", "description", "category", "milestones"]
        }
    }
}


async def extract_goal_from_conversation(messages: List[dict]) -> Optional[AIGoalGeneration]:
    """
    Extract structured goal data from a conversation using OpenAI function calling.

    Args:
        messages: List of message dicts from the conversation

    Returns:
        AIGoalGeneration with extracted goal structure, or None if extraction fails
    """
    client = get_openai_client()

    if not client:
        return None

    # Build conversation context
    conversation = "\n".join([
        f"{m['role'].upper()}: {m['content']}"
        for m in messages
    ])

    extraction_prompt = f"""Based on the following goal coaching conversation, extract a structured goal with milestones and tasks.

The goal should be SMART (Specific, Measurable, Achievable, Relevant, Time-bound).
Create 3-7 milestones that logically progress toward the goal.
Each milestone should have 2-5 specific, actionable tasks.

Conversation:
{conversation}

Extract the goal structure using the provided function."""

    response = client.chat.completions.create(
        model=AI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a goal extraction assistant. Analyze conversations and extract structured goals."
            },
            {
                "role": "user",
                "content": extraction_prompt
            }
        ],
        tools=[GOAL_EXTRACTION_TOOL],
        tool_choice={"type": "function", "function": {"name": "create_goal_roadmap"}},
        max_tokens=2000,
        temperature=0.3,
    )

    # Extract the function call arguments
    message = response.choices[0].message
    if not message.tool_calls:
        return None

    tool_call = message.tool_calls[0]
    if tool_call.function.name != "create_goal_roadmap":
        return None

    try:
        goal_data = json.loads(tool_call.function.arguments)

        # Parse milestones
        milestones = []
        for m in goal_data.get("milestones", []):
            tasks = [
                AITaskGeneration(
                    title=t.get("title", ""),
                    description=t.get("description"),
                    priority=t.get("priority", "medium"),
                )
                for t in m.get("tasks", [])
            ]
            milestones.append(AIMilestoneGeneration(
                title=m.get("title", ""),
                description=m.get("description"),
                target_date=m.get("target_date"),
                tasks=tasks,
            ))

        return AIGoalGeneration(
            title=goal_data.get("title", "My Goal"),
            description=goal_data.get("description"),
            category=goal_data.get("category", "other"),
            target_date=goal_data.get("target_date"),
            milestones=milestones,
        )

    except (json.JSONDecodeError, KeyError) as e:
        # Reason: Fallback if parsing fails
        return None
