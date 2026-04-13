# metrics.py
# Aggregates raw campaign data into dashboard KPIs


import pandas as pd
from data_generator import generate_weekly_data, generate_pdp_scores


def summary_kpis(df: pd.DataFrame) -> dict:
    """
    Returns the five headline KPIs shown in the dashboard metric cards.
    Period-on-period delta calculated by splitting data into two halves.
    """
    half = len(df) // 2
    current, previous = df.iloc[half:], df.iloc[:half]

    def pct_delta(curr_val, prev_val):
        return round(((curr_val - prev_val) / prev_val) * 100, 1)

    curr_impr  = current["impressions"].sum()
    prev_impr  = previous["impressions"].sum()

    curr_ctr   = (current["clicks"].sum() / curr_impr)
    prev_ctr   = (previous["clicks"].sum() / prev_impr)

    curr_conv  = (current["conversions"].sum() / current["clicks"].sum())
    prev_conv  = (previous["conversions"].sum() / previous["clicks"].sum())

    curr_cpc   = (current["spend_eur"].sum() / current["conversions"].sum())
    prev_cpc   = (previous["spend_eur"].sum() / previous["conversions"].sum())

    curr_roas  = (current["revenue_eur"].sum() / current["spend_eur"].sum())
    prev_roas  = (previous["revenue_eur"].sum() / previous["spend_eur"].sum())

    return {
        "impressions"  : {"value": f"{curr_impr/1e6:.1f}M",  "delta": pct_delta(curr_impr, prev_impr)},
        "ctr"          : {"value": f"{curr_ctr*100:.1f}%",   "delta": pct_delta(curr_ctr,  prev_ctr)},
        "conv_rate"    : {"value": f"{curr_conv*100:.1f}%",  "delta": pct_delta(curr_conv, prev_conv)},
        "cost_per_conv": {"value": f"€{curr_cpc:.2f}",     "delta": pct_delta(curr_cpc,  prev_cpc)},
        "roas"         : {"value": f"{curr_roas:.1f}x",     "delta": pct_delta(curr_roas, prev_roas)},
    }


def channel_attribution(df: pd.DataFrame) -> pd.Series:
    """
    Breaks total spend into channel buckets.
    In production: replace with real UTM / channel column from GA4 export.
    """
    total = df["spend_eur"].sum()
    return pd.Series({
        "Paid search": round(total * 0.42, 2),
        "Display"    : round(total * 0.28, 2),
        "Social"     : round(total * 0.18, 2),
        "Organic"    : round(total * 0.12, 2),
    })


def conversion_funnel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Builds the funnel from impressions → purchase.
    Drop-off rates calibrated to beauty eCommerce benchmarks.
    """
    impr    = df["impressions"].sum()
    clicks  = df["clicks"].sum()
    return pd.DataFrame([
        {"stage": "Impressions",  "users": impr},
        {"stage": "Clicks",       "users": clicks},
        {"stage": "PDP views",    "users": int(clicks * 0.61)},
        {"stage": "Add to cart",  "users": int(clicks * 0.12)},
        {"stage": "Purchase",     "users": df["conversions"].sum()},
    ])


if __name__ == "__main__":
    df   = generate_weekly_data()
    kpis = summary_kpis(df)
    for k, v in kpis.items():
        print(f"{k:<16} {v['value']:>8}   delta: {v['delta']:+.1f}%")
