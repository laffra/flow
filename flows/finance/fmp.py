"""
Copyright (c) 2024 laffra - All Rights Reserved. 
"""

# pylint: disable=import-outside-toplevel
# pylint: disable=redefined-outer-name
# pylint: disable=reimported

import os

import pandas

packages = [ "fmpsdk", "plotly" ]
secrets = [
    (
        "FMPSDK",
        "This node uses Financial Modeling Prep (FMP). " \
            "Please enter your FMP API key.",
        "https://site.financialmodelingprep.com/developer/docs/dashboard",
    ),
]

def quote(
        symbol:str = ""
    ) -> dict:
    """ Return a quote for the given symbol """
    import fmpsdk

    return fmpsdk.quote(os.environ["FMPSDK"], symbol)


def history(
        symbol:str = "",
        from_date: str = "",
        to_date: str = ""
    ) -> pandas.DataFrame:
    """ Return historical prices for the given symbol """
    import fmpsdk
    import pandas

    return pandas.DataFrame(fmpsdk.historical_price_full(
        os.environ["FMPSDK"],
        symbol,
        from_date,
        to_date
    ))
