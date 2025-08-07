from bybit_client import fetch_funding_rates, fetch_ohlcv
from simulator import merge_funding_and_price, simulate_realistic_pnl

if __name__ == "__main__":
    print("[MAIN] Fetching funding data...")
    funding_df = fetch_funding_rates()

    print("[MAIN] Fetching OHLCV data...")
    ohlcv_df = fetch_ohlcv()

    print("[MAIN] Merging data...")
    merged_df = merge_funding_and_price(funding_df, ohlcv_df)

    print("[MAIN] Simulating PnL...")
    pnl_df, summary = simulate_realistic_pnl(merged_df)

    print(pnl_df.tail())
    print("\n📊 PnL Breakdown:")
    for k, v in summary.items():
        print(f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}")
