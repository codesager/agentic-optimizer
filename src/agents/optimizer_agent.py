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


def generate_optimizer_code_node(state: SMAState) -> Dict:
    """
    Node function for the Optimizer Agent.
    
    Generates Python code using cvxpy for portfolio optimization based on
    structured constraints and risk model data from the state.
    """
    # Extract required data from state
    structured_constraints = state.get("structured_constraints", {})
    risk_model = state.get("risk_model", {})
    retry_count = state.get("optimization_retry_count", 0)
    
    # Check if we should even proceed
    if not structured_constraints or not risk_model:
        error_msg = "# Error: Missing " + ("constraints" if not structured_constraints else "risk model")
        return {
            "generated_python_code": error_msg,
            "optimization_retry_count": retry_count + 1
        }
    
    print(f"🤖 Optimizer Agent: Generating code (Attempt {retry_count + 1})...")

    # Initialize OpenAI LLM - Upgrade to gpt-4o
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # System prompt
    system_prompt = (
        "You are a Senior Quantitative Developer expert in Python, Numerical Optimization, and cvxpy. "
        "Your task is to write high-quality, DCP-compliant Python code for portfolio optimization. "
        "The environment already has 'mu' (expected returns) and 'Sigma' (covariance) pre-loaded as numpy arrays."
    )
    
    # Format metadata
    mu = risk_model.get("mu", [])
    Sigma = risk_model.get("Sigma", [])
    risk_model_info = json.dumps({
        "num_assets": len(mu),
        "mu_shape": f"({len(mu)},)",
        "Sigma_shape": f"({len(Sigma)}, {len(Sigma[0]) if Sigma else 0})"
    }, indent=2)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Generate Python code for portfolio optimization using cvxpy.

Available variables:
1. `mu`: Annualized expected returns.
2. `Sigma`: Annualized covariance matrix.
3. `n`: Number of assets.

User Constraints: {constraints}
Metadata: {risk_model}

Implementation Requirements:
1. Objective: Minimize `cp.quad_form(weights, Sigma)`.
2. Constraints: sum(weights)==1, weights >= 0, weights <= max_position_weight (if provided).
3. Handle risk levels (low/medium/high).
4. Return results in `weights`.
5. Assign the cvxpy problem instance to a variable named `problem` for validation.
6. Output ONLY Python code.""")
    ])
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "constraints": json.dumps(structured_constraints),
            "risk_model": risk_model_info
        })
        
        code = response.content if hasattr(response, 'content') else str(response)
        code = code.strip()
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]
        
        return {
            "generated_python_code": code.strip(),
            "optimization_retry_count": retry_count + 1
        }
    except Exception as e:
        return {
            "generated_python_code": f"# Error: {str(e)}",
            "optimization_retry_count": retry_count + 1
        }
