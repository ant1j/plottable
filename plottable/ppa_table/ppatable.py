from __future__ import annotations

import pickle
import warnings
from collections.abc import Sequence
from copy import deepcopy
from pathlib import Path
from typing import Mapping, Protocol

import matplotlib as mpl
import matplotlib.pyplot as plt
from pandas import DataFrame, concat

from plottable.ppa_table.utils import aggregate_columns_to_list
from plottable.richtable import RichTable

# Prevent window opening from (default) TkAgg
mpl.use("Agg")


class PPAData(Protocol):
    market: DataFrame
    region: DataFrame
    category: DataFrame
    labels: Mapping[str, str]
    keys: dict


# FIXME To be removed?
def _prepare_data(data, config):
    """_prepare_data"""

    # Turn group of cols to list in a single cols
    market_data = (
        data["market"]
        .copy()
        .assign(
            first_purch_to=aggregate_columns_to_list(
                data["market"],
                columns=config.first_purch_to_cols,
            ),
            evol_first_purch_to=aggregate_columns_to_list(
                data["market"],
                columns=config.first_purch_to_cols_evol,
            ),
        )
    )
    # Add cols, keep only relevant,set index
    market_data = (
        market_data.assign(entry_label="Only:\nCross-Seller:\nAverage:")
        .loc[:, config.cols_for_table]
        .assign(micro_categorie=lambda X: X.micro_categorie.map(data["label_mapping"]))
        .set_index("micro_categorie")
    )

    return market_data


# FIXME To be removed?
def _get_table_data(data: DataFrame, cat: str, sscat: str):
    sscat_data = data.query(
        f"macro_categorie == '{cat}' & nom_micro_categorie == '{sscat}'"
    ).sort_values("share_of_entry_ty", ascending=False)

    category_data = data.query(
        f"nom_micro_categorie == 'categorie_cv' and macro_categorie == '{cat}'"
    )

    return concat([sscat_data, category_data])


