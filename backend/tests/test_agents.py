"""
Unit tests for MileSync multi-agent system.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.agents.base_agent import (
    AgentContext,
    AgentResponse,
    AgentType,
    GoalType,
    TaskFrequency,
)
from app.agents.coordinator import AgentCoordinator, get_agent_coordinator
from app.agents.foundation_agent import FoundationAgent
from app.agents.planning_agent import PlanningAgent
from app.agents.execution_agent import ExecutionAgent
from app.agents.sustainability_agent import SustainabilityAgent
from app.agents.support_agent import SupportAgent
from app.agents.psychological_agent import PsychologicalAgent


# Test fixtures

@pytest.fixture
def sample_context():
    """Create a sample agent context."""
    return AgentContext(
        user_id=1,
        goal_id=1,
        session_id=1,
        messages=[
            {"role": "user", "content": "I want to learn Spanish"}
        ],
        user_profile=None,
        current_goal=None,
        task_history=[]
    )


@pytest.fixture
def coordinator():
    """Get agent coordinator instance."""
    return get_agent_coordinator()


# Test Base Agent

class TestAgentContext:
    """Tests for AgentContext model."""
    
    def test_create_context_minimal(self):
        """Test creating context with minimal fields."""
        context = AgentContext(user_id=1)
        assert context.user_id == 1
        assert context.goal_id is None
        assert context.messages == []
    
    def test_create_context_full(self):
        """Test creating context with all fields."""
        context = AgentContext(
            user_id=1,
            goal_id=2,
            session_id=3,
            messages=[{"role": "user", "content": "test"}],
            user_profile={"name": "Test"},
            current_goal={"title": "Test Goal"},
            additional_context={"key": "value"}
        )
        assert context.user_id == 1
        assert context.goal_id == 2
        assert len(context.messages) == 1


class TestAgentResponse:
    """Tests for AgentResponse model."""
    
    def test_create_response(self):
        """Test creating an agent response."""
        response = AgentResponse(
            agent_type=AgentType.FOUNDATION,
            success=True,
            message="Test message",
            data={"key": "value"}
        )
        assert response.agent_type == AgentType.FOUNDATION
        assert response.success is True
        assert response.message == "Test message"
    
    def test_response_with_next_agent(self):
        """Test response with chain to next agent."""
        response = AgentResponse(
            agent_type=AgentType.FOUNDATION,
            next_agent=AgentType.PLANNING
        )
        assert response.next_agent == AgentType.PLANNING


# Test Coordinator

class TestAgentCoordinator:
    """Tests for AgentCoordinator."""
    
    def test_coordinator_has_all_agents(self, coordinator):
        """Test that coordinator has all 6 agents."""
        assert len(coordinator.agents) == 6
        assert AgentType.FOUNDATION in coordinator.agents
        assert AgentType.PLANNING in coordinator.agents
        assert AgentType.EXECUTION in coordinator.agents
        assert AgentType.SUSTAINABILITY in coordinator.agents
        assert AgentType.SUPPORT in coordinator.agents
        assert AgentType.PSYCHOLOGICAL in coordinator.agents
    
    def test_get_agent_info(self, coordinator):
        """Test getting agent info list."""
        info = coordinator.get_agent_info()
        assert len(info) == 6
        assert all("type" in i and "name" in i for i in info)
    
    def test_get_specific_agent(self, coordinator):
        """Test getting a specific agent."""
        agent = coordinator.get_agent(AgentType.FOUNDATION)
        assert agent is not None
        assert agent.agent_type == AgentType.FOUNDATION
    
    def test_determine_foundation_for_new_conversation(self, coordinator):
        """Test routing to Foundation for new conversations."""
        context = AgentContext(
            user_id=1,
            messages=[{"role": "user", "content": "I want to..."}]
        )
        agent_type = coordinator._determine_agent(context)
        assert agent_type == AgentType.FOUNDATION
    
    def test_determine_psychological_for_emotional_content(self, coordinator):
        """Test routing to Psychological for emotional content."""
        context = AgentContext(
            user_id=1,
            goal_id=1,
            messages=[
                {"role": "user", "content": "I'm feeling stressed and overwhelmed"}
            ]
        )
        agent_type = coordinator._determine_agent(context)
        assert agent_type == AgentType.PSYCHOLOGICAL
    
    def test_determine_support_for_resource_request(self, coordinator):
        """Test routing to Support for resource requests."""
        context = AgentContext(
            user_id=1,
            goal_id=1,
            messages=[
                {"role": "user", "content": "Can you recommend some tools and courses?"}
            ]
        )
        agent_type = coordinator._determine_agent(context)
        assert agent_type == AgentType.SUPPORT


# Test Foundation Agent

class TestFoundationAgent:
    """Tests for Foundation Agent."""
    
    @pytest.fixture
    def agent(self):
        return FoundationAgent()
    
    def test_agent_properties(self, agent):
        """Test agent has correct properties."""
        assert agent.agent_type == AgentType.FOUNDATION
        assert agent.agent_name == "Foundation Agent"
        assert len(agent.get_system_prompt()) > 100
    
    def test_should_not_assess_with_few_messages(self, agent):
        """Test assessment not triggered with few messages."""
        context = AgentContext(
            user_id=1,
            messages=[{"role": "user", "content": "Test"}]
        )
        assert agent._should_generate_assessment(context) is False
    
    def test_create_response(self, agent):
        """Test creating a standardized response."""
        response = agent.create_response(
            success=True,
            message="Test",
            data={"key": "value"}
        )
        assert response.agent_type == AgentType.FOUNDATION
        assert response.trace_id is not None


# Test Planning Agent

class TestPlanningAgent:
    """Tests for Planning Agent."""
    
    @pytest.fixture
    def agent(self):
        return PlanningAgent()
    
    def test_agent_properties(self, agent):
        """Test agent has correct properties."""
        assert agent.agent_type == AgentType.PLANNING
        assert "SMART" in agent.get_system_prompt()


# Test Execution Agent

class TestExecutionAgent:
    """Tests for Execution Agent."""
    
    @pytest.fixture
    def agent(self):
        return ExecutionAgent()
    
    def test_agent_properties(self, agent):
        """Test agent has correct properties."""
        assert agent.agent_type == AgentType.EXECUTION
        assert "progress" in agent.agent_description.lower()
    
    def test_calculate_streak_empty(self, agent):
        """Test streak calculation with no history."""
        streak = agent._calculate_streak([])
        assert streak == 0
    
    def test_is_today_with_today_date(self, agent):
        """Test today check with current date."""
        today_iso = datetime.utcnow().isoformat()
        assert agent._is_today(today_iso) is True
    
    def test_is_today_with_old_date(self, agent):
        """Test today check with old date."""
        old_date = "2020-01-01T00:00:00"
        assert agent._is_today(old_date) is False


# Test Sustainability Agent

class TestSustainabilityAgent:
    """Tests for Sustainability Agent."""
    
    @pytest.fixture
    def agent(self):
        return SustainabilityAgent()
    
    def test_agent_properties(self, agent):
        """Test agent has correct properties."""
        assert agent.agent_type == AgentType.SUSTAINABILITY
        assert "habit" in agent.agent_description.lower()
    
    def test_assess_burnout_neutral(self, agent):
        """Test burnout assessment with neutral context."""
        context = AgentContext(user_id=1, messages=[])
        risk, score = agent._assess_burnout(context)
        assert risk in ["LOW", "MEDIUM", "HIGH"]
        assert 0 <= score <= 100
    
    def test_analyze_habits_empty(self, agent):
        """Test habit analysis with no history."""
        analysis = agent._analyze_habits([])
        # Returns empty HabitAnalysis with defaults
        assert analysis.days_consistent == 0
        assert len(analysis.habit_loops) == 0


# Test Support Agent

class TestSupportAgent:
    """Tests for Support Agent."""
    
    @pytest.fixture
    def agent(self):
        return SupportAgent()
    
    def test_agent_properties(self, agent):
        """Test agent has correct properties."""
        assert agent.agent_type == AgentType.SUPPORT
        assert "resource" in agent.agent_description.lower()
    
    def test_fallback_recommendations(self, agent):
        """Test fallback recommendations work."""
        context = AgentContext(user_id=1)
        response = agent._generate_fallback_recommendations(context)
        assert response.success is True
        assert len(response.data.get("recommended_resources", [])) > 0


# Test Psychological Agent

class TestPsychologicalAgent:
    """Tests for Psychological Agent."""
    
    @pytest.fixture
    def agent(self):
        return PsychologicalAgent()
    
    def test_agent_properties(self, agent):
        """Test agent has correct properties."""
        assert agent.agent_type == AgentType.PSYCHOLOGICAL
        assert "motivation" in agent.agent_description.lower()
    
    def test_assess_emotional_state_neutral(self, agent):
        """Test emotional assessment with neutral context."""
        context = AgentContext(user_id=1, messages=[])
        assessment = agent._assess_emotional_state(context)
        assert 1 <= assessment.motivation_level <= 10
        assert 1 <= assessment.stress_level <= 10
    
    def test_assess_emotional_state_stressed(self, agent):
        """Test emotional assessment detects stress."""
        context = AgentContext(
            user_id=1,
            messages=[{"role": "user", "content": "I'm so stressed and anxious"}]
        )
        assessment = agent._assess_emotional_state(context)
        assert assessment.stress_level > 5
    
    def test_create_stress_intervention(self, agent):
        """Test stress intervention creation."""
        intervention = agent._create_stress_intervention()
        assert intervention.type == "STRESS_MANAGEMENT"
        assert len(intervention.exercises) > 0


# Test Agent Enums

class TestAgentEnums:
    """Tests for agent-related enums."""
    
    def test_agent_type_values(self):
        """Test AgentType enum values."""
        assert AgentType.FOUNDATION.value == "foundation"
        assert AgentType.PLANNING.value == "planning"
        assert len(AgentType) == 6
    
    def test_goal_type_values(self):
        """Test GoalType enum values."""
        assert GoalType.SHORT_TERM.value == "short_term"
        assert GoalType.LONG_TERM.value == "long_term"
        assert GoalType.RESOLUTION.value == "resolution"
    
    def test_task_frequency_values(self):
        """Test TaskFrequency enum values."""
        assert TaskFrequency.DAILY.value == "daily"
        assert TaskFrequency.WEEKLY.value == "weekly"
        assert TaskFrequency.ONE_TIME.value == "one_time"


# Integration Tests

class TestAgentIntegration:
    """Integration tests for agent pipelines."""
    
    def test_coordinator_singleton(self, coordinator):
        """Test that coordinator is a singleton."""
        coordinator2 = get_agent_coordinator()
        assert coordinator is coordinator2
