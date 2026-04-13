# data_generator.py
# Generates Digital Shelf campaign + PDP data for the Coty dashboard


import pandas as pd
import numpy as np
from datetime import date, timedelta

# ── Campaign seed data ────────────────────────────────────────────

CAMPAIGNS = [
    {"name": "Fragrance — Glow",   "base_ctr": 0.072, "base_conv": 0.041, "daily_budget": 320},
    {"name": "Foundation — Match", "base_ctr": 0.058, "base_conv": 0.036, "daily_budget": 280},
    {"name": "Mascara — Lash",    "base_ctr": 0.064, "base_conv": 0.032, "daily_budget": 210},
    {"name": "Lip — Velvet",      "base_ctr": 0.049, "base_conv": 0.028, "daily_budget": 160},
    {"name": "Nail Color",        "base_ctr": 0.031, "base_conv": 0.019, "daily_budget": 90 },
]

def generate_weekly_data(weeks: int = 8) -> pd.DataFrame:
    """
    Simulates 8 weeks of campaign performance with realistic
    week-on-week improvement — mirrors Google Ads optimisation
    done at Kaashiv Infotech internship.
    """
    np.random.seed(42)
    rows = []
    start = date.today() - timedelta(weeks=weeks)

    for w in range(weeks):
        week_start = start + timedelta(weeks=w)
        improvement = 1 + (w * 0.025)  # 2.5% weekly optimisation lift

        for camp in CAMPAIGNS:
            impressions = int(
                np.random.normal(50_000, 4_000) * improvement
            )
            ctr        = camp["base_ctr"] * improvement * np.random.uniform(0.95, 1.05)
            clicks     = int(impressions * ctr)
            conv_rate  = camp["base_conv"] * improvement * np.random.uniform(0.93, 1.07)
            conversions = int(clicks * conv_rate)
            spend      = camp["daily_budget"] * 7 * np.random.uniform(0.9, 1.0)
            revenue    = conversions * np.random.uniform(28, 55)

            rows.append({
                "week_start"   : week_start.isoformat(),
                "campaign"     : camp["name"],
                "impressions"  : impressions,
                "clicks"       : clicks,
                "ctr"          : round(ctr, 4),
                "conversions"  : conversions,
                "conv_rate"    : round(conv_rate, 4),
                "spend_eur"    : round(spend, 2),
                "revenue_eur"  : round(revenue, 2),
            })

    df = pd.DataFrame(rows)
    df["roas"]           = (df["revenue_eur"] / df["spend_eur"]).round(2)
    df["cost_per_conv"]  = (df["spend_eur"]   / df["conversions"].replace(0, np.nan)).round(2)
    return df


def generate_pdp_scores() -> pd.DataFrame:
    """
    PDP content completeness tracker — mirrors the content audit
    and data validation work from Gateway Software internship.
    """
    pdp_data = [
        {"sku": "Fragrance Glow 50ml", "title_ok": True,  "images": 6, "aplus": "live",  "rating": 4.7},
        {"sku": "Foundation Match 30ml","title_ok": True,  "images": 5, "aplus": "live",  "rating": 4.5},
        {"sku": "Mascara Lash Boost",   "title_ok": False, "images": 4, "aplus": "draft", "rating": 4.2},
        {"sku": "Lip Velvet 01",        "title_ok": False, "images": 3, "aplus": "missing","rating": 3.9},
        {"sku": "Nail Color 12",        "title_ok": False, "images": 2, "aplus": "missing","rating": 3.4},
    ]
    df = pd.DataFrame(pdp_data)
    df["content_score"] = (
        df["title_ok"].astype(int) * 20
        + (df["images"] / 6) * 30
        + df["aplus"].map({"live": 30, "draft": 15, "missing": 0})
        + (df["rating"] / 5) * 20
    ).round(1)
    return df


if __name__ == "__main__":
    weekly = generate_weekly_data()
    pdp    = generate_pdp_scores()
    print(weekly.tail())
    print(pdp)
