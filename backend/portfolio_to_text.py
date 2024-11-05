import json
from datetime import datetime
from collections import defaultdict
import re

def create_portfolio_weights_chunk():
    # Portfolio description with keywords for better RAG matching
    content = """
    Portfolio Asset Allocation and Weights Distribution Analysis
    
    The investment portfolio follows a balanced sector allocation strategy across Swiss and Global markets. 
    The total portfolio allocation equals 100% (1.0) distributed across multiple sectors and companies:

    Swiss Banking & Finance Sector (10%):
    - UBS Group (UBSG.SW): 10% allocation
    
    Swiss Technology Sector (15%):
    - ABB Group (ABBN.SW): 7.5% allocation
    - Schindler (SCHN.SW): 7.5% allocation
    
    Swiss Healthcare & Consumer Sector (25%):
    - Nestlé (NESN.SW): 10% allocation
    - Roche (ROG.SW): 7.5% allocation
    - Novartis (NOVN.SW): 7.5% allocation
    
    Global Technology Sector (25%):
    - Apple Inc. (AAPL): 10% allocation
    - Microsoft Corporation (MSFT): 7.5% allocation
    - Alphabet Inc. (GOOGL): 7.5% allocation
    
    Global Finance Sector (25%):
    - BlackRock Inc. (BLK): 10% allocation
    - JP Morgan Chase (JPM): 7.5% allocation
    - Goldman Sachs Group (GS): 7.5% allocation

    This allocation strategy maintains a balanced exposure across sectors while emphasizing both Swiss and global market opportunities. The portfolio construction focuses on blue-chip companies with strong market positions in their respective sectors.
    """

    # Create chunk with the same structure as your previous chunks
    chunk = {
        "chunk_id": "PORTFOLIO_WEIGHTS_001",
        "content": content,
        "word_count": len(content.split()),
        "keyword_analysis": {
            "FINANCIAL_METRICS": {
                "balance_sheet": [
                    {
                        "keyword": "allocation",
                        "context": "The total portfolio allocation equals 100% (1.0) distributed across multiple sectors",
                        "position": 150,
                        "sentence": "The total portfolio allocation equals 100% (1.0) distributed across multiple sectors and companies."
                    }
                ]
            },
            "COMPANY_STATE": {
                "market_position": [
                    {
                        "keyword": "blue-chip",
                        "context": "The portfolio construction focuses on blue-chip companies with strong market positions",
                        "position": 800,
                        "sentence": "The portfolio construction focuses on blue-chip companies with strong market positions in their respective sectors."
                    }
                ]
            },
            "BUSINESS_OUTLOOK": {
                "strategic_initiatives": [
                    {
                        "keyword": "strategy",
                        "context": "The portfolio follows a balanced sector allocation strategy across Swiss and Global markets",
                        "position": 50,
                        "sentence": "The investment portfolio follows a balanced sector allocation strategy across Swiss and Global markets."
                    }
                ]
            }
        },
        "company": "PORTFOLIO",
        "year": str(datetime.now().year),
        "source": "config.py",
        "processing_date": datetime.now().isoformat(),
        "portfolio_weights": {
            "sectors": {
                "Swiss Banking & Finance": {
                    "weight": 0.10,
                    "stocks": {"UBSG.SW": 0.10}
                },
                "Swiss Technology": {
                    "weight": 0.15,
                    "stocks": {"ABBN.SW": 0.075, "SCHN.SW": 0.075}
                },
                "Swiss Healthcare & Consumer": {
                    "weight": 0.25,
                    "stocks": {"NESN.SW": 0.10, "ROG.SW": 0.075, "NOVN.SW": 0.075}
                },
                "Global Technology": {
                    "weight": 0.25,
                    "stocks": {"AAPL": 0.10, "MSFT": 0.075, "GOOGL": 0.075}
                },
                "Global Finance": {
                    "weight": 0.25,
                    "stocks": {"BLK": 0.10, "JPM": 0.075, "GS": 0.075}
                }
            },
            "total_weight": 1.0
        }
    }

    return chunk

def add_chunk_to_existing_file(new_chunk, file_path='data/raw_processed/all_chunks.json'):
    try:
        # Read existing chunks
        with open(file_path, 'r') as f:
            chunks = json.load(f)
        
        # Add new chunk
        if isinstance(chunks, list):
            chunks.append(new_chunk)
        else:
            chunks = [chunks, new_chunk]
        
        # Write back to file
        with open(file_path, 'w') as f:
            json.dump(chunks, f, indent=2)
            
        print(f"Successfully added portfolio weights chunk to {file_path}")
        
    except FileNotFoundError:
        # If file doesn't exist, create it with the new chunk
        with open(file_path, 'w') as f:
            json.dump([new_chunk], f, indent=2)
        print(f"Created new file {file_path} with portfolio weights chunk")
    
    except Exception as e:
        print(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    # Create and add the chunk
    portfolio_chunk = create_portfolio_weights_chunk()
    add_chunk_to_existing_file(portfolio_chunk)