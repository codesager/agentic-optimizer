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
        description="List of sectors to exclude from the portfolio"
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


def parse_mandate_node(state: SMAState) -> Dict[str, Dict]:
    """
    Node function for the Mandate Parsing Agent.
    
    Extracts structured constraints from the user mandate using OpenAI
    and updates the structured_constraints field in the state.
    
    Args:
        state: The current SMAState containing user_mandate
        
    Returns:
        Dictionary with structured_constraints to update in state
    """
    # Extract user mandate from state
    user_mandate = state.get("user_mandate", "")
    
    if not user_mandate:
        # Return default constraints if no mandate provided
        default_constraints = InvestmentConstraints().model_dump()
        return {"structured_constraints": default_constraints}
    
    # Initialize OpenAI LLM with structured output
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Create structured output chain
    structured_llm = llm.with_structured_output(InvestmentConstraints)
    
    # System prompt
    system_prompt = "You are an expert Investment Consultant. Extract hard constraints from the user text into a JSON object."
    
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
        
        return {"structured_constraints": constraints_dict}
        
    except Exception as e:
        print(f"Error parsing mandate: {e}")
        # Return default constraints on error
        default_constraints = InvestmentConstraints().model_dump()
        return {"structured_constraints": default_constraints}

