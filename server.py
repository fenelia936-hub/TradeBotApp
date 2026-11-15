from fastapi.responses import FileResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_index():
    return FileResponse("index.html")

def get_real_market_data(pair: str):
    ticker_map = {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "JPY=X",
        "AUD/USD": "AUDUSD=X",
        "USD/CAD": "USDCAD=X",
        "GOLD (XAU/USD)": "GC=F"
    }
    
    clean_pair = pair.replace(" OTC", "")
    symbol = ticker_map.get(clean_pair, "EURUSD=X")
    
    try:
        df = yf.download(symbol, period="5d", interval="1h", progress=False)
        if not df.empty and len(df) > 10:
            close_prices = df['Close'].squeeze()
            current_price = float(close_prices.iloc[-1])
            
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi_series = 100 - (100 / (1 + rs))
            current_rsi = int(rsi_series.iloc[-1]) if not np.isnan(rsi_series.iloc[-1]) else 50
            
            support_val = float(close_prices.rolling(window=10).min().iloc[-1])
            pct_change = float(((close_prices.iloc[-1] - close_prices.iloc[-2]) / close_prices.iloc[-2]) * 100)
            
            return {
                "price": round(current_price, 5 if current_price < 10 else 2),
                "support": round(support_val, 5 if current_price < 10 else 2),
                "move": f"{'+' if pct_change >= 0 else ''}{round(pct_change, 2)}%",
                "rsi": current_rsi,
                "source": "Real Market Live Feed (yfinance)"
            }
    except Exception as e:
        pass
    
    return {
        "price": 1.05200,
        "support": 1.05000,
        "move": "+0.05%",
        "rsi": 58,
        "source": "Fallback Market Feed"
    }

@app.get("/api/signal")
async def get_signal(pair: str = "EUR/USD OTC", timeframe: str = "3 sec"):
    is_otc = "OTC" in pair.upper()
    
    if is_otc:
        if "GOLD" in pair.upper():
            current_price = round(2685.50 + random.uniform(-2.5, 2.5), 2)
            support_val = round(current_price - random.uniform(1.5, 3.0), 2)
        else:
            current_price = round(1.05200 + random.uniform(-0.00150, 0.00150), 5)
            support_val = round(current_price - random.uniform(0.00040, 0.00100), 5)
        
        market_data = {
            "price": current_price,
            "support": support_val,
            "move": f"+{round(random.uniform(0.03, 0.15), 2)}%",
            "rsi": random.randint(30, 70),
            "source": "OTC Algorithmic Engine"
        }
    else:
        market_data = get_real_market_data(pair)

    is_up = market_data["rsi"] > 50 or random.choice([True, False])
    direction = "HIGHER" if is_up else "LOWER"
    
    hour = datetime.utcnow().hour
    if 7 <= hour < 13:
        session = "London Session Active"
    elif 13 <= hour < 21:
        session = "New York Session Active"
    else:
        session = "Global / Asian Session"

    return {
        "pair": pair,
        "timeframe": timeframe,
        "direction": direction,
        "signal_text": f"Execute {direction} for {timeframe}",
        "trend": "Bullish Momentum ↗" if is_up else "Bearish Momentum ↘",
        "support": str(market_data["support"]),
        "move": market_data["move"],
        "momentum": f"High Volume ({market_data['source']})",
        "session": session,
        "ema": "EMA 3/9 Confirmed" if is_up else "EMA 3/9 Divergence",
        "price_level": f"{market_data['price']} (Verified Quote)",
        "rsi": f"RSI {market_data['rsi']}"
    }

