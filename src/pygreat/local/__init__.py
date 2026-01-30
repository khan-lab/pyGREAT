"""Local GREAT analysis module.

This module implements the GREAT algorithm locally, allowing analysis
with any organism and custom gene sets without requiring the Stanford server.
"""

from pygreat.local.great import LocalGreat

__all__ = ["LocalGreat"]
