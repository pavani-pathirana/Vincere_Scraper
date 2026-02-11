"""
Storage module for Vincere scraper.

Handles state persistence (SQLite), file writing (JSON), and checkpoint management.
"""

from .state_manager import StateManager
from .file_writer import FileWriter

__all__ = [
    'StateManager',
    'FileWriter'
]
