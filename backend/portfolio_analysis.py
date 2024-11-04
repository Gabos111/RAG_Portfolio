# backend/src/portfolio_analysis.py

import pandas as pd
import numpy as np
from config import PORTFOLIO_WEIGHTS

def calculate_portfolio_metrics(returns_df):
    """Calculate main portfolio metrics"""
    # Verify which stocks we have data for
    available_stocks = set(returns_df.columns)
    portfolio_stocks = set(PORTFOLIO_WEIGHTS.keys())

    # Adjust weights for available stocks
    adjusted_weights = {
        stock: weight for stock, weight in PORTFOLIO_WEIGHTS.items()
        if stock in available_stocks
    }

    # Normalize weights to sum to 1
    total_weight = sum(adjusted_weights.values())
    if total_weight == 0:
        raise ValueError("Total weight of available stocks is zero.")

    adjusted_weights = {
        k: v / total_weight for k, v in adjusted_weights.items()
    }

    # Calculate portfolio returns using adjusted weights
    weights_series = pd.Series(adjusted_weights)
    portfolio_returns = returns_df[weights_series.index].dot(weights_series)

    # Calculate metrics
    metrics = {
        'Total Return': (1 + portfolio_returns).prod() - 1,
        'Annual Return': portfolio_returns.mean() * 252,
        'Annual Volatility': portfolio_returns.std() * np.sqrt(252),
        'Sharpe Ratio': (portfolio_returns.mean() * 252) / (portfolio_returns.std() * np.sqrt(252)),
        'Max Drawdown': calculate_max_drawdown(portfolio_returns)
    }

    return metrics, portfolio_returns

def calculate_max_drawdown(returns):
    """Calculate maximum drawdown"""
    cum_returns = (1 + returns).cumprod()
    rolling_max = cum_returns.cummax()
    drawdowns = cum_returns / rolling_max - 1
    return drawdowns.min()
