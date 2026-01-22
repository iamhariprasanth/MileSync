"""
Agent Coordinator for MileSync multi-agent system.

Routes requests to appropriate agents and manages multi-agent pipelines.
"""

import logging
from typing import Dict, List, Optional, Type

from app.agents.base_agent import (
    AgentContext,
    AgentResponse,
    AgentType,
    BaseAgent,
)

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """
    Central coordinator that orchestrates all MileSync agents.
    
    Responsibilities:
    - Route requests to appropriate agents based on context
    - Manage multi-agent pipelines for complete goal workflows
    - Handle agent chaining when one agent triggers another
    - Provide unified interface for agent interactions
    """
    
    def __init__(self):
        """Initialize coordinator with all agents."""
        self.agents: Dict[AgentType, BaseAgent] = {}
        self._register_agents()
        logger.info("AgentCoordinator initialized with %d agents", len(self.agents))
    
    def _register_agents(self):
        """Register all available agents."""
        # Import agents here to avoid circular imports
        from app.agents.foundation_agent import FoundationAgent
        from app.agents.planning_agent import PlanningAgent
        from app.agents.execution_agent import ExecutionAgent
        from app.agents.sustainability_agent import SustainabilityAgent
        from app.agents.support_agent import SupportAgent
        from app.agents.psychological_agent import PsychologicalAgent
        
        self.agents[AgentType.FOUNDATION] = FoundationAgent()
        self.agents[AgentType.PLANNING] = PlanningAgent()
        self.agents[AgentType.EXECUTION] = ExecutionAgent()
        self.agents[AgentType.SUSTAINABILITY] = SustainabilityAgent()
        self.agents[AgentType.SUPPORT] = SupportAgent()
        self.agents[AgentType.PSYCHOLOGICAL] = PsychologicalAgent()
    
    def get_agent(self, agent_type: AgentType) -> Optional[BaseAgent]:
        """
        Get a specific agent by type.
        
        Args:
            agent_type: The type of agent to retrieve
            
        Returns:
            The agent instance or None if not found
        """
        return self.agents.get(agent_type)
    
    async def route(self, context: AgentContext) -> AgentResponse:
        """
        Route a request to the appropriate agent based on context.
        
        Routing logic:
        - No goal_id and empty history → Foundation Agent
        - Goal exists but no plan → Planning Agent
        - Daily check-in request → Execution Agent
        - Pattern analysis request → Sustainability Agent
        - Resource request → Support Agent
        - Motivation/emotional context → Psychological Agent
        
        Args:
            context: The agent context with user and goal data
            
        Returns:
            Response from the selected agent
        """
        agent_type = self._determine_agent(context)
        agent = self.agents.get(agent_type)
        
        if not agent:
            logger.error(f"No agent found for type: {agent_type}")
            return AgentResponse(
                agent_type=agent_type,
                success=False,
                message=f"Agent {agent_type.value} not available"
            )
        
        logger.info(f"Routing to {agent_type.value} agent")
        
        try:
            response = await agent.process(context)
            
            # Handle agent chaining if next_agent is specified
            if response.next_agent and response.success:
                logger.info(f"Chaining to {response.next_agent.value} agent")
                next_context = self._prepare_chain_context(context, response)
                chain_response = await self.route(next_context)
                # Merge responses
                response.data["chained_response"] = chain_response.data
            
            return response
            
        except Exception as e:
            logger.error(f"Error in {agent_type.value} agent: {e}")
            return AgentResponse(
                agent_type=agent_type,
                success=False,
                message=f"Agent error: {str(e)}"
            )
    
    def _determine_agent(self, context: AgentContext) -> AgentType:
        """
        Determine which agent should handle the request.
        
        Args:
            context: The current context
            
        Returns:
            The appropriate agent type
        """
        # Check additional_context for explicit agent request
        if context.additional_context:
            requested = context.additional_context.get("agent_type")
            if requested:
                try:
                    return AgentType(requested)
                except ValueError:
                    pass
            
            # Check for specific request types
            request_type = context.additional_context.get("request_type")
            if request_type == "daily_checkin":
                return AgentType.EXECUTION
            elif request_type == "pattern_analysis":
                return AgentType.SUSTAINABILITY
            elif request_type == "resources":
                return AgentType.SUPPORT
            elif request_type == "motivation":
                return AgentType.PSYCHOLOGICAL
        
        # No goal yet - Foundation Agent for intake
        if not context.goal_id and len(context.messages) <= 1:
            return AgentType.FOUNDATION
        
        # Goal exists but checking conversation stage
        if context.goal_id and context.current_goal:
            goal = context.current_goal
            
            # If goal doesn't have SMART breakdown - Planning Agent
            if not goal.get("smart_specific"):
                return AgentType.PLANNING
            
            # Default to Execution for task management
            return AgentType.EXECUTION
        
        # Check message content for routing hints
        if context.messages:
            last_message = context.messages[-1].get("content", "").lower()
            
            # Motivation/emotional keywords → Psychological Agent
            emotional_keywords = [
                "stressed", "anxious", "overwhelmed", "unmotivated",
                "can't do this", "giving up", "frustrated", "tired",
                "burned out", "discouraged", "stuck"
            ]
            if any(kw in last_message for kw in emotional_keywords):
                return AgentType.PSYCHOLOGICAL
            
            # Resource keywords → Support Agent
            resource_keywords = [
                "resources", "tools", "apps", "courses", "books",
                "learn more", "recommendations", "help me find"
            ]
            if any(kw in last_message for kw in resource_keywords):
                return AgentType.SUPPORT
            
            # Habit/pattern keywords → Sustainability Agent
            habit_keywords = [
                "habit", "routine", "pattern", "consistent", "streak",
                "burn out", "sustainable", "long-term"
            ]
            if any(kw in last_message for kw in habit_keywords):
                return AgentType.SUSTAINABILITY
        
        # Default to Foundation for new conversations
        return AgentType.FOUNDATION
    
    def _prepare_chain_context(
        self,
        original_context: AgentContext,
        previous_response: AgentResponse
    ) -> AgentContext:
        """
        Prepare context for chained agent call.
        
        Args:
            original_context: The original context
            previous_response: Response from the previous agent
            
        Returns:
            Updated context for the next agent
        """
        # Create new context with previous agent's output
        return AgentContext(
            user_id=original_context.user_id,
            goal_id=original_context.goal_id,
            session_id=original_context.session_id,
            messages=original_context.messages,
            user_profile=original_context.user_profile,
            current_goal=original_context.current_goal,
            additional_context={
                **(original_context.additional_context or {}),
                "previous_agent": previous_response.agent_type,
                "previous_output": previous_response.data
            }
        )
    
    async def run_intake_pipeline(self, context: AgentContext) -> Dict:
        """
        Run the full goal intake pipeline.
        
        Flow: Foundation → Planning
        
        Args:
            context: Initial context with user message
            
        Returns:
            Combined results from all pipeline agents
        """
        results = {}
        
        # Step 1: Foundation Agent for intake
        foundation_response = await self.agents[AgentType.FOUNDATION].process(context)
        results["foundation"] = foundation_response.data
        
        if not foundation_response.success:
            return results
        
        # Step 2: Planning Agent for SMART conversion
        planning_context = self._prepare_chain_context(context, foundation_response)
        planning_response = await self.agents[AgentType.PLANNING].process(planning_context)
        results["planning"] = planning_response.data
        
        return results
    
    async def run_daily_checkin(self, context: AgentContext) -> Dict:
        """
        Run daily check-in workflow.
        
        Flow: Execution → Sustainability → Psychological (if needed)
        
        Args:
            context: Context with user's daily update
            
        Returns:
            Combined results from check-in workflow
        """
        results = {}
        
        # Step 1: Execution Agent for task status
        execution_response = await self.agents[AgentType.EXECUTION].process(context)
        results["execution"] = execution_response.data
        
        # Step 2: Sustainability Agent for pattern analysis
        sustainability_context = self._prepare_chain_context(context, execution_response)
        sustainability_response = await self.agents[AgentType.SUSTAINABILITY].process(
            sustainability_context
        )
        results["sustainability"] = sustainability_response.data
        
        # Step 3: Psychological Agent if burnout risk detected
        if sustainability_response.data.get("burnout_risk") in ["MEDIUM", "HIGH"]:
            psych_context = self._prepare_chain_context(context, sustainability_response)
            psych_response = await self.agents[AgentType.PSYCHOLOGICAL].process(psych_context)
            results["psychological"] = psych_response.data
        
        return results
    
    def get_agent_info(self) -> List[Dict]:
        """
        Get information about all registered agents.
        
        Returns:
            List of agent information dictionaries
        """
        return [
            {
                "type": agent.agent_type.value,
                "name": agent.agent_name,
                "description": agent.agent_description
            }
            for agent in self.agents.values()
        ]


# Global coordinator instance
_coordinator: Optional[AgentCoordinator] = None


def get_agent_coordinator() -> AgentCoordinator:
    """
    Get the global AgentCoordinator instance.
    
    Returns:
        The singleton AgentCoordinator
    """
    global _coordinator
    if _coordinator is None:
        _coordinator = AgentCoordinator()
    return _coordinator
