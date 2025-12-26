"""
Finviz Screener Agent for the Multi-Agent SMA Customization Engine.

This agent uses the finvizfinance library to screen stocks based on financial criteria
and filters them according to the structured constraints from the mandate.
"""

from typing import Dict, List
from finvizfinance.screener.overview import Overview
from src.state import SMAState

# Canonical Finviz sectors: 
# Basic Materials, Communication Services, Consumer Cyclical, Consumer Defensive, 
# Energy, Financial, Healthcare, Industrials, Real Estate, Technology, Utilities

SECTOR_MAPPING = {
    # Technology
    "tech": "Technology",
    "technology": "Technology",
    # Healthcare / Pharma
    "pharma": "Healthcare",
    "pharmaceuticals": "Healthcare",
    "health": "Healthcare",
    "healthcare": "Healthcare",
    # Financials
    "finance": "Financial",
    "financials": "Financial",
    "banking": "Financial",
    # Energy
    "energy": "Energy",
    "oil": "Energy",
    # Communication
    "telecom": "Communication Services",
    "communication": "Communication Services",
    # Others
    "materials": "Basic Materials",
    "cyclical": "Consumer Cyclical",
    "defensive": "Consumer Defensive",
    "industrials": "Industrials",
    "real estate": "Real Estate",
    "utilities": "Utilities"
}

def normalize_sectors(sectors: List[str]) -> List[str]:
    """Resolves short forms and ensures sectors match Finviz canonical names."""
    normalized = []
    for s in sectors:
        clean_s = s.lower().strip()
        # Direct mapping check
        if clean_s in SECTOR_MAPPING:
            normalized.append(SECTOR_MAPPING[clean_s])
        else:
            # Fallback: check if the input is a substring of any canonical sector
            canonical_sectors = [
                "Basic Materials", "Communication Services", "Consumer Cyclical",
                "Consumer Defensive", "Energy", "Financial", "Healthcare",
                "Industrials", "Real Estate", "Technology", "Utilities"
            ]
            match = next((cs for cs in canonical_sectors if clean_s in cs.lower()), None)
            normalized.append(match if match else s.title())
    return list(set(normalized))

def finviz_screener_node(state: SMAState) -> Dict:
    """
    Node function for the Finviz Screener Agent.
    """
    try:
        # Get structured constraints for sector filtering
        structured_constraints = state.get("structured_constraints", {})
        excluded_sectors = structured_constraints.get("excluded_sectors", [])
        
        # Get dynamic screening criteria from state (parsed by mandate agent)
        filters = state.get("screener_criteria", {})
        if not filters:
            # Safer defaults for broad search
            filters = {
                'Index': 'S&P 500',
                'Price': 'Over $5',
                'Market Cap.': '+Mid (over $2bln)',
                'Average Volume': 'Over 500K'
            }

        print("🔍 Screening stocks with finvizfinance (Financial view)...")
        print(f"Filters applied: {filters}")

        try:
            # Using Financial class to get Dividend Yield, ROE, etc.
            fobj = Overview()
            fobj.set_filter(filters_dict=filters)
            screen_data = fobj.screener_view()

            if screen_data.empty:
                return {
                    "universe": [],
                    "feedback": ["No stocks found matching screening criteria"]
                }

            print(f"📊 Initial screened universe: {len(screen_data)} stocks")

            # Apply sector filtering if excluded_sectors are specified
            if excluded_sectors:
                excluded_sectors = normalize_sectors(excluded_sectors)
                print(f"🚫 Filtering out excluded sectors: {excluded_sectors}")

                if 'Sector' in screen_data.columns:
                    screen_data = screen_data[~screen_data['Sector'].isin(excluded_sectors)]
                    print(f"✅ After sector filtering: {len(screen_data)} stocks")
                else:
                    print("⚠️  Sector column not available in screener data")

            if screen_data.empty:
                return {
                    "universe": [],
                    "feedback": ["No stocks found matching screening criteria after sector filtering"]
                }

            tickers = screen_data['Ticker'].tolist()

            # Store metadata for risk calculation (e.g. Dividend Yield)
            ticker_metadata = {}
            for _, row in screen_data.iterrows():
                div_str = str(row.get('Dividend', '0%')).replace('%', '')
                try:
                    div_yield = float(div_str) / 100.0 if div_str != '-' else 0.0
                except ValueError:
                    div_yield = 0.0
                ticker_metadata[row['Ticker']] = {
                    "sector": row.get('Sector'),
                    "dividend_yield": div_yield
                }

            # Limit universe size to 100
            if len(tickers) > 100:
                tickers = tickers[:100]
                print(f"⚠️  Limited universe to 100 stocks")

            return {
                "universe": tickers,
                "ticker_metadata": ticker_metadata,
                "feedback": [f"Screened {len(tickers)} stocks using technical filters."]
            }

        except Exception as e:
            error_msg = f"Error during stock screening: {str(e)}"
            return {
                "universe": [],
                "feedback": [error_msg]
            }

    except Exception as e:
        error_msg = f"Error in finviz screener agent: {str(e)}"
        return {
            "universe": [],
            "feedback": [error_msg]
        }