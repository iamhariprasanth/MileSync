"""Tests for Opik observability and evaluation integration."""

import pytest
from unittest.mock import patch, MagicMock
import json


class TestOpikConfiguration:
    """Tests for Opik configuration."""
    
    def test_configure_opik_without_api_key(self):
        """Test that Opik configuration returns False without API key."""
        with patch('app.config.settings') as mock_settings:
            mock_settings.OPIK_API_KEY = ""
            
            from app.services.opik_service import configure_opik
            
            # Reset the global state
            import app.services.opik_service as opik_service
            opik_service._opik_configured = False
            
            result = configure_opik()
            assert result == False
    
    def test_is_opik_enabled_returns_false_when_not_configured(self):
        """Test is_opik_enabled returns False when not configured."""
        import app.services.opik_service as opik_service
        opik_service._opik_configured = False
        
        from app.services.opik_service import is_opik_enabled
        assert is_opik_enabled() == False


class TestGoalCoachingQualityMetric:
    """Tests for the GoalCoachingQualityMetric evaluation."""
    
    @patch('app.services.opik_service.OpenAI')
    def test_score_returns_valid_result(self, mock_openai):
        """Test that the coaching quality metric returns a valid score."""
        # Mock the OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "score": 0.85,
            "reason": "Excellent coaching with SMART methodology"
        })
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch('app.config.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            
            from app.services.opik_service import GoalCoachingQualityMetric
            
            metric = GoalCoachingQualityMetric()
            result = metric.score(
                user_input="I want to learn Python programming",
                ai_response="Great goal! Let's make it SMART. What specific aspect of Python interests you most - web development, data science, or general programming? And what timeline are you thinking?"
            )
            
            assert "score" in result
            assert "reason" in result
            assert 0 <= result["score"] <= 1
    
    @patch('app.services.opik_service.OpenAI')
    def test_score_handles_invalid_json_response(self, mock_openai):
        """Test that the metric handles invalid JSON gracefully."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Invalid JSON response"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch('app.config.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            
            from app.services.opik_service import GoalCoachingQualityMetric
            
            metric = GoalCoachingQualityMetric()
            result = metric.score(
                user_input="Test input",
                ai_response="Test response"
            )
            
            # Should return default score on parse error
            assert result["score"] == 0.5
            assert "parse" in result["reason"].lower() or "error" in result["reason"].lower()


class TestGoalExtractionQualityMetric:
    """Tests for the GoalExtractionQualityMetric evaluation."""
    
    @patch('app.services.opik_service.OpenAI')
    def test_score_returns_valid_extraction_result(self, mock_openai):
        """Test that goal extraction quality metric returns valid results."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "score": 0.9,
            "reason": "Well-structured SMART goal with clear milestones",
            "improvements": ["Consider adding more specific deadlines"]
        })
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch('app.config.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            
            from app.services.opik_service import GoalExtractionQualityMetric
            
            metric = GoalExtractionQualityMetric()
            result = metric.score(
                conversation_summary="User wants to learn Python for web development",
                goal_title="Master Python Web Development",
                goal_description="Learn Python and Django to build full-stack web applications",
                goal_category="education",
                milestones_summary="Python Basics, Django Fundamentals, Build Portfolio Project"
            )
            
            assert "score" in result
            assert "reason" in result
            assert "improvements" in result
            assert isinstance(result["improvements"], list)


class TestUserFrustrationDetector:
    """Tests for the UserFrustrationDetector."""
    
    @patch('app.services.opik_service.OpenAI')
    def test_detect_returns_low_frustration_for_engaged_user(self, mock_openai):
        """Test frustration detection for an engaged user."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "score": 0.1,
            "indicators": []
        })
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch('app.config.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            
            from app.services.opik_service import UserFrustrationDetector
            
            detector = UserFrustrationDetector()
            result = detector.detect(
                user_input="I want to learn programming",
                previous_response="Great! What language interests you?",
                current_reply="I'm thinking Python would be good for data science!"
            )
            
            assert "frustration_score" in result
            assert result["frustration_score"] < 0.5  # Low frustration
    
    @patch('app.services.opik_service.OpenAI')
    def test_detect_identifies_high_frustration(self, mock_openai):
        """Test frustration detection for a frustrated user."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "score": 0.8,
            "indicators": ["Repetitive question", "Short dismissive reply"]
        })
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch('app.config.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            
            from app.services.opik_service import UserFrustrationDetector
            
            detector = UserFrustrationDetector()
            result = detector.detect(
                user_input="I already told you I want Python!",
                previous_response="What language would you like to learn?",
                current_reply="I said Python. Can you please just listen?"
            )
            
            assert result["frustration_score"] > 0.5  # High frustration
            assert len(result["indicators"]) > 0


class TestAIServiceTracking:
    """Tests for AI service with Opik tracking."""
    
    def test_opik_imports_available(self):
        """Test that Opik imports are available."""
        from app.services.ai_service import OPIK_AVAILABLE
        # Should be True if opik is installed
        assert isinstance(OPIK_AVAILABLE, bool)
    
    def test_track_decorator_exists(self):
        """Test that track decorator is available."""
        from app.services.ai_service import track
        assert callable(track)
    
    def test_tracked_openai_client_creation(self):
        """Test that tracked OpenAI client can be created."""
        with patch('app.config.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_settings.OPIK_API_KEY = ""  # No Opik
            
            from app.services import ai_service
            ai_service._tracked_client = None  # Reset
            
            from app.services.ai_service import get_openai_client
            client = get_openai_client()
            
            assert client is not None


class TestAnalyticsEndpoints:
    """Tests for analytics API endpoints."""
    
    def test_analytics_status_returns_correct_structure(self):
        """Test that analytics status endpoint returns expected structure."""
        from app.routes.analytics import EvaluationMetrics
        
        # Test the schema validates correctly
        metrics = EvaluationMetrics(
            opik_enabled=False,
            project_name=None,
            workspace=None,
            recent_evaluations=[],
            summary={"message": "Test"}
        )
        
        assert metrics.opik_enabled == False
        assert metrics.summary == {"message": "Test"}
    
    def test_coaching_quality_response_schema(self):
        """Test coaching quality response schema."""
        from app.routes.analytics import CoachingQualityResponse
        
        response = CoachingQualityResponse(
            score=0.85,
            reason="Good coaching response"
        )
        
        assert response.score == 0.85
        assert response.reason == "Good coaching response"
    
    def test_frustration_check_response_schema(self):
        """Test frustration check response schema."""
        from app.routes.analytics import FrustrationCheckResponse
        
        response = FrustrationCheckResponse(
            frustration_score=0.2,
            indicators=[],
            recommendation="User seems engaged. Continue current approach."
        )
        
        assert response.frustration_score == 0.2
        assert response.recommendation.startswith("User seems")
    
    def test_ai_performance_summary_schema(self):
        """Test AI performance summary schema."""
        from app.routes.analytics import AIPerformanceSummary
        
        summary = AIPerformanceSummary(
            total_conversations=100,
            avg_coaching_quality=0.75,
            avg_goal_extraction_quality=0.80,
            avg_frustration_level=0.15,
            total_goals_created=45,
            model_version="gpt-4o-mini",
            evaluation_period="last 30 days"
        )
        
        assert summary.total_conversations == 100
        assert summary.avg_coaching_quality == 0.75
        assert summary.model_version == "gpt-4o-mini"
