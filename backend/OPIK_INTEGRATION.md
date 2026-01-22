# MileSync Opik Integration

This document describes the comprehensive integration of **Opik** for LLM observability and evaluation in MileSync.

## Overview

MileSync uses Opik (by Comet) to provide:
- 🔍 **Complete LLM Tracing** - Track all OpenAI API calls with inputs, outputs, and latencies
- 📊 **LLM-as-Judge Evaluation** - Automatically evaluate AI coaching quality
- 🧪 **Experiment Tracking** - Run and compare experiments across model versions
- 📈 **Performance Dashboards** - Visualize AI performance metrics

## Quick Start

### 1. Get Opik API Key

1. Sign up for free at [comet.com/opik](https://www.comet.com/opik)
2. Create a new project
3. Copy your API key

### 2. Configure Environment

Add to your `.env` file:

```bash
# Opik Configuration
OPIK_API_KEY=H2YXyLMSvgVRpfWWAuIiCWcUq
OPIK_WORKSPACE=hariprasanth-madhavan  # Optional
OPIK_PROJECT_NAME=MileSync-AI-Coach
```

### 3. Restart Backend

```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload
```

You should see:
```
✅ Opik LLM observability enabled
```

## Features

### 1. Automatic LLM Tracing

All OpenAI calls are automatically traced using the `@track` decorator:

```python
from opik import track
from opik.integrations.openai import track_openai

# Wrap OpenAI client
client = track_openai(OpenAI())

# Decorate functions
@track(name="generate_chat_response", tags=["chat"])
async def generate_chat_response(messages):
    ...
```

### 2. Coaching Quality Evaluation

Every chat response is automatically evaluated using LLM-as-judge:

```python
from app.services.opik_service import GoalCoachingQualityMetric

metric = GoalCoachingQualityMetric()
result = metric.score(
    user_input="I want to learn Python",
    ai_response="Great goal! Let's make it SMART..."
)
# Returns: {"score": 0.85, "reason": "Excellent coaching..."}
```

**Evaluation Criteria:**
- SMART Goal Alignment (Specific, Measurable, Achievable, Relevant, Time-bound)
- Motivational Quality
- Actionability
- Clarity

### 3. Goal Extraction Quality

Evaluates how well the AI extracts structured goals from conversations:

```python
from app.services.opik_service import GoalExtractionQualityMetric

metric = GoalExtractionQualityMetric()
result = metric.score(
    conversation_summary="User wants to learn Python...",
    goal_title="Master Python Programming",
    goal_description="Learn Python for data science",
    goal_category="education",
    milestones_summary="Basics, Intermediate, Advanced"
)
```

### 4. User Frustration Detection

Detects when users are frustrated with AI responses:

```python
from app.services.opik_service import UserFrustrationDetector

detector = UserFrustrationDetector()
result = detector.detect(
    user_input="I want Python",
    previous_response="What language interests you?",
    current_reply="I SAID PYTHON!"
)
# Returns: {"frustration_score": 0.8, "indicators": ["Repetition"]}
```

## Analytics Dashboard

### Web UI

Navigate to `/analytics` in the MileSync app to view:
- Total conversations and goals
- Coaching quality scores
- SMART alignment breakdown
- User engagement metrics

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/analytics/status` | Opik connection status |
| `GET /api/analytics/performance` | AI performance summary |
| `GET /api/analytics/metrics/coaching-quality` | Detailed coaching metrics |
| `POST /api/analytics/evaluate/coaching` | Evaluate a single response |
| `POST /api/analytics/evaluate/frustration` | Check user frustration |

## Running Experiments

### Using the Experiment Runner

```bash
cd backend

# Run all experiments
python -m app.run_experiments --all

# Run specific experiment
python -m app.run_experiments --experiment coaching
python -m app.run_experiments --experiment frustration
python -m app.run_experiments --experiment extraction

# Log results to Opik
python -m app.run_experiments --all --log-to-opik
```

### Sample Output

```
🔬 MileSync AI Experiment Runner
==================================================
Model: gpt-4o-mini
Opik: Configured ✅

🎯 Running Coaching Quality Experiment...
[1/5] Testing: coach-001
   ✅ Score: 0.82 (expected: [0.7, 1.0])
...

📊 Coaching Experiment Summary:
   Average Score: 0.81
   Pass Rate: 80.0%
```

## Evaluation Datasets

Located in `app/evaluation_datasets.py`:

### Coaching Dataset
Tests AI responses for coaching quality:
```python
{
    "id": "coach-001",
    "input": {"user_message": "I want to lose weight"},
    "expected_output": {
        "asks_clarifying_questions": True,
        "mentions_smart_criteria": True
    }
}
```

### Goal Extraction Dataset
Tests goal extraction from conversations:
```python
{
    "id": "extract-001",
    "input": {"conversation": [...]},
    "expected_output": {
        "goal_title_contains": ["Spanish"],
        "milestone_count_range": [3, 7]
    }
}
```

### Frustration Dataset
Tests frustration detection accuracy:
```python
{
    "id": "frust-003",
    "expected_output": {
        "frustration_level": "high",
        "score_range": [0.8, 1.0]
    }
}
```

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MileSync Backend                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │ Chat Routes │───▶│   AI Service    │───▶│   OpenAI    │ │
│  └──────┬──────┘    └────────┬────────┘    └─────────────┘ │
│         │                    │                              │
│         │                    │ @track decorator             │
│         │                    ▼                              │
│         │           ┌─────────────────┐                     │
│         │           │ track_openai()  │                     │
│         │           └────────┬────────┘                     │
│         │                    │                              │
│         ▼                    ▼                              │
│  ┌─────────────────────────────────────┐                    │
│  │           Opik Service              │                    │
│  │  • GoalCoachingQualityMetric        │                    │
│  │  • GoalExtractionQualityMetric      │                    │
│  │  • UserFrustrationDetector          │                    │
│  └─────────────────┬───────────────────┘                    │
│                    │                                         │
└────────────────────┼─────────────────────────────────────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │   Opik Dashboard    │
          │   (comet.com/opik)  │
          │                     │
          │ • Traces            │
          │ • Evaluations       │
          │ • Experiments       │
          │ • Metrics           │
          └─────────────────────┘
```

## Best Practices

### 1. Non-Blocking Evaluation
Evaluations are logged asynchronously to avoid slowing down responses:

```python
try:
    if is_opik_enabled():
        log_chat_evaluation(...)
except Exception as e:
    logger.warning(f"Evaluation failed: {e}")
    # Don't fail the request
```

### 2. Graceful Degradation
The app works without Opik configured:

```python
if not settings.OPIK_API_KEY:
    logger.warning("Opik not configured - running without observability")
    return False
```

### 3. Custom Metrics
Create custom metrics for your use case:

```python
class MyCustomMetric:
    PROMPT = "Evaluate the response for..."
    
    def score(self, input, output):
        # Use LLM to evaluate
        result = client.chat.completions.create(...)
        return {"score": float, "reason": str}
```

## Troubleshooting

### Opik Not Connecting

1. Verify API key is correct
2. Check network connectivity to comet.com
3. Look for errors in backend logs

### Evaluations Not Appearing

1. Ensure `OPIK_API_KEY` is set
2. Check the project name matches
3. Wait a few seconds for dashboard sync

### High Latency

If evaluations slow down responses:
1. Evaluations run in background by default
2. Consider batch processing for high traffic
3. Disable real-time evaluation if needed

## Testing

Run the Opik integration tests:

```bash
cd backend
pytest tests/test_opik_integration.py -v
```

## Resources

- [Opik Documentation](https://www.comet.com/docs/opik/)
- [Opik Python SDK](https://pypi.org/project/opik/)
- [LLM-as-Judge Metrics](https://www.comet.com/docs/opik/evaluation/metrics/overview)
- [Comet Dashboard](https://www.comet.com/opik)
