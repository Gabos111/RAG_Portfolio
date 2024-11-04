# src/data_processing.py

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from config import PORTFOLIO_WEIGHTS, BENCHMARKS
from config import RISK_FREE_RATE, BENCHMARK_INDEX

### PERFORMANCE METRICS ###
# - Total Return: Overall portfolio return over the entire period
#   Formula: (Final Value / Initial Value) - 1
  
# - Annual Return: Average yearly return
#   Formula: Daily Returns Mean * 252 (trading days)
#   Interpretation: Higher is better, but consider risk

# - Annual Volatility: Yearly price fluctuation measure
#   Formula: Daily Returns Std * sqrt(252)
#   Interpretation: Lower means more stable returns

# - Sharpe Ratio: Risk-adjusted return measure
#   Formula: (Annual Return - Risk Free Rate) / Annual Volatility
#   Interpretation: Higher is better, >1 is good, >2 is very good

# - Maximum Drawdown: Biggest peak-to-trough decline
#   Formula: Minimum of (Current Value / Peak Value - 1)
#   Interpretation: Measures worst historical loss


### RISK METRICS ###
# - Beta: Market sensitivity measure
#   Formula: Covariance(Portfolio, Benchmark) / Variance(Benchmark)
#   Interpretation: 
#     >1: More volatile than market
#     <1: Less volatile than market
#     =1: Moves with market

# - Alpha (Jensen's): Excess return over market
#   Formula: Portfolio Return - (Risk Free + Beta * Market Premium)
#   Interpretation: Higher is better, shows stock selection skill

# - Information Ratio: Risk-adjusted excess returns
#   Formula: (Portfolio Return - Benchmark Return) / Tracking Error
#   Interpretation: Higher is better, shows consistency of outperformance


class PortfolioAnalyzer:
    def __init__(self, prices_df: pd.DataFrame, returns_df: pd.DataFrame, risk_free_rate: float = RISK_FREE_RATE, benchmark_symbol: str = BENCHMARK_INDEX):
        self.prices_df = prices_df
        self.returns_df = returns_df
        self.risk_free_rate = risk_free_rate
        self.benchmark = benchmark_symbol
        self.portfolio_weights = pd.Series(PORTFOLIO_WEIGHTS)
        self.benchmark = BENCHMARKS['SMI']  # Using Swiss Market Index as benchmark
        
    def calculate_portfolio_returns(self) -> pd.Series:
        """Calculate weighted portfolio returns"""
        return self.returns_df[self.portfolio_weights.index].dot(self.portfolio_weights)

    def calculate_basic_metrics(self) -> Dict:
        """Calculate main portfolio metrics"""
        portfolio_returns = self.calculate_portfolio_returns()
        
        metrics = {
            'Total Return': (1 + portfolio_returns).prod() - 1,
            'Annual Return': portfolio_returns.mean() * 252,
            'Annual Volatility': portfolio_returns.std() * np.sqrt(252),
            'Sharpe Ratio': (portfolio_returns.mean() * 252) / (portfolio_returns.std() * np.sqrt(252)),
            'Max Drawdown': self.calculate_max_drawdown(portfolio_returns)
        }
        
        return metrics
    
    def calculate_risk_metrics(self) -> Dict:
        """Calculate risk-related metrics"""
        portfolio_returns = self.calculate_portfolio_returns()
        benchmark_returns = self.returns_df[self.benchmark]
        
        # Calculate beta
        cov = portfolio_returns.cov(benchmark_returns)
        benchmark_var = benchmark_returns.var()
        beta = cov / benchmark_var
        
        risk_metrics = {
            'Beta': beta,
            'Alpha': self.calculate_alpha(portfolio_returns, benchmark_returns, beta),
            'Information Ratio': self.calculate_information_ratio(portfolio_returns, benchmark_returns)
        }
        
        return risk_metrics

    @staticmethod
    def calculate_max_drawdown(returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        cum_returns = (1 + returns).cumprod()
        rolling_max = cum_returns.expanding().max()
        drawdowns = cum_returns / rolling_max - 1
        return drawdowns.min()

    def calculate_alpha(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series, beta: float) -> float:
        """Calculate Jensen's Alpha"""
        rf = self.risk_free_rate
        portfolio_excess_return = portfolio_returns.mean() * 252 - rf
        market_excess_return = benchmark_returns.mean() * 252 - rf
        return portfolio_excess_return - beta * market_excess_return

    def calculate_information_ratio(self, portfolio_returns: pd.Series, 
                                  benchmark_returns: pd.Series) -> float:
        """Calculate Information Ratio"""
        active_returns = portfolio_returns - benchmark_returns
        return (active_returns.mean() * 252) / (active_returns.std() * np.sqrt(252))