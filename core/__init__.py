"""the core section to provide genai connecitons"""

from .prompts.sql_agent import SQL_SCHEMA_DESCRIPTION, SQL_FEW_SHOT_EXAMPLES
from .prompts.graph_agent import GRAPH_SCHEMA_DESCRIPTION, GRAPH_FEW_SHOT_EXAMPLES
from .gen_ai_provider import GenAIProvider
from .base_agent import BaseAgent

__all__ = [
    'SQL_SCHEMA_DESCRIPTION',
    'SQL_FEW_SHOT_EXAMPLES',
    'GRAPH_SCHEMA_DESCRIPTION',
    'GRAPH_FEW_SHOT_EXAMPLES',
    'GenAIProvider',
    'BaseAgent'
]