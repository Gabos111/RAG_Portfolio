# backend/main.py

from fastapi import FastAPI, HTTPException
from backend.config import STOCKS, BENCHMARKS, PORTFOLIO_WEIGHTS
from backend.data_collection import MarketDataCollector
from backend.data_processing import PortfolioAnalyzer
from backend.retrieve_and_answer import retrieve_and_answer
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px  # Added this import
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)

app = FastAPI()

# Allow CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the RAG Portfolio API"}


@app.get("/portfolio")
def get_portfolio():
    try:
        portfolio_data = [
            {
                "name": "UBS Group",
                "ticker": "UBSG.SW",
                "percentage": 10.0,
                "color": "#1f77b4",
                "sector": "Swiss Banking & Finance"
            },
            {
                "name": "ABB Group",
                "ticker": "ABBN.SW",
                "percentage": 7.5,
                "color": "#ff7f0e",
                "sector": "Tech Switzerland"
            },
            {
                "name": "Schindler",
                "ticker": "SCHN.SW",
                "percentage": 7.5,
                "color": "#2ca02c",
                "sector": "Tech Switzerland"
            },
            {
                "name": "Nestlé",
                "ticker": "NESN.SW",
                "percentage": 10.0,
                "color": "#d62728",
                "sector": "Swiss Healthcare & Consumer"
            },
            {
                "name": "Roche",
                "ticker": "ROG.SW",
                "percentage": 7.5,
                "color": "#9467bd",
                "sector": "Swiss Healthcare & Consumer"
            },
            {
                "name": "Novartis",
                "ticker": "NOVN.SW",
                "percentage": 7.5,
                "color": "#8c564b",
                "sector": "Swiss Healthcare & Consumer"
            },
            {
                "name": "Apple",
                "ticker": "AAPL",
                "percentage": 10.0,
                "color": "#e377c2",
                "sector": "Global Tech"
            },
            {
                "name": "Microsoft",
                "ticker": "MSFT",
                "percentage": 7.5,
                "color": "#7f7f7f",
                "sector": "Global Tech"
            },
            {
                "name": "Alphabet",
                "ticker": "GOOGL",
                "percentage": 7.5,
                "color": "#bcbd22",
                "sector": "Global Tech"
            },
            {
                "name": "BlackRock",
                "ticker": "BLK",
                "percentage": 10.0,
                "color": "#17becf",
                "sector": "Global Finance"
            },
            {
                "name": "JP Morgan",
                "ticker": "JPM",
                "percentage": 7.5,
                "color": "#aec7e8",
                "sector": "Global Finance"
            },
            {
                "name": "Goldman Sachs",
                "ticker": "GS",
                "percentage": 7.5,
                "color": "#ffbb78",
                "sector": "Global Finance"
            }
        ]
        
        return JSONResponse(content=portfolio_data)
    except Exception as e:
        logging.exception("An error occurred in /portfolio endpoint.")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/prices")
def get_portfolio_prices():
    try:
        # Initialize collector and fetch data
        collector = MarketDataCollector()
        prices_df = collector.fetch_stock_data()[0]
        
        # First convert all numeric columns to float64
        numeric_columns = prices_df.select_dtypes(include=['float64', 'float32', 'int64', 'int32']).columns
        for col in numeric_columns:
            prices_df[col] = prices_df[col].astype('float64')
        
        # Replace problematic values
        prices_df = prices_df.replace([np.inf, -np.inf, np.nan], None)
        
        # Handle remaining problematic floats by converting to strings with fixed precision
        for col in numeric_columns:
            prices_df[col] = prices_df[col].apply(
                lambda x: round(float(x), 4) if x is not None else None
            )
        
        # Convert DataFrame to JSON
        prices_df.index = prices_df.index.strftime('%Y-%m-%d')
        
        # Convert to records and explicitly handle any remaining problematic values
        records = []
        for record in prices_df.reset_index().melt(id_vars='Date').to_dict(orient='records'):
            cleaned_record = {}
            for key, value in record.items():
                if isinstance(value, float):
                    if np.isfinite(value):
                        cleaned_record[key] = round(value, 4)
                    else:
                        cleaned_record[key] = None
                else:
                    cleaned_record[key] = value
            records.append(cleaned_record)
        
        return JSONResponse(content=records)
    except Exception as e:
        logging.exception("An error occurred in /portfolio/prices endpoint.")
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/portfolio/graphs")
def get_portfolio_graphs():
    try:
        # Initialize collector and fetch data
        collector = MarketDataCollector()
        prices_df, returns_df = collector.fetch_stock_data()
        
        # Generate Performance Chart
        normalized = prices_df.div(prices_df.iloc[0]) * 100
        fig1 = go.Figure()
        for col in normalized.columns:
            fig1.add_trace(go.Scatter(
                x=normalized.index,
                y=normalized[col],
                name=col,
                mode='lines'
            ))
        fig1.update_layout(title='Portfolio Performance (Normalized to 100)')
        
        # Generate Risk-Return Scatter Plot
        annual_returns = returns_df.mean() * 252
        annual_vol = returns_df.std() * (252 ** 0.5)
        fig2 = px.scatter(
            x=annual_vol,
            y=annual_returns,
            text=annual_returns.index,
            title='Risk-Return Analysis',
            labels={'x': 'Annual Volatility', 'y': 'Annual Return'}
        )
        
        # Convert figures to JSON
        graphJSON1 = fig1.to_json()
        graphJSON2 = fig2.to_json()
        
        return {
            "performance_chart": graphJSON1,
            "risk_return_scatter": graphJSON2
        }
    except Exception as e:
        logging.exception("An error occurred in /portfolio/graphs endpoint.")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/performance")
