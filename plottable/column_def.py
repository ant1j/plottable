from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List

import pandas as pd
from matplotlib.colors import LinearSegmentedColormap


class ColumnType(Enum):
    """The Column Type.

    Column Types are:
        STRING = "string"
        SUBPLOT = "subplot"
    """

    STRING = "string"
    SUBPLOT = "subplot"
    HIGHLIGHTTEXT = "highlighttext"
    FLEXITEXT = "flexitext"
    RICHTEXT = "richtext"


def _filter_none_values(d: Dict[str, Any]) -> Dict[str, Any]:
    """Filters out keys with None values from a dictionary.

    Args:
        d (Dict[str, Any]): Dictionary

    Returns:
        Dict[str, Any]: Dictionary without None valued values.
    """
    return {k: v for k, v in d.items() if v is not None}


@dataclass
class ColumnDefinition:
    """A Class defining attributes for a table column.

    Args:
        name: str:
            the column name
        title: str = None:
            the plotted title to override the column name
        width: float = 1:
            the width of the column as a factor of the default width
        textprops: Dict[str, Any] = field(default_factory=dict)
            textprops provided to each textcell
        formatter: Callable | str = None:
            Either A Callable or a builtin format string to format
            the appearance of the texts
        cmap: Callable | LinearSegmentedColormap = None:
            A Callable that returns a color based on the cells value.
        text_cmap: Callable | LinearSegmentedColormap = None:
            A Callable that returns a color based on the cells value.
        group: str = None:
            Each group will get a spanner column label above the column labels.
        plot_fn: Callable = None
            A Callable that will take the cells value as input and create a subplot
            on top of each cell and plot onto them.
            To pass additional arguments to it, use plot_kw (see below).
        plot_kw: Dict[str, Any] = field(default_factory=dict)
            Additional keywords provided to plot_fn.
        border: str | List = None:
            Plots a vertical borderline.
            can be either "left" / "l", "right" / "r" or "both"

    Formatting digits reference:

    source: https://www.pythoncheatsheet.org/cheatsheet/string-formatting

        number      format      output      description
        ------      ------      ------      -----------
        3.1415926   {:.2f}      3.14        Format float 2 decimal places
        3.1415926   {:+.2f}     +3.14       Format float 2 decimal places with sign
        -1          {:+.2f}     -1.00       Format float 2 decimal places with sign
        2.71828     {:.0f}      3           Format float with no decimal places
        4           {:0>2d}     04          Pad number with zeros (left padding, width 2)
        4           {:x<4d}     4xxx        Pad number with x’s (right padding, width 4)
        10          {:x<4d}     10xx	    Pad number with x’s (right padding, width 4)
        1000000     {:,}        1,000,000   Number format with comma separator
        0.35        {:.2%}      35.00%      Format percentage
        1000000000  {:.2e}      1.00e+09    Exponent notation
        11          {:11d}      11          Right-aligned (default, width 10)
        11          {:<11d}     11          Left-aligned (width 10)
        11          {:^11d}     11          Center aligned (width 10)

    """

    name: str
    title: str = None  # allows to default to name in Table._get_column_titles
    width: float = 1
    textprops: Dict[str, Any] = field(default_factory=dict)
    type: ColumnType = ColumnType.STRING
    formatter: Callable | str = None
    cmap: Callable | LinearSegmentedColormap = None
    text_cmap: Callable | LinearSegmentedColormap = None
    group: str = None
    plot_fn: Callable = None
    plot_kw: Dict[str, Any] = field(default_factory=dict)
    border: str | List = None

    def _as_non_none_dict(self) -> Dict[str, Any]:
        """Returns the attributes as a dictionary, filtering out
        keys with None values.

        Returns:
            Dict[str, Any]: Dictionary of Column Attributes.
        """
        return _filter_none_values(asdict(self))

    def get(self, key, default=None) -> Any:
        return getattr(self, key, default)

    def __contains__(self, key) -> Any:
        return hasattr(self, key)

    def __getitem__(self, key):
        return getattr(self, key)


