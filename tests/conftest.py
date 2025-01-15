import functools

import numpy as np
import pandas as pd
import pytest

from plottable.cell import Cell, SubplotCell, TableCell, TextCell
from plottable.plots import percentile_bars
from plottable.table import Table


@pytest.fixture
def default_cell() -> Cell:
    return Cell(xy=(0, 0))


@pytest.fixture
def custom_cell() -> Cell:
    return Cell(xy=(1, 2), width=3, height=4)


@pytest.fixture
def table_cell() -> TableCell:
    return TableCell(
        xy=(1, 2), content="String Content", row_idx=1, col_idx=2, width=3, height=4
    )


@pytest.fixture
def text_cell() -> TextCell:
    return TextCell(
        xy=(1, 2), content="String Content", row_idx=1, col_idx=2, width=3, height=4
    )


@pytest.fixture
def subplot_cell() -> SubplotCell:
    return SubplotCell(
        xy=(0, 0),
        content=60,
        row_idx=0,
        col_idx=0,
        plot_fn=percentile_bars,
        width=2,
        height=1,
    )


@pytest.fixture
def df() -> pd.DataFrame:
    return pd.DataFrame(np.random.random((5, 5)), columns=["A", "B", "C", "D", "E"])


@pytest.fixture
def table(df) -> Table:
    return Table(df)


# https://github.com/yamti1/pytest-nice-parametrize/blob/master/nice_parametrize.py
def parametrize(parameters, arguments_dict, **kwargs):
    """
    A nicer pytest parametrization decorator
    :param parameters: A list of parameter names that will be parametrized
    :param arguments_dict: A dict that maps between the ID of an argument list to the list itself
    :param kwargs: Additional keyword arguments to be passed to pytest.parametrize
    """

    def wrapper(func):
        @functools.wraps(func)
        @pytest.mark.parametrize(
            parameters,
            list(arguments_dict.values()),
            ids=list(arguments_dict.keys()),
            **kwargs,
        )
        def wrapped(*func_args, **func_kwargs):
            return func(*func_args, **func_kwargs)

        return wrapped

    return wrapper
