"""the core section to provide genai connecitons"""

from .prompts.sql_agent import SQL_AGENT_INSTRUCTIONS
from .gen_ai_provider import GenAIProvider

__all__ = [
    'SQL_AGENT_INSTRUCTIONS',
    'GenAIProvider',
    
]