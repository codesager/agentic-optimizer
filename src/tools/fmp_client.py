"""
Financial Modeling Prep (FMP) API Client Wrapper.

This module provides a wrapper class for interacting with the Financial Modeling Prep API.
It handles API requests, authentication, rate limiting, and data retrieval for market data,
company profiles, financial statements, and other financial information needed for SMA customization.
"""

import os
import requests
import pandas as pd
from typing import List, Dict, Optional, Tuple
from requests.exceptions import HTTPError, RequestException, Timeout


class FMPClient:
    """Client for interacting with the Financial Modeling Prep API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the FMP API client.
        
        Args:
            api_key: FMP API key. If not provided, will attempt to load from environment.
            
        Raises:
            ValueError: If API key is not provided and not found in environment.
        """
        self.api_key = api_key or os.getenv("FMP_API_KEY")
        if not self.api_key:
            raise ValueError("FMP_API_KEY environment variable not set. Please set it in your .env file or environment.")
        
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Make a request to the FMP API with error handling.
        
        Args:
            endpoint: API endpoint path (without base URL)
            params: Optional query parameters
            
        Returns:
            Tuple of (JSON response as dictionary, error_message)
            Returns (None, error_message) if request fails
            Returns (data, None) if request succeeds
        """
        url = f"{self.base_url}/{endpoint}"
        request_params = {"apikey": self.api_key}
        if params:
            request_params.update(params)
        
        try:
            response = self.session.get(url, params=request_params, timeout=30)
            response.raise_for_status()
            return response.json(), None
        except HTTPError as e:
            error_msg = f"HTTP {response.status_code} error for {endpoint}: {e}"
            try:
                error_body = response.text
                error_msg += f"\nResponse body: {error_body}"
            except:
                pass
            return None, error_msg
        except Timeout:
            return None, f"Request timeout for {endpoint}"
        except RequestException as e:
            return None, f"Request error for {endpoint}: {e}"
        except Exception as e:
            return None, f"Unexpected error for {endpoint}: {e}"
    
    def get_sp500_universe(self) -> List[Dict]:
        """
        Fetch the S&P 500 universe from the FMP API.
        
        Returns:
            List of dictionaries containing S&P 500 company data with fields like:
            symbol, name, sector, industry, etc.
            
        Raises:
            RuntimeError: If API request fails and no data is returned.
        """
        endpoint = "sp500_constituent"
        data, error = self._make_request(endpoint)
        
        if data is None:
            error_msg = f"Failed to fetch S&P 500 universe from FMP API"
            if error:
                error_msg += f": {error}"
            raise RuntimeError(error_msg)
        
        if not isinstance(data, list):
            raise RuntimeError(f"Unexpected response format from S&P 500 endpoint: {type(data)}")
        
        return data
    
    def get_historical_prices(self, tickers: List[str], days: int = 252) -> pd.DataFrame:
        """
        Batch fetch historical close prices for the last N trading days.
        
        Uses batch endpoint when possible, with rate limiting to avoid API limits.
        
        Args:
            tickers: List of stock tickers to fetch data for
            days: Number of trading days to fetch (default: 252, approximately 1 year)
            
        Returns:
            pandas DataFrame with dates as index and tickers as columns.
            Each column contains the closing price for that ticker.
            
        Note:
            This method attempts to fetch data for all tickers. If some fail,
            they will be excluded from the result DataFrame.
        """
        if not tickers:
            return pd.DataFrame()
        
        import time
        
        all_data = {}
        failed_tickers = []
        error_details = {}  # Store error details for each failed ticker
        
        # Try batch endpoint first - FMP supports comma-separated tickers
        # Batch size limited to avoid URL length issues (typically 5-10 tickers per batch)
        batch_size = 5
        ticker_batches = [tickers[i:i + batch_size] for i in range(0, len(tickers), batch_size)]
        
        for batch in ticker_batches:
            try:
                # Try batch endpoint with comma-separated tickers
                ticker_list = ",".join(batch)
                endpoint = f"historical-price-full/{ticker_list}"
                params = {"timeseries": days}
                
                data, error = self._make_request(endpoint, params)
                
                if data is None:
                    # If batch fails, fall back to individual requests for this batch
                    batch_error = error or "Unknown error"
                    print(f"Batch request failed for {ticker_list}: {batch_error}")
                    print(f"Falling back to individual requests for this batch...")
                    for ticker in batch:
                        time.sleep(0.1)  # Small delay to avoid rate limits
                        endpoint = f"historical-price-full/{ticker}"
                        params = {"timeseries": days}
                        ticker_data, ticker_error = self._make_request(endpoint, params)
                        
                        if ticker_data and "historical" in ticker_data:
                            historical = ticker_data.get("historical", [])
                            if historical:
                                df = pd.DataFrame(historical)
                                if "date" in df.columns and "close" in df.columns:
                                    df["date"] = pd.to_datetime(df["date"])
                                    df = df.set_index("date").sort_index()
                                    all_data[ticker] = df["close"]
                                    continue
                        failed_tickers.append(ticker)
                        if ticker_error:
                            error_details[ticker] = ticker_error
                    continue
                
                # Process batch response - can be a list or dict
                if isinstance(data, list):
                    # Multiple tickers returned as list
                    for ticker_data in data:
                        if isinstance(ticker_data, dict) and "symbol" in ticker_data:
                            ticker = ticker_data["symbol"]
                            historical = ticker_data.get("historical", [])
                            if historical:
                                df = pd.DataFrame(historical)
                                if "date" in df.columns and "close" in df.columns:
                                    df["date"] = pd.to_datetime(df["date"])
                                    df = df.set_index("date").sort_index()
                                    all_data[ticker] = df["close"]
                                else:
                                    failed_tickers.append(ticker)
                            else:
                                failed_tickers.append(ticker)
                elif isinstance(data, dict) and "historical" in data:
                    # Single ticker response
                    ticker = batch[0]  # Assume first ticker in batch
                    historical = data.get("historical", [])
                    if historical:
                        df = pd.DataFrame(historical)
                        if "date" in df.columns and "close" in df.columns:
                            df["date"] = pd.to_datetime(df["date"])
                            df = df.set_index("date").sort_index()
                            all_data[ticker] = df["close"]
                        else:
                            failed_tickers.append(ticker)
                    else:
                        failed_tickers.append(ticker)
                else:
                    # Unexpected format, fall back to individual
                    for ticker in batch:
                        failed_tickers.append(ticker)
                
                # Rate limiting: small delay between batches
                time.sleep(0.2)
                
            except Exception as e:
                error_msg = f"Error processing batch {batch}: {e}"
                print(error_msg)
                for ticker in batch:
                    failed_tickers.append(ticker)
                    error_details[ticker] = error_msg
        
        if failed_tickers:
            print(f"\n{'='*80}")
            print(f"Warning: Failed to fetch data for {len(failed_tickers)} tickers")
            print(f"{'='*80}")
            
            # Print first few error details
            print("\nSample error details (first 10 failures):")
            for i, ticker in enumerate(failed_tickers[:10]):
                error = error_details.get(ticker, "No error details available")
                print(f"  {ticker}: {error}")
            
            if len(failed_tickers) > 10:
                print(f"\n... and {len(failed_tickers) - 10} more failures")
            
            # Check if there's a common error pattern
            if error_details:
                error_counts = {}
                for error in error_details.values():
                    # Extract status code if present
                    if "HTTP" in error:
                        status_match = error.split("HTTP")[1].split()[0] if "HTTP" in error else None
                        if status_match:
                            error_counts[status_match] = error_counts.get(status_match, 0) + 1
                
                if error_counts:
                    print(f"\nError summary:")
                    for status, count in error_counts.items():
                        print(f"  {status}: {count} failures")
            
            print(f"{'='*80}\n")
        
        if not all_data:
            raise RuntimeError("Failed to fetch historical prices for any tickers")
        
        # Combine all series into a DataFrame
        result_df = pd.DataFrame(all_data)
        result_df.index.name = "date"
        
        return result_df
    
    def filter_by_sector(self, companies: List[Dict], sector_name: str) -> List[Dict]:
        """
        Filter the universe by sector name.
        
        Args:
            companies: List of company dictionaries (e.g., from get_sp500_universe())
            sector_name: Sector name to filter by (case-sensitive)
            
        Returns:
            Filtered list of companies in the specified sector
        """
        if not companies:
            return []
        
        filtered = [
            company for company in companies
            if company.get("sector") == sector_name
        ]
        
        return filtered