def get_portfolio_performance():
    try:
        # Initialize collector and fetch data
        collector = MarketDataCollector()
        prices_df, returns_df = collector.fetch_stock_data()
        
        # Print debug information
        print("Original prices head:")
        print(prices_df.head())
        print("\nColumns with null values:", prices_df.isnull().sum())
        
        # Remove columns that are completely null
        prices_df = prices_df.dropna(axis=1, how='all')
        
        # For remaining columns, handle partial null values
        prices_df = prices_df.fillna(method='ffill').fillna(method='bfill')
        
        def safe_float(x):
            try:
                if pd.isna(x) or not np.isfinite(x):
                    return None
                # Convert to float and round to 4 decimal places
                val = round(float(x), 4)
                # Check if value is within safe JSON range
                if abs(val) > 1e308:
                    return None
                return val
            except:
                return None
        
        # Normalize prices to 100 for performance chart
        # Only normalize if first row value exists
        normalized_prices = pd.DataFrame(index=prices_df.index)
        for column in prices_df.columns:
            if not pd.isna(prices_df[column].iloc[0]):
                normalized_prices[column] = (prices_df[column] / prices_df[column].iloc[0]) * 100
        
        # Handle any remaining special float values
        for column in normalized_prices.columns:
            normalized_prices[column] = normalized_prices[column].apply(safe_float)
        
        # Format dates
        normalized_prices.index = normalized_prices.index.strftime('%Y-%m-%d')
        
        # Create normalized prices data with better handling of null values
        normalized_data = []
        for date in normalized_prices.index:
            row_data = {'date': date}
            for column in normalized_prices.columns:
                value = normalized_prices.loc[date, column]
                if pd.notnull(value) and value is not None:
                    row_data[column] = value
                else:
                    row_data[column] = None  # Explicit null for missing values
            normalized_data.append(row_data)
        
        # Calculate risk-return metrics only for non-null columns
        valid_returns = returns_df.dropna(axis=1, how='all')
        annual_returns = valid_returns.mean() * 252
        annual_vol = valid_returns.std() * np.sqrt(252)
        
        # Create risk-return data
        risk_return_data = []
        for stock in valid_returns.columns:
            ret = safe_float(annual_returns.get(stock))
            vol = safe_float(annual_vol.get(stock))
            if ret is not None and vol is not None:
                risk_return_data.append({
                    'stock': stock,
                    'annualReturn': ret,
                    'annualVolatility': vol
                })
        
        return JSONResponse(content={
            "normalized_prices": normalized_data,
            "risk_return_data": risk_return_data
        })
        
    except Exception as e:
        logging.exception("An error occurred in /portfolio/performance endpoint.")
        print(f"Error details: {str(e)}")  # Add detailed error logging
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/metrics")
def get_portfolio_metrics():
    try:
        # Initialize collector and fetch data
        collector = MarketDataCollector()
        prices_df, returns_df = collector.fetch_stock_data()

        # Initialize analyzer and calculate metrics
        analyzer = PortfolioAnalyzer(prices_df, returns_df)
        basic_metrics = analyzer.calculate_basic_metrics()
        risk_metrics = analyzer.calculate_risk_metrics()

        return {
            "basic_metrics": basic_metrics,
            "risk_metrics": risk_metrics
        }
    except Exception as e:
        logging.exception("An error occurred in /portfolio/metrics endpoint.")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    try:
        answer = retrieve_and_answer(request.query)
        return {"answer": answer}
    except Exception as e:
        logging.exception("An error occurred in /chat endpoint.")
        raise HTTPException(status_code=500, detail=str(e))