@dataclass
class TextColumnDefinition(ColumnDefinition):
    """A Class defining attributes for a table column.

    Args:
        name: str:
            the column name
        title: str = None:
            the plotted title to override the column name
        width: float = 1:
            the width of the column as a factor of the default width
        textprops: Dict[str, Any] = field(default_factory=dict)
            textprops provided to each textcell
        formatter: Callable | str = None:
            Either A Callable or a builtin format string to format
            the appearance of the texts
        group: str = None:
            Each group will get a spanner column label above the column labels.
        cmap: Callable | LinearSegmentedColormap = None:
            A Callable that returns a color based on the cells value.
        text_cmap: Callable | LinearSegmentedColormap = None:
            A Callable that returns a color based on the cells value.
        border: str | List = None:
            Plots a vertical borderline.
            can be either "left" / "l", "right" / "r" or "both"


    """

    name: str
    title: str = None
    width: float = 1
    textprops: Dict[str, Any] = field(default_factory=dict)
    type: ColumnType = ColumnType.STRING
    formatter: Callable | str = None
    group: str = None
    cmap: Callable | LinearSegmentedColormap = None
    text_cmap: Callable | LinearSegmentedColormap = None
    border: str | List = None

    def _as_non_none_dict(self) -> Dict[str, Any]:
        """Returns the attributes as a dictionary, filtering out
        keys with None values.

        Returns:
            Dict[str, Any]: Dictionary of Column Attributes.
        """
        return _filter_none_values(asdict(self))


@dataclass
class RichTextColumnDefinition(TextColumnDefinition):
    type: ColumnType = ColumnType.RICHTEXT
    richtext_props: Dict[str, Any] | None = None

    def __post_init__(self):
        self.formatter = self.formatter or str


@dataclass
class SubplotColumnDefinition(TextColumnDefinition):
    """_summary_

    Args:
        plot_fn: Callable = None
            A Callable that will take the cells value as input and create a subplot
            on top of each cell and plot onto them.
            To pass additional arguments to it, use plot_kw (see below).
        plot_kw: Dict[str, Any] = field(default_factory=dict)
            Additional keywords provided to plot_fn.
    """

    type: ColumnType = ColumnType.SUBPLOT
    plot_fn: Callable = None
    plot_kw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ColumnsInfos:
    definitions: dict[str, ColumnDefinition]

    @classmethod
    def from_definitions_and_table(
        cls, definitions: list[ColumnDefinition], table: pd.DataFrame
    ) -> ColumnsInfos:
        definitions = definitions or []

        if table.index.name is None:
            raise ValueError("Table index must have a name.")

        column_definitions = dict.fromkeys([table.index.name] + list(table.columns))

        # Populate with definitions list
        for cdef in definitions:
            column_definitions[cdef.name] = cdef

        # Add default for missing col defs
        for col in column_definitions:
            if column_definitions[col] is None:
                column_definitions[col] = ColumnDefinition(name=col)

        return cls(column_definitions)

    @property
    def names(self):
        return list(self.definitions.keys())

    @property
    def titles(self, name_as_default: bool = True):
        if not name_as_default:
            return self.pluck("title")

        return [
            name if not title else title
            for name, title in zip(self.names, self.pluck("title"))
        ]

    def get_columns_by_group(self):
        groups = defaultdict(list)
        for name, definition in self.definitions.items():
            if definition.group:
                groups[definition.group].append(name)

        return groups

    def __getitem__(self, key):
        return self.definitions[key]

    def get(self, key, default=None):
        return self.definitions.get(key, default=default)

    def pluck(self, key, default=None) -> list:
        """Returns a list of the ColumnDefinition property requested through `key`

        Args:
            key (str): the key to look for each ColumnDefinition
            default (Any, optional): Default value if not found. Defaults to None.

        Returns:
            list: list of the property looked for
        """
        return [coldef.get(key, default) for coldef in self.definitions.values()]

    def dict_pluck(self, key, default=None) -> dict:
        """Returns a list of the ColumnDefinition property requested through `key`

        Args:
            key (str): the key to look for each ColumnDefinition
            default (Any, optional): Default value if not found. Defaults to None.

        Returns:
            dict: dict of the property looked for as value, name as key
        """
        return {
            name: coldef.get(key, default) for name, coldef in self.definitions.items()
        }


# abbreviated name to reduce writing
ColDef = ColumnDefinition
