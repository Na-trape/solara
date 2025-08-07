import requests
import pandas as pd
from datetime import datetime, timezone, timedelta

# Step 1: Fetch 30 days of funding rates from Bybit
def fetch_funding_rates(symbol="SOLUSDT", days=30):
    BASE_URL = "https://api.bybit.com/v5/market/funding/history"
    now = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_time = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp() * 1000)

    params = {
        "category": "linear",  # for USDT perpetuals
        "symbol": symbol,
        "startTime": start_time,
        "endTime": now,
        "limit": 200
    }

    all_rates = []
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
    df = df.sort_values("timestamp")
    return df[["timestamp", "fundingRate"]]

# Step 2: Simulate PnL
def simulate_pnl(df, position_size=100, fee_rate=0.0006, leverage=10):
    pnl = 0
    results = []
    for _, row in df.iterrows():
        funding = row["fundingRate"] * position_size * leverage
        fees = 2 * fee_rate * position_size
        net = funding - fees
        pnl += net
        results.append({
            "timestamp": row["timestamp"],
            "funding_rate": row["fundingRate"],
            "funding_payment": funding,
            "fees": fees,
            "net_pnl": net,
            "cumulative_pnl": pnl
        })
    return pd.DataFrame(results)

# Step 3: Run
if __name__ == "__main__":
    df = fetch_funding_rates()
    pnl_df = simulate_pnl(df)
    print(pnl_df.tail())
    print(f"\n💰 Total simulated PnL: ${pnl_df['cumulative_pnl'].iloc[-1]:.2f}")
