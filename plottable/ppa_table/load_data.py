"""
This should not be here, but it is for convinience

TODO Remove once we are OK (the kind of things that never happens in real life)
"""

import pickle
from pathlib import Path

import pandas as pd


def load_data_from_files(region, market, tabs) -> dict:
    region_data = _read_data(path=region, tab=tabs["recruitment"], skiprows=1)
    market_data = _read_data(path=market, tab=tabs["recruitment"], skiprows=1)

    label_mapping = (
        _read_data(
            path=market,
            tab=tabs["labels_mappings"],
            skiprows=1,
            usecols=[6, 7],
            header=None,
            names=["micro_categorie", "chart"],
        )
        .dropna()
        .drop_duplicates(subset="micro_categorie", keep="first")
        .set_index("micro_categorie")
        .squeeze()
    )

    return {
        "region": region_data,
        "market": market_data,
        "label_mapping": label_mapping,
    }


def get_from_cache_or_load(path: Path, region, market, tabs):
    if path.exists():
        print("Loading data from cached pickle")
        data = pd.read_pickle(path)
    else:
        print("Loading data from excel files")
        data = load_data_from_files(region=region, market=market, tabs=tabs)
        with open(path, "wb") as f:
            pickle.dump(data, f)

    return data


def _read_data(path, tab, **kwargs) -> pd.DataFrame:
    return (
        pd.read_excel(path, sheet_name=tab, **kwargs).replace(",", pd.NA)
        # .pipe(col_types_on_substr, col_types=SUBSTR_TYPES)
    )
