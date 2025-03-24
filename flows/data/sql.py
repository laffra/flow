"""
Copyright (c) 2024 laffra - All Rights Reserved. 
"""

# pylint: disable=import-outside-toplevel
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=reimported

import pandas
import duckdb

packages = ["duckdb", "pandas", "fsspec"]


def query() -> duckdb.sql:
    """
    A SQL query for DuckDB.
    """
    return "SELECT * FROM table"


def csv_table(csv: bytes) -> duckdb.table:
    """ CSV => DuckDB """
    import duckdb
    return duckdb.read_csv(csv)


def table_df(table: duckdb.table) -> pandas.DataFrame:
    """ DuckDB -> Dataframe """
    return table.df()
