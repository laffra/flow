"""
Copyright (c) 2024 laffra - All Rights Reserved. 
"""

# pylint: disable=import-outside-toplevel
# pylint: disable=invalid-name

import pandas
import matplotlib.pyplot

packages = ["pandas", "matplotlib", "plotly" ]


def df_plot(df: pandas.DataFrame) -> matplotlib.pyplot.Figure:
    """
    Pandas Dataframe => Plot
    """
    return df.plot()


def df_candlestick(df: pandas.DataFrame) -> matplotlib.pyplot.Figure:
    """
    Pandas Dataframe => Plot
    """
    import plotly

    chart = plotly.graph_objects.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close']
    )
    return plotly.graph_objects.Figure(data=[chart])
