"""
Entry point for the Multi-Agent SMA Customization Engine.

This module initializes and runs the LangGraph workflow for managing
Separately Managed Account (SMA) customization processes. It orchestrates
multiple agents that work together to analyze, optimize, and customize
investment portfolios based on client requirements and market data.
"""

import json
import sys
from pathlib import Path

# Add project root to Python path to allow imports when running from src/
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.graph import app
from src.state import SMAState


def print_portfolio_results(state: SMAState) -> None:
    """
    Print the final portfolio weights and approval/rejection status.
    
    Args:
        state: The final SMAState after workflow execution
    """
    print("\n" + "="*80)
    print("PORTFOLIO OPTIMIZATION RESULTS")
    print("="*80)
    
    # Print final portfolio weights
    final_portfolio = state.get("final_portfolio", {})
    if final_portfolio:
        print("\n📊 FINAL PORTFOLIO WEIGHTS:")
        print("-" * 80)
        
        # Sort by weight (descending)
        sorted_portfolio = sorted(
            final_portfolio.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        total_weight = 0.0
        for ticker, weight in sorted_portfolio:
            percentage = weight * 100
            total_weight += weight
            print(f"  {ticker:10s}: {percentage:6.2f}%")
        
        print("-" * 80)
        print(f"  {'Total':10s}: {total_weight * 100:6.2f}%")
        print()
    else:
        print("\n⚠️  No portfolio generated.")
    
    # Print approval/rejection status
    feedback = state.get("feedback", "")
    if feedback:
        print("📝 REVIEWER FEEDBACK:")
        print("-" * 80)
        
        # Check if approved
        if "approved" in feedback.lower():
            print("✅ STATUS: APPROVED")
        else:
            print("❌ STATUS: NOT APPROVED")
        
        print(f"\n{feedback}")
        print("-" * 80)
    
    # Print any errors or warnings
    if not final_portfolio and not feedback:
        print("\n⚠️  Workflow completed but no portfolio or feedback was generated.")
    
    print("\n" + "="*80)


def main():
    """
    Main CLI interface for the SMA Customization Engine.
    """
    print("="*80)
    print("Multi-Agent SMA Customization Engine")
    print("="*80)
    print("\nEnter your investment mandate (e.g., 'I want a low vol portfolio without Tech stocks'):")
    print("(Press Enter on an empty line to exit)\n")
    
    # Get user input
    user_mandate = input("> ").strip()
    
    if not user_mandate:
        print("\nExiting. No mandate provided.")
        return
    
    print(f"\n🔄 Processing mandate: '{user_mandate}'")
    print("⏳ This may take a few moments...\n")
    
    try:
        # Initialize SMAState
        initial_state: SMAState = {
            "user_mandate": user_mandate
        }
        
        # Invoke the LangGraph app
        final_state = app.invoke(initial_state)
        
        # Print results
        print_portfolio_results(final_state)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during workflow execution: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
