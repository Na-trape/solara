import pandas as pd

def simulate_pnl(df, position_size=100, fee_rate=0.0006, leverage=10, slippage_rate=0.0002, min_funding=0.0001):
    funding_total = 0
    accepted_fundings = []
    
    for _, row in df.iterrows():
        rate = row["fundingRate"]

        # Only include positive funding (shorting perp, receiving payment)
        if rate >= min_funding:
            funding_payment = rate * position_size * leverage
            funding_total += funding_payment

            accepted_fundings.append({
                "timestamp": row["timestamp"],
                "funding_rate": rate,
                "funding_payment": funding_payment
            })

    funding_df = pd.DataFrame(accepted_fundings)

    # Fees: 2x entry/exit taker fees
    trading_fees = 2 * fee_rate * position_size

    # Slippage/spread loss: 2x side entry/exit
    slippage = 2 * slippage_rate * position_size

    # Final PnL
    pnl = funding_total - trading_fees - slippage

    return funding_df, pnl, {
        "funding_total": funding_total,
        "fees": trading_fees,
        "slippage": slippage,
        "net_pnl": pnl,
        "windows_earned": len(funding_df),
        "total_windows": len(df)
    }
