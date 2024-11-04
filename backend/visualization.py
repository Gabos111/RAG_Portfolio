# src/visualization.py

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

### VISUALIZATION ###
# - Performance Dashboard:
#   * Portfolio Value Evolution: Shows growth of investment
#   * Return Distribution: Shows return patterns
#   * Drawdown Analysis: Shows periods of losses
#   * Rolling Volatility: Shows risk changes over time

# - Risk-Return Scatter:
#   * Visual comparison of all assets
#   * X-axis: Risk (Volatility)
#   * Y-axis: Return

class PortfolioVisualizer:
    def __init__(self, prices_df: pd.DataFrame, returns_df: pd.DataFrame, portfolio_returns: pd.Series):
        self.prices_df = prices_df
        self.returns_df = returns_df
        self.portfolio_returns = portfolio_returns

    def create_performance_dashboard(self):
        """Creates main performance dashboard"""
        # Create figure with secondary y-axis
        fig = make_subplots(rows=2, cols=2,
                           subplot_titles=('Portfolio Value Evolution',
                                         'Return Distribution',
                                         'Drawdown Analysis',
                                         'Rolling Volatility'))

        # 1. Portfolio Value Evolution (normalized to 100)
        cum_returns = (1 + self.portfolio_returns).cumprod() * 100
        fig.add_trace(
            go.Scatter(x=cum_returns.index, y=cum_returns,
                      name='Portfolio Value'),
            row=1, col=1
        )

        # 2. Return Distribution
        fig.add_trace(
            go.Histogram(x=self.portfolio_returns,
                        name='Returns Distribution',
                        nbinsx=50),
            row=1, col=2
        )

        # 3. Drawdown Analysis
        drawdown = self.calculate_drawdown()
        fig.add_trace(
            go.Scatter(x=drawdown.index, y=drawdown,
                      name='Drawdown',
                      fill='tozeroy'),
            row=2, col=1
        )

        # 4. Rolling Volatility (21 days)
        rolling_vol = self.portfolio_returns.rolling(21).std() * np.sqrt(252)
        fig.add_trace(
            go.Scatter(x=rolling_vol.index, y=rolling_vol,
                      name='21D Rolling Vol'),
            row=2, col=2
        )

        # Update layout
        fig.update_layout(
    hovermode='x unified',
    sliders=[dict(
        steps=[dict(method='restyle', args=['visible', [True, False]], label='Option 1')],
        # ... (additional slider configuration)
    )]
)
        return fig

    def create_risk_return_scatter(self):
        """Creates risk-return scatter plot for all assets"""
        annual_returns = self.returns_df.mean() * 252
        annual_vol = self.returns_df.std() * np.sqrt(252)
        
        fig = px.scatter(
            x=annual_vol, y=annual_returns,
            text=self.returns_df.columns,
            labels={'x': 'Annual Volatility',
                   'y': 'Annual Return'},
            title='Risk-Return Analysis'
        )
        return fig

    def calculate_drawdown(self):
        """Calculate drawdown series"""
        cum_returns = (1 + self.portfolio_returns).cumprod()
        rolling_max = cum_returns.expanding().max()
        drawdown = cum_returns / rolling_max - 1
        return drawdown