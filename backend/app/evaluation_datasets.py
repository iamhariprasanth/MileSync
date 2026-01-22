"""Evaluation datasets for MileSync AI coaching experiments.

This module provides sample datasets for running Opik experiments to:
- Test goal coaching quality
- Benchmark goal extraction accuracy
- Measure SMART goal alignment
- Track regression across model versions
"""

# Sample coaching conversations for evaluation
COACHING_EVALUATION_DATASET = [
    {
        "id": "coach-001",
        "input": {
            "user_message": "I want to lose weight this year",
            "context": "New user, first message"
        },
        "expected_output": {
            "asks_clarifying_questions": True,
            "mentions_smart_criteria": True,
            "is_encouraging": True,
            "provides_next_steps": True
        },
        "metadata": {
            "category": "health",
            "difficulty": "medium",
            "expected_score_range": [0.7, 1.0]
        }
    },
    {
        "id": "coach-002",
        "input": {
            "user_message": "I want to become a millionaire",
            "context": "Ambitious but vague goal"
        },
        "expected_output": {
            "asks_clarifying_questions": True,
            "mentions_measurable_steps": True,
            "is_realistic": True,
            "breaks_down_goal": True
        },
        "metadata": {
            "category": "finance",
            "difficulty": "hard",
            "expected_score_range": [0.6, 0.9]
        }
    },
    {
        "id": "coach-003",
        "input": {
            "user_message": "I want to learn Python programming to get a data science job within 6 months",
            "context": "Specific goal with timeline"
        },
        "expected_output": {
            "acknowledges_timeline": True,
            "suggests_milestones": True,
            "is_actionable": True,
            "considers_feasibility": True
        },
        "metadata": {
            "category": "career",
            "difficulty": "easy",
            "expected_score_range": [0.8, 1.0]
        }
    },
    {
        "id": "coach-004",
        "input": {
            "user_message": "I don't know what I want to do with my life",
            "context": "Exploratory, needs guidance"
        },
        "expected_output": {
            "is_empathetic": True,
            "asks_discovery_questions": True,
            "doesnt_assume": True,
            "provides_framework": True
        },
        "metadata": {
            "category": "personal",
            "difficulty": "hard",
            "expected_score_range": [0.6, 0.85]
        }
    },
    {
        "id": "coach-005",
        "input": {
            "user_message": "I want to run a marathon next year. I've never run more than 1 mile.",
            "context": "Ambitious with baseline"
        },
        "expected_output": {
            "acknowledges_starting_point": True,
            "creates_progressive_plan": True,
            "sets_realistic_milestones": True,
            "considers_timeline": True
        },
        "metadata": {
            "category": "health",
            "difficulty": "medium",
            "expected_score_range": [0.75, 0.95]
        }
    }
]

# Sample goal extraction scenarios
GOAL_EXTRACTION_DATASET = [
    {
        "id": "extract-001",
        "input": {
            "conversation": [
                {"role": "user", "content": "I want to learn Spanish"},
                {"role": "assistant", "content": "Great goal! What level would you like to reach and by when?"},
                {"role": "user", "content": "I'd like to be conversational in 6 months for my trip to Spain"},
                {"role": "assistant", "content": "Perfect! Let's create a plan with weekly milestones."}
            ]
        },
        "expected_output": {
            "goal_title_contains": ["Spanish", "conversational"],
            "category": "education",
            "has_target_date": True,
            "milestone_count_range": [3, 7],
            "is_smart": True
        },
        "metadata": {
            "complexity": "medium"
        }
    },
    {
        "id": "extract-002",
        "input": {
            "conversation": [
                {"role": "user", "content": "I need to save $10,000 for an emergency fund"},
                {"role": "assistant", "content": "That's a smart financial goal! What's your timeline?"},
                {"role": "user", "content": "I'd like to do it in 12 months"},
                {"role": "assistant", "content": "So about $833/month. What's your current savings rate?"},
                {"role": "user", "content": "I can probably save $500-600 a month now"},
                {"role": "assistant", "content": "We'll need to find ways to increase savings or extend timeline slightly."}
            ]
        },
        "expected_output": {
            "goal_title_contains": ["save", "emergency", "fund"],
            "category": "finance",
            "has_measurable_target": True,
            "milestones_are_incremental": True
        },
        "metadata": {
            "complexity": "high"
        }
    },
    {
        "id": "extract-003",
        "input": {
            "conversation": [
                {"role": "user", "content": "I want to get promoted to senior engineer this year"},
                {"role": "assistant", "content": "Excellent career goal! What skills do you need to develop?"},
                {"role": "user", "content": "I need to improve my system design and mentoring skills"},
                {"role": "assistant", "content": "Let's break this into specific learning goals and practice opportunities."}
            ]
        },
        "expected_output": {
            "goal_title_contains": ["senior", "engineer", "promotion"],
            "category": "career",
            "has_skill_milestones": True,
            "is_actionable": True
        },
        "metadata": {
            "complexity": "medium"
        }
    }
]

