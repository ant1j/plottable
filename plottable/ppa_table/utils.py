from collections.abc import Callable, Sequence

import pandas as pd


def combine_cols_to_multiline(table, cols: Sequence, mapfn: Callable):
    return table[cols].map(mapfn).sum(axis=1)
    # return table[cols].map(lambda v: apply_colour(v, pick_colour)).sum(axis=1)


def aggregate_columns_to_list(df: pd.DataFrame, columns: Sequence[str]) -> pd.Series:
    return df[columns].apply(lambda row: row.dropna().tolist(), axis=1)
