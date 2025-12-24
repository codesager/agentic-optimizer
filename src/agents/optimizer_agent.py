"""
Optimizer Agent for the Multi-Agent SMA Customization Engine.

This agent uses LangChain and OpenAI to generate Python code using cvxpy
for portfolio optimization based on structured constraints and risk model data.
"""

import json
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.state import SMAState

# Load environment variables from .env file
load_dotenv()


def generate_optimizer_code_node(state: SMAState) -> Dict[str, str]:
    """
    Node function for the Optimizer Agent.
    
    Generates Python code using cvxpy for portfolio optimization based on
    structured constraints and risk model data from the state.
    
    Args:
        state: The current SMAState containing structured_constraints and risk_model
        
    Returns:
        Dictionary with generated_python_code to update in state
    """
    # Extract required data from state
    structured_constraints = state.get("structured_constraints", {})
    risk_model = state.get("risk_model", {})
    
    # Validate that required data exists
    if not structured_constraints:
        return {"generated_python_code": "# Error: No structured constraints found in state"}
    
    if not risk_model:
        return {"generated_python_code": "# Error: No risk model found in state"}
    
    # Initialize OpenAI LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # System prompt
    system_prompt = (
        "You are a Quantitative Developer expert in Python and cvxpy. "
        "Write a Python script to optimize a portfolio based on the provided constraints. "
        "- Use `cvxpy` to minimize portfolio variance.\n"
        "- Assume `mu` (expected returns) and `Sigma` (covariance) are available as numpy arrays.\n"
        "- Output ONLY valid Python code string. Do not execute it yet."
    )
    
    # Format constraints for the prompt
    constraints_str = json.dumps(structured_constraints, indent=2)
    
    # Extract risk model metadata (not the full arrays to avoid token limit)
    mu = risk_model.get("mu", [])
    Sigma = risk_model.get("Sigma", [])
    
    # Create summary of risk model instead of full data
    risk_model_summary = {
        "num_assets": len(mu) if mu else 0,
        "mu_shape": f"({len(mu)},)" if mu else "unknown",
        "Sigma_shape": f"({len(Sigma)}, {len(Sigma[0]) if Sigma else 0})" if Sigma else "unknown",
        "mu_summary": {
            "min": min(mu) if mu else 0,
            "max": max(mu) if mu else 0,
            "mean": sum(mu) / len(mu) if mu else 0
        } if mu else {}
    }
    
    risk_model_info = json.dumps(risk_model_summary, indent=2)
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Generate Python code for portfolio optimization using cvxpy.

Constraints:
{constraints}

Risk Model Metadata:
{risk_model}

IMPORTANT: The actual mu (expected returns) and Sigma (covariance matrix) numpy arrays 
are already available in the execution environment. Do NOT include them in your code.
Just reference them as 'mu' and 'Sigma' in your cvxpy optimization code.

Requirements:
1. Minimize portfolio variance using cvxpy
2. Apply constraints from the structured_constraints:
   - max_position_weight: maximum weight for any single position (0.0 to 1.0)
   - min_dividend_yield: minimum dividend yield (if applicable)
   - target_risk: risk level ('low', 'medium', 'high')
3. Use mu (expected returns) and Sigma (covariance matrix) - they are already defined as numpy arrays
4. Return portfolio weights as a numpy array named 'weights'
5. Output ONLY the Python code, no explanations or markdown formatting

Generate the code:""")
    ])
    
    # Create chain
    chain = prompt | llm
    
    try:
        # Invoke the chain to get generated code
        response = chain.invoke({
            "constraints": constraints_str,
            "risk_model": risk_model_info
        })
        
        # Extract code from response (handle both AIMessage and string responses)
        code = response.content if hasattr(response, 'content') else str(response)
        
        # Clean up the code - remove markdown code blocks if present
        code = code.strip()
        if code.startswith("```python"):
            code = code[9:]  # Remove ```python
        elif code.startswith("```"):
            code = code[3:]  # Remove ```
        if code.endswith("```"):
            code = code[:-3]  # Remove closing ```
        code = code.strip()
        
        return {"generated_python_code": code}
        
    except Exception as e:
        error_msg = f"# Error generating optimizer code: {e}"
        print(f"Error in optimizer agent: {e}")
        return {"generated_python_code": error_msg}

