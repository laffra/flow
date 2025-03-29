"""
Copyright (c) 2024 laffra - All Rights Reserved. 
"""

# pylint: disable=import-outside-toplevel
# pylint: disable=invalid-name

import pandas
import matplotlib.pyplot

packages = ["pandas", "matplotlib", "plotly" ]


def dataframe_plot(dataframe: pandas.DataFrame) -> matplotlib.pyplot.Figure:
    """
    Pandas Dataframe => Plot
    """
    return dataframe.plot()


def df_candlestick(dataframe: pandas.DataFrame) -> matplotlib.pyplot.Figure:
    """
    Pandas Dataframe => Plot
    """
    import plotly

    chart = plotly.graph_objects.Candlestick(
        x=dataframe['date'],
        open=dataframe['open'],
        high=dataframe['high'],
        low=dataframe['low'],
        close=dataframe['close']
    )
    return plotly.graph_objects.Figure(data=[chart])
