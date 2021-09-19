"""
`neologism`
===========

This module implements dynamically modifiable context-free grammar.

Available Classes
-----------------

DCFG
    The main context-free grammar class.
Rule
    A class to represent a grammar rule in a DCFG.
"""

from .dcfg import DCFG
from .rule import Rule

__all__ = [
    "DCFG",
    "Rule",
]
