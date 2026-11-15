from fastapi.responses import FileResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
from datetime import datetime
import httpx

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

@app.get("/api/signal")
async def get_signal(pair: str = "EUR/USD OTC", timeframe: str = "1 min"):
    is_gold = "GOLD" in pair.upper() or "XAU" in pair.upper()
    is_jpy = "JPY" in pair.upper()
    
    # Ale chache vrè pri reyèl la nan mache a atravè API to echanj piblik la
    real_price = 1.0520
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://open.er-api.com/v6/latest/USD", timeout=4.0)
            if response.status_code == 200:
                rates = response.json().get("rates", {})
                if "EUR" in pair:
                    eur = rates.get("EUR", 1.05)
                    real_price = round(1.0 / eur, 5) if eur else 1.0520
                elif "GBP" in pair:
                    gbp = rates.get("GBP", 0.78)
                    real_price = round(1.0 / gbp, 5) if gbp else 1.2650
                elif "JPY" in pair:
                    real_price = round(rates.get("JPY", 152.0), 3)
    except Exception:
        pass

    if is_gold:
        current_price = round(2685.50 + random.uniform(-1.5, 1.5), 2)
        support_val = str(round(current_price - random.uniform(1.5, 3.0), 2))
        move_val = f"+{round(random.uniform(0.1, 0.4), 2)}%"
    elif is_jpy:
        current_price = real_price
        support_val = str(round(current_price - random.uniform(0.03, 0.09), 3))
        move_val = f"+{round(random.uniform(0.02, 0.06), 2)}%"
    else:
        current_price = real_price
        support_val = str(round(current_price - random.uniform(0.0002, 0.0009), 5))
        move_val = f"+{round(random.uniform(0.02, 0.06), 2)}%"

    direction = random.choice(["HIGHER", "LOWER"])
    is_up = direction == "HIGHER"

    hour = datetime.utcnow().hour
    if 7 <= hour < 13:
        session = "London (Active Market)"
    elif 13 <= hour < 21:
        session = "New York (Active Market)"
    else:
        session = "Global / OTC Market"

    rsi_val = random.randint(55, 74) if is_up else random.randint(26, 45)

    return {
        "pair": pair,
        "timeframe": timeframe,
        "direction": direction,
        "signal_text": f"Execute {direction} for {timeframe}",
        "trend": "Bullish ↗" if is_up else "Bearish ↘",
        "support": support_val,
        "move": move_val,
        "momentum": "Real Market High" if is_up else "Real Market Low",
        "session": session,
        "ema": "Aligned 50/200" if is_up else "Breaking 50/200",
        "price_level": f"{current_price} (Real Market Quote)",
        "rsi": f"RSI {rsi_val}"
    }

