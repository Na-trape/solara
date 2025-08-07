from bybit_client import fetch_funding_rates
from simulator import simulate_pnl
from config import POSITION_SIZE, FEE_RATE, LEVERAGE

if __name__ == "__main__":
    df = fetch_funding_rates("SOLUSDT", days=30)
    result_df, pnl = simulate_pnl(df, POSITION_SIZE, FEE_RATE, LEVERAGE)

    print(result_df.tail())
    print(f"\n💰 Total simulated PnL: ${pnl:.2f}")
