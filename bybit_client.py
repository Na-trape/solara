import ccxt
import pandas as pd
from datetime import datetime, timezone, timedelta
import requests



def fetch_funding_rates(symbol="SOLUSDT", days=30):
    BASE_URL = "https://api.bybit.com/v5/market/funding/history"
    now = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_time = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp() * 1000)

    all_rates = []
    params = {
        "category": "linear",
        "symbol": symbol,
        "startTime": start_time,
        "endTime": now,
        "limit": 200
    }

    while True:
        res = requests.get(BASE_URL, params=params)
        data = res.json()
        if data["retCode"] != 0:
            raise Exception(f"Bybit error: {data['retMsg']}")
        rows = data["result"]["list"]
        if not rows:
            break
        all_rates.extend(rows)
        last_time = int(rows[-1]["fundingRateTimestamp"])
        if last_time >= now:
            break
        params["startTime"] = last_time + 1

    df = pd.DataFrame(all_rates)
    df["timestamp"] = pd.to_datetime(df["fundingRateTimestamp"].astype(int), unit="ms")
    df["fundingRate"] = df["fundingRate"].astype(float)
    return df[["timestamp", "fundingRate"]].sort_values("timestamp")


def fetch_ohlcv(symbol="SOL/USDT", since_days=30):
    exchange = ccxt.bybit()
    since = exchange.milliseconds() - since_days * 24 * 60 * 60 * 1000
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe="1h", since=since)
    
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    
    # Resample to 8h candles
    df.set_index("timestamp", inplace=True)
    df_8h = df.resample("8H").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum"
    }).dropna().reset_index()

    return df_8h
