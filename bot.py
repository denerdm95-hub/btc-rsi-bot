import requests
import time
import pandas as pd
import numpy as np

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
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=200"
    data = requests.get(url).json()
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
    try:
        closes = get_klines()
        rsi = calculate_rsi(closes, rsi_period)

        print("RSI atual:", rsi)

        levels = [25, 30, 70, 75]

        for level in levels:
            if round(rsi) == level and last_alert != level:
                send_telegram_message(f"🚨 BTCUSDT atingiu RSI {level} no 4H!\nRSI atual: {round(rsi,2)}")
                last_alert = level

        time.sleep(60)

    except Exception as e:
        print("Erro:", e)
        time.sleep(60)