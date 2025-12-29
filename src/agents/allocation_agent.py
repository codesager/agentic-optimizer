"""
Allocation Agent for the Multi-Agent SMA Customization Engine.

This agent runs after the portfolio has been reviewed. It interacts with the user
to determine the investment amount and calculates the precise number of shares
to purchase based on the optimized weights and current market prices.
"""

import pandas as pd
import json
import csv
from typing import Dict
from src.state import SMAState


def allocation_agent_node(state: SMAState) -> Dict:
    """
    Node function for the Allocation Agent.
    
    Prompts the user for a total investment value and calculates the 
    asset allocation (shares/units) for the approved portfolio.
    
    Args:
        state: The current SMAState containing final_portfolio and market_data
    
    Returns:
        Dictionary with allocation_results, portfolio_value, and feedback
    """
    final_portfolio = state.get("final_portfolio", {})
    market_data = state.get("market_data")
    
    # 1. Validation checks
    if not final_portfolio:
        msg = "Skipping Allocation Agent: No final portfolio available."
        print(f"\n⚠️ {msg}")
        return {"feedback": [msg]}
        
    if market_data is None or market_data.empty:
        msg = "Skipping Allocation Agent: No market data available for pricing."
        print(f"\n⚠️ {msg}")
        return {"feedback": [msg]}
    
    print("\n" + "="*80)
    print("💰 ALLOCATION AGENT")
    print("="*80)
    
    # 2. User Interaction
    print("\nThe portfolio has been generated and reviewed.")
    print("Please enter the total Portfolio Value you intend to allocate (e.g., 1000000):")
    
    while True:
        try:
            user_input = input("Total Value ($): ").strip().replace(",", "").replace("$", "")
            if not user_input:
                print("Skipping allocation calculation.")
                return {"feedback": ["User skipped allocation step."]}
                
            portfolio_value = float(user_input)
            if portfolio_value <= 0:
                print("Value must be positive. Please try again.")
                continue
            break
        except ValueError:
            print("Invalid number. Please enter a numeric value (e.g. 100000).")
            
    print(f"\n🔄 Calculating allocation for ${portfolio_value:,.2f}...\n")
    
    # 3. Calculation
    allocation_results = []
    
    # Get latest prices (last row of the dataframe)
    # market_data columns should be tickers
    latest_prices = market_data.iloc[-1]
    last_date = market_data.index[-1].strftime('%Y-%m-%d')
    print(f"Using latest market prices from: {last_date}")
    
    total_calculated_value = 0.0
    
    # Calculate shares for each ticker
    for ticker, weight in final_portfolio.items():
        if ticker not in latest_prices:
            print(f"⚠️ Warning: No price found for {ticker} in market data. Skipping.")
            continue
            
        price = latest_prices[ticker]
        if pd.isna(price) or price <= 0:
            print(f"⚠️ Warning: Invalid price for {ticker} (${price}). Skipping.")
            continue
            
        # Target value for this stock
        target_value = portfolio_value * weight
        
        # Calculate units (allowing fractional shares for precision, 
        # but one could floor() this for whole shares if required)
        units = target_value / price
        
        allocation_results.append({
            "Ticker": ticker,
            "Target Weight": weight,
            "Price": price,
            "Units": units,
            "Allocated Value": target_value
        })
        
        total_calculated_value += target_value

    if not allocation_results:
        return {"feedback": ["Allocation failed: No valid prices found for portfolio assets."]}

    # Sort by weight descending
    allocation_results.sort(key=lambda x: x["Target Weight"], reverse=True)
    
    # 4. Output & Saving
    
    # Print table
    print(f"{'Ticker':<10} {'Weight':<10} {'Price ($)':<12} {'Units':<15} {'Value ($)':<15}")
    print("-" * 70)
    
    for item in allocation_results:
        print(f"{item['Ticker']:<10} {item['Target Weight']:.2%}    {item['Price']:<12.2f} {item['Units']:<15.4f} {item['Allocated Value']:<15.2f}")
        
    print("-" * 70)
    print(f"{'TOTAL':<10} {sum(item['Target Weight'] for item in allocation_results):.2%}    {'':<12} {'':<15} {total_calculated_value:<15.2f}")
    
    # Save to CSV
    filename = "portfolio_allocation.csv"
    try:
        keys = allocation_results[0].keys()
        with open(filename, 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(allocation_results)
        print(f"\n💾 Detailed allocation saved to: {filename}")
        
        # Also save a simple JSON summary
        with open("portfolio_allocation.json", "w") as f:
            json.dump({
                "meta": {
                    "portfolio_value": portfolio_value,
                    "date": last_date
                },
                "allocations": allocation_results
            }, f, indent=2)
            
    except Exception as e:
        print(f"⚠️ Error saving allocation files: {e}")

    return {
        "portfolio_value": portfolio_value,
        "allocation_results": allocation_results,
        "feedback": [f"Allocation calculated for ${portfolio_value:,.2f}. Saved to {filename}."]
    }
