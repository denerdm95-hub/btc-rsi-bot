import requests
import time
import pandas as pd
import numpy as np

print("BOT INICIADO", flush=True)

# CONFIGURAÇÕES
TOKEN = "SEU_TOKEN_AQUI"
CHAT_ID = "SEU_CHAT_ID_AQUI"

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
        "symbol": symbol,  # CORRIGIDO AQUI
        "interval": interval,
        "limit": 100
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Se Binance retornar erro
    if not isinstance(data, list):
        print("Erro na API:", data, flush=True)
        return []

    closes = []
    for candle in data:
        if isinstance(candle, list) and len(candle) > 4:
            closes.append(float(candle[4]))

    return closes


def calculate_rsi(closes, period=14):
    if len(closes) < period:
        return None

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
        print("LOOP ATIVO", flush=True)

        closes = get_klines()

        if not closes:
            time.sleep(60)
            continue

        rsi = calculate_rsi(closes, rsi_period)

        if rsi is None:
            time.sleep(60)
            continue

        print("RSI atual:", round(rsi, 2), flush=True)

        levels = [25, 30, 70, 75]

        for level in levels:
            if round(rsi) == level and last_alert != level:
                send_telegram_message(
                    f"🚨 BTCUSDT atingiu RSI {level} no {interval}!\nRSI atual: {round(rsi, 2)}"
                )
                last_alert = level

        time.sleep(60)

    except Exception as e:
        print("Erro:", e, flush=True)
        time.sleep(60)