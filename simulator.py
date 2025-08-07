import pandas as pd

def simulate_pnl(df, position_size=100, fee_rate=0.0006, leverage=10):
    funding_total = 0
    records = []

    for _, row in df.iterrows():
        rate = row["fundingRate"]
        funding_payment = rate * position_size * leverage
        funding_total += funding_payment
        records.append({
            "timestamp": row["timestamp"],
            "funding_rate": rate,
            "funding_payment": funding_payment,
            "cumulative_funding": funding_total
        })

    # Apply entry+exit fee once
    fees = 2 * fee_rate * position_size
    pnl = funding_total - fees

    return pd.DataFrame(records), pnl
