"""agents init"""

# the functions are to create the instance
from .nl2graph_agent import create_nl2graph_agent
from .nl2sql_agent import create_nl2sql_agent

__all__ = [
    'create_nl2graph_agent',
    'create_nl2sql_agent'
]