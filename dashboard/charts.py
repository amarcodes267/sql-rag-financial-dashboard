import pandas as pd
import plotly.express as px


def revenue_chart(data):

    df = pd.DataFrame(data)

    if df.empty:
        return None

    return px.line(
        df,
        x="year",
        y="revenue",
        markers=True,
        title="Revenue Trend"
    )


def profit_chart(data):

    df = pd.DataFrame(data)

    if df.empty:
        return None

    return px.bar(
        df,
        x="year",
        y="net_income",
        title="Net Income"
    )


def assets_liabilities_chart(data):

    df = pd.DataFrame(data)

    if df.empty:
        return None

    chart_data = df[
        [
            "year",
            "total_assets",
            "total_liabilities"
        ]
    ]

    chart_data = chart_data.melt(
        id_vars=["year"],
        var_name="metric",
        value_name="value"
    )

    return px.bar(
        chart_data,
        x="year",
        y="value",
        color="metric",
        barmode="group",
        title="Assets vs Liabilities"
    )