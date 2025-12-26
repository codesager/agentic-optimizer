"""
Shared state definition for the Multi-Agent SMA Customization Engine.

This module defines the TypedDict-based state schema that flows between agents
in the LangGraph workflow. The state contains all necessary information for
agents to collaborate on portfolio analysis, risk assessment, and customization.
"""

from typing import TypedDict, Optional, Annotated, List
import operator
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
    
    screener_criteria: dict
    """Screening criteria for stock selection (e.g., market_cap_min, eps_max)."""
    
    universe: list
    """List of tickers to consider."""
    
    market_data: pd.DataFrame
    """Historical prices fetched from yfinance."""
    
    risk_model: dict
    """Covariance matrix and expected returns."""
    
    generated_python_code: str
    """The cvxpy code written by the Optimizer Agent."""
    
    final_portfolio: dict
    """Tickers and weights."""
    
    optimization_retry_count: int
    """Counter for optimization retries to prevent infinite loops."""
    
    feedback: Annotated[List[str], operator.add]
    """A running log of comments and feedback from all agents."""
