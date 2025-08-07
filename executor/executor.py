import ccxt
from config import API_KEY, API_SECRET, POSITION_SIZE, FUNDING_THRESHOLD


def get_authenticated_client():
    return ccxt.bybit({
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'swap',  # for USDT perpetuals
        }
    })


def fetch_current_funding(symbol="SOL/USDT:USDT"):
    client = get_authenticated_client()
    market = client.fetch_funding_rate(symbol)
    return market['fundingRate']


def enter_hedged_position(amount=1):
    client = get_authenticated_client()

    # Short perpetual (SOLUSDT perpetual)
    perp_symbol = "SOL/USDT:USDT"
    short_order = client.create_market_sell_order(perp_symbol, amount)
    print("[EXECUTOR] Opened SHORT perp:", short_order['id'])

    # Long spot (SOL/USDT)
    spot_symbol = "SOL/USDT"
    long_order = client.create_market_buy_order(spot_symbol, amount)
    print("[EXECUTOR] Opened LONG spot:", long_order['id'])

    return {
        "short_perp_order": short_order,
        "long_spot_order": long_order,
    }


def run_executor():
    print("[EXECUTOR] Checking funding rate...")

    try:
        funding_rate = fetch_current_funding()
        print(f"[EXECUTOR] Current funding rate: {funding_rate:.6f}")

        if funding_rate >= FUNDING_THRESHOLD:
            print(f"[EXECUTOR] ✅ Funding rate is {funding_rate:.6f}, above threshold {FUNDING_THRESHOLD}.")
            print(f"[EXECUTOR] 🔐 Entering hedged position with size: {POSITION_SIZE} SOL")

            # Confirm user before placing trade
            confirm = input("⚠️ Type 'YES' to confirm execution: ").strip().upper()
            if confirm == "YES":
                orders = enter_hedged_position(POSITION_SIZE)
                print("[EXECUTOR] ✅ Hedge executed successfully.")
            else:
                print("[EXECUTOR] ❌ Cancelled by user.")

        else:
            print(f"[EXECUTOR] ❌ Funding rate {funding_rate:.6f} is below threshold. Doing nothing.")

    except Exception as e:
        print("[EXECUTOR] ❌ Error:", str(e))

