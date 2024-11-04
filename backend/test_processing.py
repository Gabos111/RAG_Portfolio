# src/test_processing.py

from data_collection import MarketDataCollector
from data_processing import PortfolioAnalyzer

def main():
    # Get data
    collector = MarketDataCollector()
    prices_df, returns_df = collector.fetch_stock_data()
    
    # Initialize analyzer
    analyzer = PortfolioAnalyzer(prices_df, returns_df)
    
    # Calculate and print metrics
    basic_metrics = analyzer.calculate_basic_metrics()
    risk_metrics = analyzer.calculate_risk_metrics()
    
    print("\nBasic Portfolio Metrics:")
    for metric, value in basic_metrics.items():
        print(f"{metric}: {value:.2%}")
    
    print("\nRisk Metrics:")
    for metric, value in risk_metrics.items():
        print(f"{metric}: {value:.2f}")

if __name__ == "__main__":
    main()