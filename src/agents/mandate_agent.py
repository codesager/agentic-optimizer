"""
Mandate Parsing Agent for the Multi-Agent SMA Customization Engine.

This agent uses LangChain and OpenAI to parse user mandates and extract
structured investment constraints from natural language input.
"""

from typing import Dict, List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.state import SMAState

# Load environment variables from .env file
load_dotenv()


class InvestmentConstraints(BaseModel):
    """Pydantic model for structured investment constraints."""
    
    excluded_sectors: List[str] = Field(
        default_factory=list,
        description=(
            "List of sectors to exclude. Map short forms like 'tech' to 'Technology' "
            "and 'pharma' to 'Healthcare'. Valid sectors: Technology, Healthcare, "
            "Financial, Energy, Basic Materials, Consumer Cyclical, Consumer Defensive, "
            "Industrials, Real Estate, Utilities, Communication Services."
        )
    )
    
    max_position_weight: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Maximum weight for any single position (0.0 to 1.0)"
    )
    
    min_dividend_yield: float = Field(
        default=0.0,
        ge=0.0,
        description="Minimum dividend yield requirement (as decimal, e.g., 0.03 for 3%)"
    )
    
    target_risk: str = Field(
        default="medium",
        description="Target risk level: 'low', 'medium', or 'high'"
    )

    screener_criteria: Dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Technical filters for the stock screener. "
            "Include 'Market Cap.' (e.g. '+Mid (over $2bln)'), "
            "'P/E' (e.g. 'Under 15'), or 'Index' (e.g. 'S&P 500'). "
            "If user wants 'Growth', suggest positive EPS growth. "
            "If 'Value', suggest low P/E. If 'Low Vol', suggest Beta < 1."
        )
    )


def parse_mandate_node(state: SMAState) -> Dict:
    """
    Node function for the Mandate Agent.
    
    Extracts structured constraints from the user mandate using OpenAI
    and updates the structured_constraints field in the state.
    """
    # Extract user mandate from state
    user_mandate = state.get("user_mandate", "")
    
    if not user_mandate:
        # Return default constraints if no mandate provided
        default_constraints = InvestmentConstraints().model_dump()
        return {
            "structured_constraints": default_constraints,
            "feedback": ["No mandate provided, using default constraints."]
        }
    
    # Initialize OpenAI LLM with structured output - Upgrade to gpt-4o
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # Create structured output chain - Use method="function_calling" to avoid strict schema validation errors
    structured_llm = llm.with_structured_output(InvestmentConstraints, method="function_calling")
    
    # System prompt
    system_prompt = (
        "You are an expert Investment Consultant. Carefully extract all investment constraints "
        "and technical screening criteria from the user's natural language mandate. "
        "PAY SPECIAL ATTENTION to sector exclusions (e.g., 'avoid utilities', 'no tech'). "
        "Map these to the canonical sector names: Technology, Healthcare, Financial, Energy, "
        "Basic Materials, Consumer Cyclical, Consumer Defensive, Industrials, Real Estate, "
        "Utilities, Communication Services."
    )
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Extract investment constraints from the following user mandate:\n\n{user_mandate}")
    ])
    
    # Create chain
    chain = prompt | structured_llm
    
    try:
        # Invoke the chain to get structured constraints
        constraints = chain.invoke({"user_mandate": user_mandate})
        
        # Convert Pydantic model to dictionary
        constraints_dict = constraints.model_dump()
        
        # Extract screener_criteria to separate field
        screener_criteria = constraints_dict.pop("screener_criteria", {})
        
        return {
            "structured_constraints": constraints_dict,
            "screener_criteria": screener_criteria,
            "optimization_retry_count": 0,
            "feedback": ["Successfully parsed mandate and extracted investment constraints."]
        }
        
    except Exception as e:
        print(f"Error parsing mandate: {e}")
        # Return default constraints on error
        default_constraints = InvestmentConstraints().model_dump()
        return {
            "structured_constraints": default_constraints,
            "feedback": [f"Error parsing mandate logic: {str(e)}"]
        }

