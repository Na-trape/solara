import pandas as pd
from config import FEE_RATE, SPREAD_SLIPPAGE_RATE, POSITION_SIZE, LEVERAGE, FUNDING_THRESHOLD


def merge_funding_and_price(funding_df, ohlcv_df):
    return pd.merge_asof(
        funding_df.sort_values("timestamp"),
        ohlcv_df.sort_values("timestamp"),
        on="timestamp",
        direction="backward"
    )


def estimate_slippage(row):
    # Estimate dynamic slippage based on candle range
    volatility = (row["high"] - row["low"]) / row["open"]
    slippage = SPREAD_SLIPPAGE_RATE + volatility * 0.2  # scale factor
    return slippage * POSITION_SIZE * row["open"]  # slippage in USDT


def simulate_realistic_pnl(merged_df):
    records = []
    total_funding = 0
    for _, row in merged_df.iterrows():
        rate = row["fundingRate"]
        if rate < FUNDING_THRESHOLD:
            continue

        price = row["open"]
        funding_payment = rate * POSITION_SIZE * LEVERAGE
        fee = 2 * FEE_RATE * POSITION_SIZE * price
        slippage = estimate_slippage(row)
        net = funding_payment - fee - slippage
        total_funding += funding_payment

        records.append({
            "timestamp": row["timestamp"],
            "funding_rate": rate,
            "price": price,
            "funding_payment": funding_payment,
            "fee": fee,
            "slippage": slippage,
            "net_pnl": net,
            "cumulative_pnl": total_funding - fee - slippage
        })

    df = pd.DataFrame(records)
    return df, {
        "final_pnl": df["net_pnl"].sum(),
        "funding_earned": df["funding_payment"].sum(),
        "fees_total": df["fee"].sum(),
        "slippage_total": df["slippage"].sum(),
        "windows_used": len(df),
        "windows_available": len(merged_df)
    }
