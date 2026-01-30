import os
import requests
import yfinance as yf
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

assets = [
    ("SPY", "S&P 500"),
    ("QQQ", "Nasdaq"),
    ("GLD", "Gold"),
    ("CL=F", "WTI Oil"),
    ("BTC-USD", "Bitcoin"),
    ("ETH-USD", "Ethereum"),
]

def get_change(symbol):
    data = yf.download(
        symbol,
        period="2d",
        interval="1h",
        progress=False
    )

    if len(data) < 2:
        return None

    now_price = data["Close"].iloc[-1]
    yesterday_close = data["Close"].iloc[0]
    today_open = data["Open"].iloc[-24] if len(data) >= 24 else data["Open"].iloc[0]

    pct_from_yesterday = (now_price - yesterday_close) / yesterday_close * 100
    pct_today = (now_price - today_open) / today_open * 100

    return now_price, pct_from_yesterday, pct_today

results = []
for symbol, name in assets:
    res = get_change(symbol)
    if res:
        price, pct_y, pct_t = res
        emoji = "📈" if pct_y > 0 else "📉"
        results.append(
            f"{emoji} {name}: {price:.2f}\n"
            f"   เทียบเมื่อวาน: {pct_y:+.2f}%\n"
            f"   วันนี้: {pct_t:+.2f}%"
        )

now = datetime.now().strftime("%d/%m/%Y %H:%M")

message = f"⏰ Market Hourly Report ({now})\n\n"
for r in results:
    message += r + "\n\n"

# ส่ง Telegram
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
requests.post(
    url,
    data={"chat_id": CHAT_ID, "text": message}
)
