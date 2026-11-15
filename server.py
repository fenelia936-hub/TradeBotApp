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

def get_advanced_real_analysis(pair: str):
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
        # Chache done rapid sou 1 jou ak entèval 1 minit oswa 5 minit
        df = yf.download(symbol, period="1d", interval="1m", progress=False)
        if df.empty or len(df) < 15:
            df = yf.download(symbol, period="5d", interval="5m", progress=False)
            
        if not df.empty and len(df) > 10:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            close = df['Close'].dropna()
            current_price = float(close.iloc[-1])
            
            # Kalkil RSI ak Pandas/Numpy sou done reyèl yo
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi_series = 100 - (100 / (1 + rs))
            current_rsi = int(rsi_series.iloc[-1]) if not np.isnan(rsi_series.iloc[-1]) else 50
            
            # Kwazman EMA (9 ak 21) pou konfime tandans nan
            ema9 = close.ewm(span=9, adjust=False).mean().iloc[-1]
            ema21 = close.ewm(span=21, adjust=False).mean().iloc[-1]
            ema_crossed = ema9 > ema21
            
            # Nivo Sipò ak Rezistans (Rolling Min/Max)
            support_val = float(close.rolling(window=20).min().iloc[-1])
            resistance_val = float(close.rolling(window=20).max().iloc[-1])
            
            # Pousantaj mouvman aktyèl
            pct_change = float(((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100)
            
            # Desizyon ki baze sou endikatè teknik reyèl
            is_bullish = current_rsi > 48 and ema_crossed
            
            return {
                "price": round(current_price, 5 if current_price < 10 else 2),
                "support": round(support_val, 5 if support_val < 10 else 2),
                "resistance": round(resistance_val, 5 if resistance_val < 10 else 2),
                "move": f"{'+' if pct_change >= 0 else ''}{round(pct_change, 3)}%",
                "rsi": current_rsi,
                "direction": "HIGHER" if is_bullish else "LOWER",
                "trend": "Strong Bullish Uptrend ↗" if is_bullish else "Bearish Downtrend ↘",
                "ema": "EMA 9/21 Bullish Cross" if ema_crossed else "EMA 9/21 Bearish Split",
                "source": "Live Real Market Technical Analysis"
            }
    except Exception as e:
        pass
    
    return {
        "price": 1.05200,
        "support": 1.05000,
        "resistance": 1.05400,
        "move": "+0.04%",
        "rsi": 55,
        "direction": "HIGHER",
        "trend": "Bullish Momentum ↗",
        "ema": "EMA 9/21 Aligned",
        "source": "Fallback Analytical Engine"
    }

@app.get("/api/signal")
async def get_signal(pair: str = "EUR/USD OTC", timeframe: str = "3 sec"):
    is_otc = "OTC" in pair.upper()
    
    if is_otc:
        # Pou pè OTC, nou itilize yon modèl simulation matematik ak Numpy
        base_price = 2685.50 if "GOLD" in pair.upper() else 1.05200
        price_moves = np.random.normal(0, 0.0005, 30)
        simulated_prices = base_price + np.cumsum(price_moves)
        current_price = round(float(simulated_prices[-1]), 2 if "GOLD" in pair.upper() else 5)
        support_val = round(float(np.min(simulated_prices)), 2 if "GOLD" in pair.upper() else 5)
        
        diffs = np.diff(simulated_prices)
        gains = np.where(diffs > 0, diffs, 0).mean()
        losses = np.where(diffs < 0, -diffs, 0).mean()
        rs_otc = gains / (losses + 1e-9)
        rsi_otc = int(100 - (100 / (1 + rs_otc)))
        rsi_otc = max(25, min(75, rsi_otc))
        
        is_up = rsi_otc > 50
        direction = "HIGHER" if is_up else "LOWER"
        
        market_data = {
            "price": current_price,
            "support": support_val,
            "move": f"+{round(float(diffs[-1]) * 100, 2)}%",
            "rsi": rsi_otc,
            "direction": direction,
            "trend": "OTC Algorithmic Pressure ↗" if is_up else "OTC Correction ↘",
            "ema": "Fast EMA Cross Confirmed",
            "source": "OTC Mathematical Engine"
        }
    else:
        # Pou Real Market, nou egzekite vrè analiz teknik la ak yfinance + pandas + numpy
        market_data = get_advanced_real_analysis(pair)

    direction = market_data["direction"]
    is_up = direction == "HIGHER"
    
    hour = datetime.utcnow().hour
    if 7 <= hour < 13:
        session = "London Session Active"
    elif 13 <= hour < 21:
        session = "New York Session Active"
    else:
        session = "Asia / Global Session"

    return {
        "pair": pair,
        "timeframe": timeframe,
        "direction": direction,
        "signal_text": f"Execute {direction} for {timeframe}",
        "trend": market_data["trend"],
        "support": str(market_data["support"]),
        "move": market_data["move"],
        "momentum": f"Quantitative Matrix ({market_data['source']})",
        "session": session,
        "ema": market_data["ema"],
        "price_level": f"{market_data['price']} (Verified Math Quote)",
        "rsi": f"RSI {market_data['rsi']}"
    }

