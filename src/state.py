"""
Shared state definition for the Multi-Agent SMA Customization Engine.

This module defines the TypedDict-based state schema that flows between agents
in the LangGraph workflow. The state contains all necessary information for
agents to collaborate on portfolio analysis, risk assessment, and customization.
"""

from typing import TypedDict, Optional
import pandas as pd


class SMAState(TypedDict, total=False):
    """
    State schema for SMA customization workflow.
    
    All fields are optional to allow partial state updates during workflow execution.
    """
    
    user_mandate: str
    """The raw input from the user."""
    
    structured_constraints: dict
    """The parsed JSON constraints (e.g., max_weights, excluded_sectors)."""
    
    universe: list
    """List of tickers to consider."""
    
    market_data: pd.DataFrame
    """Historical prices fetched from FMP."""
    
    risk_model: dict
    """Covariance matrix and expected returns."""
    
    generated_python_code: str
    """The cvxpy code written by the Optimizer Agent."""
    
    final_portfolio: dict
    """Tickers and weights."""
    
    feedback: str
    """Comments from the Reviewer agent if optimization fails."""
