import pandas as pd


def calculate_metrics(data):

    if not data:
        return {
            "revenue": 0,
            "profit": 0,
            "assets": 0,
            "growth": 0
        }

    df = pd.DataFrame(data)

    df = df.sort_values("year")

    latest = df.iloc[-1]

    revenue = latest["revenue"] or 0

    profit = latest["net_income"] or 0

    assets = latest["total_assets"] or 0

    growth = 0

    if len(df) >= 2:

        previous = df.iloc[-2]["revenue"]

        if previous:
            growth = (
                (revenue - previous)
                / previous
            ) * 100

    return {
        "revenue": revenue,
        "profit": profit,
        "assets": assets,
        "growth": growth
    }