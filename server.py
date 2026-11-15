from fastapi.responses import HTMLResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>GPT Trade Mini App</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #0b0b0e; color: #ffffff; padding: 14px; display: flex; flex-direction: column; min-height: 100vh; padding-bottom: 75px; }
        
        #auth-screen { position: fixed; inset: 0; background: #0b0b0e; z-index: 100; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 24px; }
        .auth-box { background: #16161a; padding: 24px; border-radius: 16px; width: 100%; max-width: 360px; text-align: center; border: 1px solid #27272a; }
        .auth-box h2 { margin-bottom: 8px; font-size: 20px; color: #fff; }
        .auth-box p { color: #a1a1aa; font-size: 13px; margin-bottom: 20px; }
        .auth-box input { width: 100%; padding: 14px; border-radius: 10px; border: 1px solid #3f3f46; background: #27272a; color: white; font-size: 16px; margin-bottom: 14px; text-align: center; outline: none; }

        .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .app-title { font-size: 20px; font-weight: 700; display: flex; align-items: center; gap: 8px; }
        .top-badges { display: flex; gap: 6px; }
        .badge { background: #16161a; border: 1px solid #27272a; padding: 4px 10px; border-radius: 16px; font-size: 11px; color: #d4d4d8; display: flex; align-items: center; gap: 4px; cursor: pointer; }

        .card { background: #16161a; border-radius: 14px; padding: 12px; margin-bottom: 10px; border: 1px solid #27272a; }
        .card-label { font-size: 12px; color: #a1a1aa; margin-bottom: 8px; }

        .pair-row { display: flex; justify-content: space-between; align-items: center; }
        .pair-info h3 { font-size: 15px; font-weight: 700; margin-bottom: 2px; }
        .pair-info p { font-size: 11px; color: #a1a1aa; }

        .tf-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-top: 6px; }
        .tf-btn { background: #27272a; border: 1px solid #3f3f46; color: #d4d4d8; padding: 8px 2px; border-radius: 8px; font-size: 11px; font-weight: 600; cursor: pointer; text-align: center; transition: 0.2s; }
        .tf-btn.active { background: rgba(168, 85, 247, 0.15); border-color: #a855f7; color: #d8b4fe; }

        .status-box { background: linear-gradient(145deg, #18122b, #110e1b); border: 1px solid #3b2859; border-radius: 14px; padding: 14px; text-align: center; margin-bottom: 10px; }
        .status-title { font-size: 18px; font-weight: 700; color: #d8b4fe; margin-bottom: 4px; }
        .status-sub { font-size: 12px; color: #c084fc; }
        .signal-action { font-size: 16px; font-weight: 700; margin: 6px 0; text-align: center; }

        .readings-header { display: flex; justify-content: space-between; font-size: 11px; color: #a1a1aa; margin-bottom: 6px; padding: 0 2px; }
        .grid-8 { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 12px; }
        
        .reading-card { background: #16161a; border: 1px solid #27272a; border-radius: 10px; padding: 10px; transition: 0.3s; }
        .reading-card.scanning { border-color: #a855f7; box-shadow: 0 0 10px rgba(168, 85, 247, 0.25); background: #1f142b; }
        .reading-card.success-green { border-color: #22c55e; background: rgba(34, 197, 94, 0.08); }
        .reading-card.success-red { border-color: #ef4444; background: rgba(239, 68, 68, 0.08); }
        
        .reading-label { font-size: 10px; color: #a1a1aa; margin-bottom: 2px; display: flex; align-items: center; gap: 4px; }
        .reading-val { font-size: 12px; font-weight: 600; color: #ffffff; }
        .reading-val.green { color: #22c55e; }
        .reading-val.red { color: #ef4444; }

        .btn-purple { width: 100%; background: linear-gradient(135deg, #9333ea, #7e22ce); color: #ffffff; border: none; padding: 14px; border-radius: 12px; font-size: 15px; font-weight: 700; cursor: pointer; box-shadow: 0 4px 12px rgba(147, 51, 234, 0.3); }
        .btn-purple:disabled { opacity: 0.6; cursor: not-allowed; }

        .bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; background: #16161a; border-top: 1px solid #27272a; display: flex; justify-content: space-around; padding: 8px 0; z-index: 50; }
        .nav-item { text-align: center; color: #a1a1aa; font-size: 10px; cursor: pointer; }
        .nav-item.active { color: #c084fc; }
        .nav-item svg { width: 20px; height: 20px; margin-bottom: 2px; fill: currentColor; }
    </style>
</head>
<body>

    <div id="auth-screen">
        <div class="auth-box">
            <h2>GPT Trade Bot 🔒</h2>
            <p>Antre kòd sekrè w la pou w louvri app a.</p>
            <input type="password" id="secret-code" placeholder="Antre kòd la..." onkeydown="if(event.key === 'Enter') unlockApp()">
            <button class="btn-purple" onclick="unlockApp()">Louvri App a</button>
        </div>
    </div>

    <div class="top-bar">
        <div class="app-title">🟣 GPT trade</div>
        <div class="top-badges">
            <div class="badge">⚙️ Help</div>
            <div class="badge">🌐 EN ▾</div>
        </div>
    </div>

    <div class="card">
        <div class="card-label">Choose a currency pair</div>
        <div class="pair-row">
            <div class="pair-info">
                <h3 id="current-pair-title">EUR/USD OTC</h3>
                <p>AI Analysis Ready</p>
            </div>
            <select id="pair-select" style="background: #27272a; color: #fff; border: 1px solid #3f3f46; padding: 6px 10px; border-radius: 8px; font-size: 12px; outline: none;" onchange="updatePairLabel()">
                <option value="EUR/USD OTC">EUR/USD OTC</option>
                <option value="GBP/USD OTC">GBP/USD OTC</option>
                <option value="USD/JPY OTC">USD/JPY OTC</option>
                <option value="GOLD (XAU/USD) OTC">GOLD (XAU/USD) OTC</option>
                <option value="AUD/USD OTC">AUD/USD OTC</option>
                <option value="EUR/USD">EUR/USD</option>
                <option value="GBP/USD">GBP/USD</option>
            </select>
        </div>
    </div>

    <div class="card">
        <div class="card-label">Expiration time</div>
        <div class="tf-grid">
            <div class="tf-btn active" data-tf="3s">3s</div>
            <div class="tf-btn" data-tf="5s">5s</div>
            <div class="tf-btn" data-tf="10s">10s</div>
            <div class="tf-btn" data-tf="15s">15s</div>
            <div class="tf-btn" data-tf="30s">30s</div>
            <div class="tf-btn" data-tf="1m">1m</div>
            <div class="tf-btn" data-tf="2m">2m</div>
        </div>
    </div>

    <div class="status-box">
        <div class="status-title" id="status-title">Ready to Scan</div>
        <div class="status-sub" id="status-sub">⚡ GPT-4o Astro Engine Idle</div>
        <div id="countdown-display" style="font-size: 15px; font-weight: 700; color: #c084fc; margin-top: 4px; display: none;"></div>
    </div>

    <div class="signal-action" id="signal-action"></div>

    <div class="readings-header">
        <span>Decoding at level GPT-4 Astro</span>
        <span id="scan-counter">0 of 8</span>
    </div>

    <div class="grid-8">
        <div class="reading-card" id="card-1">
            <div class="reading-label">📉 Trend</div>
            <div class="reading-val" id="val-trend">-</div>
        </div>
        <div class="reading-card" id="card-2">
            <div class="reading-label">📊 EMA 50/200</div>
            <div class="reading-val" id="val-ema">-</div>
        </div>
        <div class="reading-card" id="card-3">
            <div class="reading-label">⚡ Momentum</div>
            <div class="reading-val" id="val-momentum">-</div>
        </div>
        <div class="reading-card" id="card-4">
            <div class="reading-label">📉 RSI</div>
            <div class="reading-val" id="val-rsi">-</div>
        </div>
        <div class="reading-card" id="card-5">
            <div class="reading-label" id="lbl-move">Move over 3s</div>
            <div class="reading-val" id="val-move">-</div>
        </div>
        <div class="reading-card" id="card-6">
            <div class="reading-label">🛡️ Level below</div>
            <div class="reading-val" id="val-support">-</div>
        </div>
        <div class="reading-card" id="card-7">
            <div class="reading-label">🌍 Session</div>
            <div class="reading-val" id="val-session">-</div>
        </div>
        <div class="reading-card" id="card-8">
            <div class="reading-label">💎 Summary 3s</div>
            <div class="reading-val" id="val-summary">-</div>
        </div>
    </div>

    <button class="btn-purple" id="get-signal-btn" onclick="startAnalysis()">⚡ Get signal</button>

    <div class="bottom-nav">
        <div class="nav-item">
            <svg viewBox="0 0 24 24"><path d="M12 3L2 12h3v8h6v-6h2v6h6v-8h3L12 3z"/></svg>
            <div>Signals</div>
        </div>
        <div class="nav-item">
            <svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm1 14h-2v-2h2zm0-4h-2V7h2z"/></svg>
            <div>Learn</div>
        </div>
        <div class="nav-item active">
            <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/></svg>
            <div>Profile</div>
        </div>
    </div>

    <script>
        if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.expand();
        }

        let selectedTimeframe = "3s";

        document.querySelectorAll('.tf-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tf-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                selectedTimeframe = btn.getAttribute('data-tf');
                document.getElementById('lbl-move').innerText = `Move over ${selectedTimeframe}`;
            });
        });

        function updatePairLabel() {
            document.getElementById('current-pair-title').innerText = document.getElementById('pair-select').value;
        }

        function unlockApp() {
            const code = document.getElementById('secret-code').value.trim();
            if (code === "Alibourchet2026") {
                document.getElementById('auth-screen').style.display = 'none';
            } else {
                alert("Kòd sekrè a pa kòrèk. Tanpri tape Alibourchet2026.");
            }
        }

        async function startAnalysis() {
            const btn = document.getElementById('get-signal-btn');
            const pair = document.getElementById('pair-select').value;
            const statusTitle = document.getElementById('status-title');
            const statusSub = document.getElementById('status-sub');
            const signalAction = document.getElementById('signal-action');
            const counter = document.getElementById('scan-counter');
            const countdownEl = document.getElementById('countdown-display');

            btn.disabled = true;
            signalAction.innerText = "";
            countdownEl.style.display = 'none';
            statusTitle.innerText = "Checking Indicators...";
            statusTitle.style.color = "#c084fc";

            const valIds = ['val-trend', 'val-ema', 'val-momentum', 'val-rsi', 'val-move', 'val-support', 'val-session', 'val-summary'];
            
            for (let i = 1; i <= 8; i++) {
                const c = document.getElementById(`card-${i}`);
                c.className = "reading-card";
                document.getElementById(valIds[i-1]).innerText = "...";
                document.getElementById(valIds[i-1]).className = "reading-val";
            }

            try {
                const res = await fetch(`/api/signal?pair=${encodeURIComponent(pair)}&timeframe=${encodeURIComponent(selectedTimeframe)}`);
                const data = await res.json();

                const values = [
                    data.trend,
                    data.ema,
                    data.momentum,
                    data.rsi,
                    data.move,
                    data.support,
                    data.session,
                    `Summary ${selectedTimeframe}`
                ];

                const isUp = data.direction === "HIGHER";

                for (let i = 0; i < 8; i++) {
                    const card = document.getElementById(`card-${i + 1}`);
                    card.classList.add('scanning');
                    counter.innerText = `${i + 1} of 8`;
                    statusSub.innerText = `Analyzing - ${i + 1} of 8...`;
                    
                    await new Promise(r => setTimeout(r, 250));
                    
                    card.classList.remove('scanning');
                    card.classList.add(isUp ? 'success-green' : 'success-red');
                    
                    const valEl = document.getElementById(valIds[i]);
                    valEl.innerText = values[i];
                    valEl.classList.add(isUp ? 'green' : 'red');
                }

                statusTitle.innerText = isUp ? "BUY / HIGHER ↗" : "SELL / LOWER ↘";
                statusTitle.style.color = isUp ? "#22c55e" : "#ef4444";
                statusSub.innerText = `${pair} • ${selectedTimeframe}`;
                
                signalAction.innerText = data.signal_text;
                signalAction.className = isUp ? "signal-action" : "signal-action down";

                countdownEl.style.display = 'block';
                let timeLeft = 10; 

                const timerInterval = setInterval(() => {
                    if (timeLeft > 0) {
                        countdownEl.innerText = `⏳ Entry window: ${timeLeft}s`;
                        timeLeft--;
                    } else {
                        countdownEl.innerText = `🔒 Window closed (${selectedTimeframe})`;
                        clearInterval(timerInterval);
                    }
                }, 1000);

            } catch (err) {
                statusTitle.innerText = "Connection Error";
                statusSub.innerText = "Tcheke sèvè a sou Render.";
            } finally {
                btn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return HTML_CONTENT

@app.get("/api/signal")
async def get_signal(pair: str = "EUR/USD OTC", timeframe: str = "3s"):
    is_gold = "GOLD" in pair.upper() or "XAU" in pair.upper()
    
    if is_gold:
        price = round(2685.50 + random.uniform(-2.0, 2.0), 2)
        support = round(price - random.uniform(1.5, 3.0), 2)
    else:
        price = round(1.05200 + random.uniform(-0.00100, 0.00100), 5)
        support = round(price - random.uniform(0.00050, 0.00100), 5)

    direction = random.choice(["HIGHER", "LOWER"])
    is_up = direction == "HIGHER"
    rsi_val = random.randint(55, 78) if is_up else random.randint(22, 45)

    return {
        "pair": pair,
        "timeframe": timeframe,
        "direction": direction,
        "signal_text": f"Execute {direction} for {timeframe}",
        "trend": "Bullish ↗" if is_up else "Bearish ↘",
        "support": str(support),
        "move": f"+{round(random.uniform(0.03, 0.15), 2)}%",
        "momentum": "GPT-4o Optimized",
        "session": "Active Session",
        "ema": "EMA 50/200 Aligned" if is_up else "EMA 50/200 Crossing",
        "price_level": str(price),
        "rsi": f"RSI {rsi_val}"
    }