class PPATable:
    """
    PPATable class

    Wrapper around a RichTable object, to manage and prepare the little details of a PPA Table on a slide:
        * The category name in the "only"/"X-sellers/Avg' column
        * the footer text
        * Adding a "total" prefix to the category label on the last row - if not present yet

    """

    def __init__(self, data: DataFrame, config=None, metadata: dict | None = None):
        self.data = data
        self.config = config or {}
        self.metadata = metadata or {}
        self.rich_table = None

        self.fig = None
        self.ax = None

    def build(self):
        # remove nb_cli_ty (not displayed) but used for low base
        nb_cli = self.data.pop("nb_cli_ty").tolist()

        self._format_entry_label()
        self._format_category_total()

        self.fig, self.ax = plt.subplots(
            figsize=(15, max(4, len(self.data)))
        )  # at least 4
        plt.rcParams["font.family"] = "Century Gothic"
        plt.rcParams["svg.fonttype"] = "none"

        self.fig.tight_layout()

        self.rich_table = RichTable(
            table=self.data,
            ax=self.ax,
            column_definitions=self.config.column_definitions,
            col_label_divider=False,
            col_label_cell_kw={"height": 0.5},
            row_dividers=False,
            footer=self._format_footer_text(),
            group_props=self.config.group_props,
        )
        # tab.col_label_row.set_fontfamily("Century Gothic")
        # self.rich_table.col_label_row.set_fontsize(8)

        self._format_low_base(criteria=nb_cli)
        self._format_category_font()

    @property
    def shape(self):
        if self.rich_table:
            return self.rich_table.shape

    def __len__(self):
        if self.rich_table:
            return self.rich_table.shape[0]
        return -1

    def _format_low_base(
        self, criteria: Sequence, threshold: int = 50, facecolor="#eee"
    ) -> None:
        for idx, base in enumerate(criteria):
            if base < threshold:
                self.rich_table.rows[idx].set_facecolor(facecolor)

    def _format_category_font(self):
        cell = self.rich_table.cells[(self.rich_table.n_rows - 1, 0)]

        cell.text.set_fontsize(12)
        cell.text.set_color("#333")

    def _format_entry_label(self) -> None:
        category_name = self.data.index[-1]

        if str(category_name).lower().startswith("total"):
            # remove 1st word if it's 'total'
            category_name = category_name.split(" ", 1)[1]

        self.data["entry_label"] = self.data["entry_label"].apply(
            lambda val: f"{category_name} {val}"
        )

    def _format_category_total(self) -> None:
        category_name = self.data.index[-1]

        if not str(category_name).lower().startswith("total"):
            self.data = self.data.rename(
                index={category_name: f"Total {category_name}"}
            )

    def _format_footer_text(self) -> str:
        # values in first row, label of the row (index), and category name
        values = self.data.iloc[0].to_dict() | dict(
            label=self.data.iloc[0].name,
            category_name=self.data.index[-1],
        )
        template = (
            "Reading Note: among clients recruited in the category, {share_of_entry_ty:.0%}"
            "were recruited through {category_name} {label} in 2024. {repeat_rate_ty:.0%} "
            "({evol_repeat_rate:+.0f}pp vs LY) of those have repurchased over the next 12 months, "
            "for an amount of ${repeat_to_ty:,.0f} ({evol_repeat_to:+.0%} vs LY)"
        )
        return template.format_map(values)

    def to_pickle(self, path):
        with open(path, "wb") as fd:
            pickle.dump(self.fig, fd)

        return self

    def savefig(
        self,
        path: Path | str,
        create_path: bool = True,
        overwrite: bool = True,
        **kwargs,
    ) -> None:
        """Save fig to file.

        Parameters
        ----------
        path : Path | str
            the path to save the figure to.
        create_path : bool, optional
            If the folders should be created or not, by default True
        overwrite : bool, optional
            if the file should be overwritten if it already exists, by default True
        kwargs
            Arguments passed to the `plt.savefig` method.
        """
        path = Path(path)

        if not path.parent.exists() and create_path:
            path.parent.mkdir(parents=True, exist_ok=True)

        kwargs = dict(
            # format="png",
            dpi=200,
            bbox_inches="tight",
        ).update(kwargs)

        if not overwrite and path.exists():
            warnings.warn(
                f"File `{path}` already exists and was not overwritten. "
                "Use `overwrite=True` if you want to overwrite existing file.",
                stacklevel=2,
            )
        else:
            plt.savefig(path)

        return self

    def show(self) -> None:
        plt.show()
        return self

    def close(self) -> None:
        plt.close(self.fig)
        return self

    @classmethod
    def from_ppadata(
        cls, data: PPAData, config, params: Mapping | None = None
    ) -> PPATable:
        """Create a PPATable from a PPAData object that is taken from a `PPADataRepo`.

        We need to adapt the data to fit to the PPATable data model.

        PPADataRepo is also used for other things, e.g. Bubble Charts generation, etc., hence
        the need for a generic output that consumer classes can adapt to their needs.

        Args:
            data (PPAData): the data from a `PPADataRepo`
            config (Mapping): config object, passed to the PPATable

        Returns:
            PPATable: the PPATable for the given data
        """
        table_data = (
            concat(
                [
                    data.market.sort_values("share_of_entry_ty", ascending=False),
                    data.category,
                ]
            )
            .convert_dtypes()
            .infer_objects(copy=False)
            .fillna(0)
        )

        table_data = (
            table_data.assign(
                first_purch_to=aggregate_columns_to_list(
                    table_data,
                    columns=config.first_purch_to_cols,
                ),
                evol_first_purch_to=aggregate_columns_to_list(
                    table_data,
                    columns=config.first_purch_to_cols_evol,
                ),
                entry_label="Only:\nCross-Seller:\nAverage:",
                micro_categorie=(lambda X: X["micro_categorie"].replace(data.labels)),
            )
            .drop(["nom_micro_categorie", "macro_categorie"], axis=1)
            .loc[:, config.cols_for_table]
            .set_index("micro_categorie")
        )

        # Copy before mutate
        # config = deepcopy(config)

        if (
            params is not None
            and params.get("purchase_type", "recruitment") == "conversion"
        ):
            config.column_definitions = config.column_definitions_conversion
        else:
            config.column_definitions = config.column_definitions

        return cls(
            data=table_data,
            config=config,
            metadata=data.keys,
        )
