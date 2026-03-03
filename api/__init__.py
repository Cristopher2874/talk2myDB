"""Possible router"""

from .agents import router as agent_router
from .manual import router as manual_router

__all__ = [
    'agent_router',
    'manual_router'
]