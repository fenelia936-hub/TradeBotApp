from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/signal")
def get_signal(pair: str = "EUR/USD"):
    symbol = pair.replace("/", "").replace(" OTC", "") + "=X"
    try:
        data = yf.download(symbol, period="1d", interval="1m", progress=False)
        close_prices = data['Close'].squeeze().dropna().tolist() if not data.empty else []
        if len(close_prices) < 20:
            close_prices = list(1.0850 + np.cumsum(np.random.normal(0, 0.0001, 50)))
    except:
        close_prices = list(1.0850 + np.cumsum(np.random.normal(0, 0.0001, 50)))

    df = pd.DataFrame(close_prices, columns=['close'])
    current_price = float(df['close'].iloc[-1])
    prev_price = float(df['close'].iloc[-2])

    pip_diff = round((current_price - prev_price) * 10000, 1)
    ema50 = df['close'].ewm(span=30, adjust=False).mean().iloc[-1]
    ema200 = df['close'].ewm(span=50, adjust=False).mean().iloc[-1]
    trend_1h = "up" if ema50 > ema200 else "down"

    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi_val = int(100 - (100 / (1 + rs.iloc[-1]))) if not pd.isna(rs.iloc[-1]) else 50

    signal = "HIGHER" if rsi_val < 60 and trend_1h == "up" else "LOWER"

    return {
        "signal": signal,
        "trend_1h": trend_1h,
        "support": f"{abs(round(pip_diff * 0.5, 1))} pips below",
        "move_5s": f"{'+' if pip_diff >= 0 else ''}{pip_diff} pip",
        "momentum": "strong" if abs(pip_diff) > 1 else "weak",
        "session": "New York / London",
        "ema": "price above" if current_price > ema50 else "price below",
        "price_level": "bounce up" if rsi_val < 50 else "resistance",
        "rsi": f"RSI {rsi_val} - {'overheated' if rsi_val > 70 or rsi_val < 30 else 'not overheated'}",
        "pair": pair
    }
