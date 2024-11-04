import yfinance as yf
import pandas as pd
from config import STOCKS, BENCHMARKS, START_DATE, END_DATE
import logging
import os

class MarketDataCollector:
    def __init__(self):
        # Flatten stock list from all sectors
        self.all_stocks = [stock for sector in STOCKS.values() for stock in sector]
        self.benchmarks = list(BENCHMARKS.values())
        
    def fetch_stock_data(self):
        """
        Fetches daily data for all stocks and benchmarks
        Returns:
            - prices_df: DataFrame with adjusted close prices
            - returns_df: DataFrame with daily returns
        """
        prices_path = 'data/raw/prices.csv'
        returns_path = 'data/raw/returns.csv'

        if os.path.exists(prices_path) and os.path.exists(returns_path):
            logging.info("Loading data from cache...")
            prices_df = pd.read_csv(prices_path, index_col=0, parse_dates=True)
            returns_df = pd.read_csv(returns_path, index_col=0, parse_dates=True)
        else:
            try:
                logging.info("Fetching market data...")
                df = yf.download(
                    self.all_stocks + self.benchmarks,
                    start=START_DATE,
                    end=END_DATE,
                    progress=False
                )
                # Fetch all symbols (stocks + benchmarks)
                all_symbols = self.all_stocks + self.benchmarks
                
                # Download data
                print("Fetching market data...")
                df = yf.download(
                    all_symbols,
                    start=START_DATE,
                    end=END_DATE,
                    progress=False
                )
                
                # Extract adjusted close prices
                prices_df = df['Adj Close']
                
                # Calculate returns
                returns_df = prices_df.pct_change()
                
                # Save raw data
                prices_df.to_csv('data/raw/prices.csv')
                returns_df.to_csv('data/raw/returns.csv')
                logging.info("Market data fetched successfully.")
            except Exception as e:
                logging.error(f"Error fetching market data: {e}")
                raise
            prices_df.to_csv(prices_path)
            returns_df.to_csv(returns_path)
        return prices_df, returns_df

def main():
    # Initialize collector
    collector = MarketDataCollector()
    
    # Fetch data
    prices, returns = collector.fetch_stock_data()
    
    print("Data collection completed.")
    print(f"Collected data for {len(collector.all_stocks)} stocks and {len(collector.benchmarks)} benchmarks")
    print(f"Data shape: {prices.shape}")

if __name__ == "__main__":
    main()