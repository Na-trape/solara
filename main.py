from bybit_client import fetch_funding_rates
from simulator import simulate_pnl
from config import POSITION_SIZE, FEE_RATE, LEVERAGE, SPREAD_SLIPPAGE_RATE, FUNDING_THRESHOLD


if __name__ == "__main__":
    df = fetch_funding_rates("SOLUSDT", days=30)

    result_df, pnl, summary = simulate_pnl(
        df,
        position_size=POSITION_SIZE,
        fee_rate=FEE_RATE,
        leverage=LEVERAGE,
        slippage_rate=SPREAD_SLIPPAGE_RATE,
        min_funding=FUNDING_THRESHOLD
    )

    print(result_df.tail())
    print("\n📊 PnL Breakdown:")
    for k, v in summary.items():
        print(f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}")

