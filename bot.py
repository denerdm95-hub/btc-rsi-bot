
import requests
import time
import pandas as pd
import numpy as np

print("BOT INICIADO", flush=True)

# CONFIGURAÇÕES
TOKEN = "8772767472:AAGnnI0tiiHRCnWZvJQHadi8bXtNy64JPgU"
CHAT_ID = "8729665942"

symbol = "BTCUSDT"
interval = "4h"
rsi_period = 14

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)

def get_klines():
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": "symbol",
        "interval": interval,
        "limit": 100
    }

    response = requests.get(url, params=params)
    data = response.json()

    if not data or len(data) == 0:
        print("⚠ Binance retornou vazio", flush=True)
        return []

    closes = [float(candle[4]) for candle in data]
    return closes
def calculate_rsi(closes, period=14):
    delta = np.diff(closes)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(period).mean()
    avg_loss = pd.Series(loss).rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]

last_alert = None

while True:
    print("LOOP ATIVO", flush=True)

    try:
        closes = get_klines()

        # proteção 1
        if not closes:
            print("Sem dados da Binance", flush=True)
            time.sleep(60)
            continue

        # proteção 2
        if len(closes) < rsi_period:
            print("Dados insuficientes para RSI", flush=True)
            time.sleep(60)
            continue

        rsi = calculate_rsi(closes, rsi_period)

        # proteção 3
        if pd.isna(rsi):
            print("RSI ainda não calculável", flush=True)
            time.sleep(60)
            continue

        print("RSI atual:", rsi, flush=True)

        levels = [25, 30, 70, 75]

        for level in levels:
            if round(rsi) == level and last_alert != level:
                send_telegram_message(
                    f"🚨 BTCUSDT atingiu RSI {level} no {interval}!\nRSI atual: {round(rsi,2)}"
                )
                last_alert = level

        time.sleep(60)

    except Exception as e:
        print("Erro:", e, flush=True)
        time.sleep(60)