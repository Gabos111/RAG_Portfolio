# src/config.py

# src/config.py

import os
from dotenv import load_dotenv

load_dotenv()

# Time period for analysis
START_DATE = os.getenv('START_DATE', '2023-01-01')
END_DATE = os.getenv('END_DATE', '2024-06-30')

# Risk-free rate
RISK_FREE_RATE = float(os.getenv('RISK_FREE_RATE', '0.02'))

# Benchmark Index
BENCHMARK_INDEX = os.getenv('BENCHMARK_INDEX', '^SSMI')


# Stocks organized by sectors relevant to Swiss/Global markets
STOCKS = {
    'Swiss Banking & Finance': [
        'UBSG.SW',    # UBS Group
    ],

    'Tech switzerland': [
        'ABBN.SW',     # ABB Group
        'SCHN.SW',     # Schindler
    ],
    'Swiss Healthcare & Consumer': [
        'NESN.SW',    # Nestlé
        'ROG.SW',     # Roche
        'NOVN.SW',    # Novartis
    ],
    'Global Tech': [
        'AAPL',       # Apple
        'MSFT',       # Microsoft
        'GOOGL',      # Alphabet
    ],
    'Global Finance': [
        'BLK',        # BlackRock
        'JPM',        # JP Morgan
        'GS'          # Goldman Sachs
    ]
}

# Benchmark Indices
BENCHMARKS = {
    'SPX': '^GSPC',    # S&P 500
    'SMI': '^SSMI',    # Swiss Market Index
    'CAC40': '^FCHI'   # CAC 40
}


# Portfolio allocation (balanced across sectors)
PORTFOLIO_WEIGHTS = {
    # Swiss Banking & Finance (25%)
    'UBSG.SW': 0.10,

    # Tech switzerland (7.5%)
    'ABBN.SW': 0.075,
    'SCHN.SW': 0.075,
    # Swiss Healthcare & Consumer (25%)
    'NESN.SW': 0.10,
    'ROG.SW': 0.075,
    'NOVN.SW': 0.075,
    
    # Global Tech (25%)
    'AAPL': 0.10,
    'MSFT': 0.075,
    'GOOGL': 0.075,
    
    # Global Finance (25%)
    'BLK': 0.10,
    'JPM': 0.075,
    'GS': 0.075
}

# Validation for portfolio weights
total_weight = sum(PORTFOLIO_WEIGHTS.values())
if not abs(total_weight - 1.0) < 1e-6:
    raise ValueError(f"Total portfolio weights must sum to 1.0, but got {total_weight}")