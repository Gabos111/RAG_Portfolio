# backend/main.py

from fastapi import FastAPI, HTTPException
from src.data_processing import fetch_and_process_data
from src.portfolio_analysis import calculate_portfolio_metrics
from src.visualization import (
    get_portfolio_value_evolution,
    get_drawdown,
    get_rolling_volatility,
    get_return_distribution,
    get_risk_return_scatter
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow CORS for local development (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/portfolio")
def get_portfolio_data():
    try:
        prices, returns = fetch_and_process_data()
        metrics, portfolio_returns = calculate_portfolio_metrics(returns)
        response = {
            'metrics': metrics,
            'portfolio_returns': portfolio_returns.to_json(),
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio/performance")
def get_portfolio_performance():
    try:
        prices, returns = fetch_and_process_data()
        _, portfolio_returns = calculate_portfolio_metrics(returns)
        value_evolution = get_portfolio_value_evolution(portfolio_returns)
        drawdown = get_drawdown(portfolio_returns)
        rolling_volatility = get_rolling_volatility(portfolio_returns)
        return {
            'value_evolution': value_evolution,
            'drawdown': drawdown,
            'rolling_volatility': rolling_volatility,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio/risk_return")
def get_risk_return_data():
    try:
        prices, returns = fetch_and_process_data()
        _, portfolio_returns = calculate_portfolio_metrics(returns)
        risk_return_data = get_risk_return_scatter(returns, portfolio_returns)
        return risk_return_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Additional endpoints can be added as needed

# Define a request model
class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    try:
        # Call your RAG system function with the user's message
        response = your_rag_function(request.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))