from langchain.tools import tool
from langchain.agents.middleware import ModelRequest, ModelResponse, AgentMiddleware
from langchain.messages import SystemMessage
from typing import Callable
from core import Skill
from core.prompts.skills.basic_query_struct import BASIC_QUERY_SKILL
from core.prompts.skills.graph_patterns import GRAPH_PATTERNS_SKILL
from core.prompts.skills.filters_and_conditions import FILTERS_AND_CONDITIONS_SKILL
from core.prompts.skills.aggregation_grouping import AGGREGATION_GROUPING_SKILL
from core.prompts.skills.path_finding import PATH_FINDING_SKILL
from core.prompts.skills.functions_operators import FUNCTIONS_OPERATORS_SKILL
from core.prompts.skills.syntax_rules import SYNTAX_RULES_SKILL
from core.prompts.skills.advanced_query_patterns import ADVANCED_QUERY_PATTERNS_SKILL

SKILLS: list[Skill] = [
    BASIC_QUERY_SKILL,
    GRAPH_PATTERNS_SKILL,
    FILTERS_AND_CONDITIONS_SKILL,
    AGGREGATION_GROUPING_SKILL,
    PATH_FINDING_SKILL,
    FUNCTIONS_OPERATORS_SKILL,
    SYNTAX_RULES_SKILL,
    ADVANCED_QUERY_PATTERNS_SKILL,
]

@tool
def load_skill(skill_name: str) -> str:
    """Load the full content of a skill into the agent's context.

    Use this when you need detailed information about how to handle a specific
    type of request. This will provide you with comprehensive instructions,
    policies, and guidelines for the skill area.

    Args:
        skill_name: The name of the skill to load (e.g., "expense_reporting", "travel_booking")
    """
    # Find and return the requested skill
    for skill in SKILLS:
        if skill["name"] == skill_name:
            return f"Loaded skill: {skill_name}\n\n{skill['content']}"

    # Skill not found
    available = ", ".join(s["name"] for s in SKILLS)
    return f"Skill '{skill_name}' not found. Available skills: {available}"

class SkillMiddleware(AgentMiddleware):
    """Middleware that injects skill descriptions into the system prompt."""

    # Register the load_skill tool as a class variable
    tools = [load_skill]

    def __init__(self):
        """Initialize and generate the skills prompt from SKILLS."""
        # Build skills prompt from the SKILLS list
        skills_list = []
        for skill in SKILLS:
            skills_list.append(
                f"- **{skill['name']}**: {skill['description']}"
            )
        self.skills_prompt = "\n".join(skills_list)

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Sync: Inject skill descriptions into system prompt."""
        # Build the skills addendum
        skills_addendum = (
            f"\n\n## Available Skills\n\n{self.skills_prompt}\n\n"
            "Use the load_skill tool when you need detailed information "
            "about handling a specific type of request."
        )

        # Append to system message content blocks
        new_content = list(request.system_message.content_blocks) + [
            {"type": "text", "text": skills_addendum}
        ]
        new_system_message = SystemMessage(content=new_content)
        modified_request = request.override(system_message=new_system_message)
        return handler(modified_request)

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Async: Inject skill descriptions into system prompt."""
        # Build the skills addendum
        skills_addendum = (
            f"\n\n## Available Skills\n\n{self.skills_prompt}\n\n"
            "Use the load_skill tool when you need detailed information "
            "about handling a specific type of request."
        )

        # Append to system message content blocks
        new_content = list(request.system_message.content_blocks) + [
            {"type": "text", "text": skills_addendum}
        ]
        new_system_message = SystemMessage(content=new_content)
        modified_request = request.override(system_message=new_system_message)
        return await handler(modified_request)
