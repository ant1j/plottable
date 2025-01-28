from __future__ import annotations

import pickle as pl
from collections.abc import Sequence
from pathlib import Path
from typing import Mapping, Protocol

import matplotlib.pyplot as plt
from pandas import DataFrame, concat

from plottable.ppa_table import config as default_config
from plottable.ppa_table.utils import aggregate_columns_to_list
from plottable.richtable import RichTable


class PPAData(Protocol):
    market: DataFrame
    region: DataFrame
    category: DataFrame
    labels: Mapping[str, str]
    keys: dict


# TODO Move this somewhere more meaningful
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
        * Adding a "total" prefix to the category label on the last row

    """

    def __init__(
        self, data: DataFrame, config=default_config, metadata: dict | None = None
    ):
        self.data = data
        self.config = config
        self.metadata = metadata or {}
        self.rich_table = None

        self.fig = None
        self.ax = None

    def build(self):
        # remove nb_cli_ty (not displayed) but used for low base
        nb_cli = self.data.pop("nb_cli_ty").tolist()
        # self.data.drop(
        #     labels=["macro_categorie", "nom_micro_categorie"],
        #     axis=1,
        # )
        self._format_entry_label()
        self._format_category_total()
        footer_text = self._format_footer_text()

        self.fig, self.ax = plt.subplots(
            figsize=(15, max(4, len(self.data)))
        )  # at least 3
        plt.rcParams["font.family"] = "Century Gothic"
        plt.rcParams["svg.fonttype"] = "none"

        self.fig.tight_layout()

        self.rich_table = RichTable(
            self.data,
            column_definitions=self.config.column_definitions,
            col_label_divider=False,
            col_label_cell_kw={"height": 0.5},
            row_dividers=False,
            footer=footer_text,
            group_props=self.config.group_props,
        )
        # tab.col_label_row.set_fontfamily("Century Gothic")
        self.rich_table.col_label_row.set_fontsize(8)

        self._format_low_base(criteria=nb_cli)

    def _format_low_base(self, criteria: Sequence) -> None:
        for idx, base in enumerate(criteria):
            if base < 50:
                self.rich_table.rows[idx].set_facecolor("#eee")

    def _format_entry_label(self) -> None:
        category_name = self.data.index[-1]
        self.data["entry_label"] = self.data["entry_label"].apply(
            lambda val: f"{category_name} {val}"
        )

    def _format_category_total(self) -> None:
        category_name = self.data.index[-1]

        self.data = self.data.rename(index={category_name: f"Total {category_name}"})

    def _format_footer_text(self) -> str:
        # values in first row, label of the row (index), and category name
        values = self.data.iloc[0].to_dict() | dict(
            label=self.data.iloc[0].name,
            category_name=self.data.index[-1],
        )
        template = "Reading Note: among clients recruited in the category, {share_of_entry_ty:.0%} were recruited through {category_name} {label} in 2024. {repeat_rate_ty:.0%} ({evol_repeat_rate:+.0f}pp vs LY) of those have repurchased over the next 12 months, for an amount of ${repeat_to_ty:,.0f} ({evol_repeat_to:+.0%} vs LY)"
        return template.format_map(values)

    def dump_fig(self, path: str | Path) -> None:
        path = Path(path)

        with open(path, "wb") as pf:
            pl.dump(self.fig, pf)

    def savefig(self, path: Path | str, **kwargs) -> None:
        kwargs = kwargs | dict(
            format="png",
            dpi=200,
            bbox_inches="tight",
        )

        plt.savefig(path)

    def show(self) -> None:
        plt.show()

    def close(self) -> None:
        plt.close(self.fig)

    @classmethod
    def from_ppadata(cls, data: PPAData, config) -> PPATable:
        """Create a PPATable from a PPAData object that is taken from a `PPADataRepo`.

        We need to adapt the data to fit to the PPATable data model.

        PPADataRepo is also used for other things, e.g. Bubble Charts generation, etc., hence
        the need for a generic output that consumer classes can adapt to their needs

        Args:
            data (PPAData): the data from a `PPADataRepo`
            config (Mapping): config object, passed to the PPATable

        Returns:
            PPATable: the PPATable for the given data
        """
        table_data = concat(
            [
                data.market.sort_values("share_of_entry_ty", ascending=False),
                data.category,
            ]
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

        return cls(
            data=table_data,
            config=config,
            metadata=data.keys,
        )