# Frustration detection test cases
FRUSTRATION_DETECTION_DATASET = [
    {
        "id": "frust-001",
        "input": {
            "original_question": "I want to learn programming",
            "ai_response": "What language are you interested in?",
            "user_reply": "Python sounds great!"
        },
        "expected_output": {
            "frustration_level": "low",
            "score_range": [0.0, 0.2]
        }
    },
    {
        "id": "frust-002",
        "input": {
            "original_question": "I want to learn Python",
            "ai_response": "What language are you interested in?",
            "user_reply": "I just said Python..."
        },
        "expected_output": {
            "frustration_level": "medium",
            "score_range": [0.4, 0.7]
        }
    },
    {
        "id": "frust-003",
        "input": {
            "original_question": "I already told you I want to run a marathon",
            "ai_response": "What fitness goals do you have?",
            "user_reply": "ARE YOU EVEN LISTENING? MARATHON. I WANT TO RUN A MARATHON."
        },
        "expected_output": {
            "frustration_level": "high",
            "score_range": [0.8, 1.0]
        }
    }
]

# SMART goal alignment test cases
SMART_ALIGNMENT_DATASET = [
    {
        "id": "smart-001",
        "goal": {
            "title": "Lose weight",
            "description": "I want to lose weight",
            "target_date": None,
            "milestones": []
        },
        "expected_scores": {
            "specific": 0.2,
            "measurable": 0.1,
            "achievable": 0.5,
            "relevant": 0.8,
            "time_bound": 0.0
        },
        "overall_smart_score_range": [0.2, 0.4]
    },
    {
        "id": "smart-002",
        "goal": {
            "title": "Lose 20 pounds in 6 months through diet and exercise",
            "description": "Achieve healthy weight loss of 20 lbs by following a structured diet plan and exercising 4x weekly",
            "target_date": "2025-06-30",
            "milestones": [
                "Lose 5 lbs in month 1",
                "Establish consistent workout routine",
                "Lose 10 lbs by month 3",
                "Reach target weight by month 6"
            ]
        },
        "expected_scores": {
            "specific": 0.9,
            "measurable": 0.95,
            "achievable": 0.85,
            "relevant": 0.9,
            "time_bound": 1.0
        },
        "overall_smart_score_range": [0.85, 1.0]
    },
    {
        "id": "smart-003",
        "goal": {
            "title": "Learn Spanish by summer",
            "description": "Want to speak Spanish for vacation",
            "target_date": "2025-08-01",
            "milestones": ["Learn basics", "Practice speaking"]
        },
        "expected_scores": {
            "specific": 0.5,
            "measurable": 0.3,
            "achievable": 0.7,
            "relevant": 0.9,
            "time_bound": 0.8
        },
        "overall_smart_score_range": [0.5, 0.7]
    }
]


def get_coaching_dataset():
    """Return the coaching evaluation dataset."""
    return COACHING_EVALUATION_DATASET


def get_goal_extraction_dataset():
    """Return the goal extraction dataset."""
    return GOAL_EXTRACTION_DATASET


def get_frustration_dataset():
    """Return the frustration detection dataset."""
    return FRUSTRATION_DETECTION_DATASET


def get_smart_alignment_dataset():
    """Return the SMART alignment dataset."""
    return SMART_ALIGNMENT_DATASET


def get_all_datasets():
    """Return all evaluation datasets."""
    return {
        "coaching": COACHING_EVALUATION_DATASET,
        "goal_extraction": GOAL_EXTRACTION_DATASET,
        "frustration": FRUSTRATION_DETECTION_DATASET,
        "smart_alignment": SMART_ALIGNMENT_DATASET
    }
