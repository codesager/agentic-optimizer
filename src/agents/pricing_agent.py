"""
Pricing Agent for the Multi-Agent SMA Customization Engine.

This agent uses yfinance to retrieve historical price data for the screened
universe of stocks.
"""

import yfinance as yf
import pandas as pd
from typing import Dict
from src.state import SMAState


def pricing_agent_node(state: SMAState) -> Dict:
    """
    Node function for the Pricing Agent.

    Downloads historical price data using yfinance for the universe of stocks.

    Args:
        state: The current SMAState containing universe

    Returns:
        Dictionary with market_data (DataFrame) to update in state
    """
    try:
        universe = state.get("universe", [])

        if not universe:
            return {
                "market_data": pd.DataFrame(),
                "feedback": ["No universe available for pricing"]
            }

        print(f"📈 Downloading historical prices for {len(universe)} stocks...")
        print(f"Tickers: {universe[:10]}{'...' if len(universe) > 10 else ''}")

        # Download historical data (252 trading days = ~1 year)
        try:
            # yfinance download with error handling
            data = yf.download(
                tickers=universe,
                period="1y",  # 1 year of data
                interval="1d",  # Daily data
                group_by='ticker',
                auto_adjust=True,  # Adjust for splits/dividends
                prepost=False,  # Exclude pre/post market
                threads=True,  # Use multiple threads
                progress=False  # Suppress progress bars
            )

            if data.empty:
                return {
                    "market_data": pd.DataFrame(),
                    "feedback": ["No price data retrieved from yfinance"]
                }

            # Handle single ticker case (yfinance returns different structure)
            if len(universe) == 1:
                ticker = universe[0]
                if 'Close' in data.columns:
                    # Single ticker returns flat DataFrame
                    market_data = pd.DataFrame({
                        ticker: data['Close']
                    })
                else:
                    return {
                        "market_data": pd.DataFrame(),
                        "feedback": [f"No close price data available for {ticker}"]
                    }
            else:
                # Multi-ticker case - extract Close prices
                if isinstance(data.columns, pd.MultiIndex):
                    # Multi-level columns: (ticker, price_type)
                    close_data = {}
                    for ticker in universe:
                        if (ticker, 'Close') in data.columns:
                            close_data[ticker] = data[(ticker, 'Close')]
                        else:
                            print(f"Warning: No close price data for {ticker}")

                    if not close_data:
                        return {
                            "market_data": pd.DataFrame(),
                            "feedback": ["No close price data available for any tickers"]
                        }

                    market_data = pd.DataFrame(close_data)
                else:
                    # Fallback - assume single level columns
                    if 'Close' in data.columns:
                        market_data = data[['Close']].copy()
                        market_data.columns = universe[:len(market_data.columns)]
                    else:
                        return {
                            "market_data": pd.DataFrame(),
                            "feedback": ["Unexpected data structure from yfinance"]
                        }

            # Clean up the data
            market_data = market_data.dropna(axis=1, how='all')  # Remove columns with all NaN
            market_data = market_data.dropna(axis=0, how='all')  # Remove rows with all NaN

            if market_data.empty:
                return {
                    "market_data": pd.DataFrame(),
                    "feedback": ["All price data was NaN after cleaning"]
                }

            # Ensure we have enough data points (at least 100 trading days)
            if len(market_data) < 100:
                print(f"Warning: Only {len(market_data)} trading days of data available")

            # Sort by date
            market_data = market_data.sort_index()

            print(f"✅ Downloaded {len(market_data)} days of price data for {len(market_data.columns)} stocks")
            
            return {
                "market_data": market_data,
                "feedback": [f"Downloaded {len(market_data)} days of price data for {len(market_data.columns)} stocks."]
            }

        except Exception as e:
            error_msg = f"Error downloading price data: {str(e)}"
            print(error_msg)
            return {
                "market_data": pd.DataFrame(),
                "feedback": [error_msg]
            }

    except Exception as e:
        error_msg = f"Error in pricing agent: {str(e)}"
        print(error_msg)
        return {
            "market_data": pd.DataFrame(),
            "feedback": [error_msg]
        }