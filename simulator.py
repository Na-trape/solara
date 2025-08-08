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
    funding_total = 0
    usable_rows = []

    for _, row in merged_df.iterrows():
        rate = row["fundingRate"]
        if rate >= FUNDING_THRESHOLD:
            funding_payment = rate * POSITION_SIZE * LEVERAGE
            funding_total += funding_payment
            usable_rows.append({
                "timestamp": row["timestamp"],
                "funding_rate": rate,
                "price": row["open"],
                "funding_payment": funding_payment
            })

    if not usable_rows:
        return pd.DataFrame(), {
            "final_pnl": 0,
            "funding_earned": 0,
            "fees_total": 0,
            "slippage_total": 0,
            "windows_used": 0,
            "windows_available": len(merged_df)
        }

    # Estimate average price + slippage from first row only
    first = usable_rows[0]
    entry_price = first["price"]
    slippage = SPREAD_SLIPPAGE_RATE * 2 * POSITION_SIZE * entry_price  # once in, once out
    fees = 2 * FEE_RATE * POSITION_SIZE * entry_price

    final_pnl = funding_total - slippage - fees

    df = pd.DataFrame(usable_rows)
    df["cumulative_funding"] = df["funding_payment"].cumsum()
    df["cumulative_pnl"] = df["cumulative_funding"] - slippage - fees

    return df, {
        "final_pnl": final_pnl,
        "funding_earned": funding_total,
        "fees_total": fees,
        "slippage_total": slippage,
        "windows_used": len(df),
        "windows_available": len(merged_df)
    }
