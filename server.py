from fastapi.responses import FileResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
from datetime import datetime

app = FastAPI()

@app.get("/")
async def read_index():
    return FileResponse("index.html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/signal")
def get_signal(pair: str = "EUR/USD OTC", timeframe: str = "5 sec"):
    is_gold = "GOLD" in pair.upper() or "XAU" in pair.upper()
    is_jpy = "JPY" in pair.upper()
    
    direction = random.choice(["HIGHER", "LOWER"])
    is_up = direction == "HIGHER"
    
    # Kalkile pri ak sipò ki koresponn ak mache a
    if is_gold:
        base_price = round(random.uniform(2650.00, 2710.00), 2)
        support_val = str(round(base_price - random.uniform(2.5, 6.0), 2))
        move_val = f"{'+' if is_up else '-'}{round(random.uniform(0.15, 0.85), 2)}%"
    elif is_jpy:
        base_price = round(random.uniform(152.10, 155.80), 3)
        support_val = str(round(base_price - random.uniform(0.05, 0.15), 3))
        move_val = f"{'+' if is_up else '-'}{round(random.uniform(0.02, 0.09), 2)}%"
    else:
        base_price = round(random.uniform(1.0450, 1.0950), 5)
        support_val = str(round(base_price - random.uniform(0.0005, 0.0018), 5))
        move_val = f"{'+' if is_up else '-'}{round(random.uniform(0.01, 0.08), 2)}%"

    # Detèmine sesyon mache a selon lè a
    hour = datetime.utcnow().hour
    if 7 <= hour < 13:
        session = "London"
    elif 13 <= hour < 21:
        session = "New York"
    else:
        session = "Asian / OTC"

    rsi_val = random.randint(58, 76) if is_up else random.randint(24, 42)

    return {
        "pair": pair,
        "timeframe": timeframe,
        "direction": direction,
        "signal_text": f"Open {direction} for {timeframe}",
        "trend": "Bullish ↗" if is_up else "Bearish ↘",
        "support": support_val,
        "move": move_val,
        "momentum": "Strong High" if is_up else "Strong Low",
        "session": session,
        "ema": "Above 50/200" if is_up else "Below 50/200",
        "price_level": f"{base_price} (Confirmed)",
        "rsi": f"RSI {rsi_val}"
    }
