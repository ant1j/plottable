from __future__ import annotations

from itertools import accumulate
from numbers import Number
from typing import Any, Callable

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

from plottable.cell import SubplotCell, TableCell, create_cell
from plottable.cellsequence import Column, Row
from plottable.column_def import ColumnDefinition, ColumnsInfos
from plottable.font import contrasting_font_color
from plottable.formatters import apply_formatter
from plottable.helpers import _replace_lw_key


class RichTable:
    def __init__(
        self,
        table: pd.DataFrame,
        ax: mpl.axes.Axes = None,
        column_definitions: list[ColumnDefinition] | None = None,
        textprops: dict[str, Any] = {},
        cell_kw: dict[str, Any] = {},
        col_label_cell_kw: dict[str, Any] = {},
        col_label_divider: bool = True,
        col_label_divider_kw: dict[str, Any] = {},
        row_dividers: bool = True,
        row_divider_kw: dict[str, Any] = {},
        column_border_kw: dict[str, Any] = {},
        even_row_color: str | tuple = None,
        odd_row_color: str | tuple = None,
        footer: str = "",
        footer_divider: bool = False,
        footer_divider_kw: dict[str, Any] = {},
        group_props: dict[str, Any] = {},
    ):
        self.ax = ax or plt.gca()
        self.figure = self.ax.figure

        # Ensure index name for table
        self.table = self._init_table(table)

        self.column_names = [self.table.index.name] + list(self.table.columns)

        # Attach passed column_definitions and add default to table's columns without one
        self.column_definitions = self._init_column_definitions(column_definitions)

        # This should replace (at least):
        # * self.column_names
        # * self.column_definitions
        self.column_infos = ColumnsInfos.from_definitions_and_table(
            definitions=column_definitions,
            table=table,
        )

        self.cell_kw = cell_kw
        self.col_label_cell_kw = col_label_cell_kw
        self.textprops = textprops
        if "ha" not in textprops:
            self.textprops.update({"ha": "right"})

        self.cells = {}
        self.columns = self._init_columns()
        self.rows = self._init_rows()
        self.col_label_row = self._build_col_label_row(-1, self.column_infos.titles)
        self.col_group_cells: dict[str, TableCell] = {}
        # FIXME Should not pass those vars here
        self._apply_table_formatting_rules(even_row_color, odd_row_color)

        self._plot_elements(
            group_props,
            col_label_divider_kw,
            footer_divider_kw,
            row_divider_kw,
            column_border_kw,
            # footer,
        )

        self._footer = self._plot_footer(footer)

        self._adjust_axes()

        self._plot_subplots()

    @property
    def n_rows(self):
        return self.table.shape[0]

    @property
    def n_cols(self):
        return self.table.shape[1]

    @property
    def shape(self):
        return self.table.shape

    def _init_table(self, table: pd.DataFrame):
        if table.index.name is None:
            table.index.name = "index"

        return table

    def _init_column_definitions(
        self, column_definitions: list[ColumnDefinition] | None = None
    ) -> dict[str, ColumnDefinition]:
        """
        Initializes the Tables ColumnDefinitions.

        Store column definition and adds ColumnDefinition for missing ones.

        Args:
            column_definitions (list[ColumnDefinition]):
                List of ColumnDefinitions
        """
        column_defs = {_def.name: _def for _def in (column_definitions or [])}

        for col in self.column_names:
            if col not in column_defs:
                column_defs[col] = ColumnDefinition(name=col)

        return column_defs

    def _init_columns(self) -> dict[str, Column]:
        """Initializes the Tables columns."""
        return {
            name: Column(index=idx, cells=[], name=name)
            for idx, name in enumerate(self.column_names)
        }

    def _init_rows(self) -> dict[int, Row]:
        """Initializes the Tables Rows."""
        return {
            idx: self._build_row(idx, values)
            for idx, values in enumerate(self.table.to_records())
        }

    def _apply_table_formatting_rules(self, even_row_color, odd_row_color):
        self._apply_alternating_row_colors(even_row_color, odd_row_color)
        self._apply_column_formatters()
        self._apply_column_cmaps()
        self._apply_column_text_cmaps()

    def _apply_alternating_row_colors(
        self, color: str | tuple[float] = None, color2: str | tuple[float] = None
    ) -> RichTable:
        """Sets the color of even row's rectangle patches to `color`.

        Args:
            color (str): color recognized by matplotlib for the even rows 0 ...
            color2 (str): color recognized by matplotlib for the odd rows 1 ...

        Returns:
            Table: plottable.table.Table
        """
        rows = list(self.rows.values())

        if color is not None:
            for row in rows[::2]:
                row.set_facecolor(color)

        if color2 is not None:
            for row in rows[1::2]:
                row.set_facecolor(color2)

        return self

    def _apply_column_formatters(self) -> None:
        """
        Formatting should be down at Cell level,
        to adapt the right formatting rules"""
        return

        for colname, _dict in self.column_definitions.items():
            formatter = _dict.get("formatter")
            if formatter is None:
                continue

            for cell in self.columns[colname].cells:
                if not hasattr(cell, "text"):
                    continue

                formatted = apply_formatter(formatter, cell.content)
                cell.text.set_text(formatted)

    def _apply_column_cmaps(self) -> None:
        for colname, _dict in self.column_definitions.items():
            cmap_fn = _dict.get("cmap")
            if cmap_fn is None:
                continue

            for cell in self.columns[colname].cells:
                if not isinstance(cell.content, Number):
                    continue

                if ("bbox" in _dict.get("textprops")) & hasattr(cell, "text"):
                    cell.text.set_bbox(
                        {
                            "color": cmap_fn(cell.content),
                            **_dict.get("textprops").get("bbox"),
                        }
                    )
                else:
                    cell.rectangle_patch.set_facecolor(cmap_fn(cell.content))

    def _apply_column_text_cmaps(self) -> None:
        for colname, _dict in self.column_definitions.items():
            cmap_fn = _dict.get("text_cmap")
            if cmap_fn is None:
                continue

            for cell in self.columns[colname].cells:
                # if isinstance(cell.content, Number) & hasattr(cell, "text"):
                if hasattr(cell, "text"):
                    cell.text.set_color(cmap_fn(cell.content))

    def _plot_elements(
        self,
        group_props: dict[str, Any],
        col_label_divider_kw: dict[str, Any],
        footer_divider_kw: dict[str, Any],
        row_divider_kw: dict[str, Any],
        column_border_kw: dict[str, Any],
    ):
        self._plot_col_group_labels(group_props)
        self._plot_col_label_divider(**col_label_divider_kw)
        self._plot_footer_divider(**footer_divider_kw)
        self._plot_row_dividers(**row_divider_kw)
        self._plot_column_borders(**column_border_kw)

    def _plot_col_group_labels(self, group_props: dict = {}) -> None:
        """Plots the column group labels."""

        GROUP_LABEL_TEXTPROPS = {}
        GROUP_LABEL_KW = {
            "height": 0.5,
        }

        for group in [
            group for group in self.column_infos.pluck("group") if group is not None
        ]:
            columns = [
                self.columns[colname]
                for colname, _dict in self.column_definitions.items()
                if _dict.get("group") == group
            ]
            x_min = min(col.xrange[0] for col in columns)
            x_max = max(col.xrange[1] for col in columns)
            dx = x_max - x_min

            # CHANGED Substract the group label (default) height (1) to the `y` coordinates to position properly
            y = 0 - self.col_label_row.height - GROUP_LABEL_KW["height"]

            textprops = self.textprops.copy()
            textprops.update({"ha": "center", "va": "bottom"})

            textprops.update(GROUP_LABEL_TEXTPROPS)

            self.col_group_cells[group] = create_cell(
                xy=(x_min, y),
                content=group,
                row_idx=y,
                col_idx=columns[0].index,
                width=x_max - x_min,
                height=GROUP_LABEL_KW["height"],
                ax=self.ax,
                textprops=textprops,
                # rect_kw={"facecolor": "lightpink"},
                rich_textprops=group_props.get(group, {}),
            )

            self.col_group_cells[group].draw()
            self.ax.plot(
                [x_min + 0.05 * dx, x_max - 0.05 * dx],
                # CHANGED Add height (1) to have the border at the botton of the Rectangle patch of the group label
                [y + GROUP_LABEL_KW["height"], y + GROUP_LABEL_KW["height"]],
                lw=0.2,
                color=plt.rcParams["text.color"],
            )

    def _plot_col_label_divider(self, **kwargs):
        """Plots a line below the column labels."""
        if not kwargs:
            return

        COL_LABEL_DIVIDER_KW = {"color": plt.rcParams["text.color"], "linewidth": 1}
        if "lw" in kwargs:
            kwargs["linewidth"] = kwargs.pop("lw")
        COL_LABEL_DIVIDER_KW.update(kwargs)
        self.COL_LABEL_DIVIDER_KW = COL_LABEL_DIVIDER_KW

        x0, x1 = self.rows[0].xrange
        self.ax.plot(
            [x0, x1],
            [0, 0],
            **COL_LABEL_DIVIDER_KW,
        )

    def _plot_footer_divider(self, **kwargs):
        """Plots a line below the bottom TableRow."""
        if not kwargs:
            return

        FOOTER_DIVIDER_KW = {"color": plt.rcParams["text.color"], "linewidth": 1}
        if "lw" in kwargs:
            kwargs["linewidth"] = kwargs.pop("lw")
        FOOTER_DIVIDER_KW.update(kwargs)
        self.FOOTER_DIVIDER_KW = FOOTER_DIVIDER_KW

        x0, x1 = list(self.rows.values())[-1].xrange
        y = len(self.table)
        self.ax.plot([x0, x1], [y, y], **FOOTER_DIVIDER_KW)

    def _plot_footer(self, footer: str) -> TableCell | None:
        """Plots the footer text below the table.

        Args:
            footer (str): footer text
        """
        if not footer:
            return

        x0, x1 = list(self.rows.values())[-1].xrange
        y = len(self.table)

        footer_cell = create_cell(
            xy=(x0, y),
            content=footer,
            row_idx=y,
            col_idx=1,
            width=x1 - x0,
            height=0.5,
            ax=self.ax,
            textprops={"fontsize": 8, "ha": "left", "va": "top"},
            padding=0.1,
        )
        footer_cell.draw()

        return footer_cell

    def _plot_row_dividers(self, **kwargs):
        """Plots lines between all TableRows."""
        if not kwargs:
            return

        ROW_DIVIDER_KW = {
            "color": plt.rcParams["text.color"],
            "linewidth": 0.2,
        }
        kwargs = _replace_lw_key(kwargs)
        ROW_DIVIDER_KW.update(kwargs)

        for idx, row in list(self.rows.items())[1:]:
            x0, x1 = row.xrange

            self.ax.plot([x0, x1], [idx, idx], **ROW_DIVIDER_KW)

    def _plot_column_borders(self, **kwargs):
        """Plots lines between all TableColumns where "border" is defined."""
        if not kwargs:
            return

        COLUMN_BORDER_KW = {"linewidth": 1, "color": plt.rcParams["text.color"]}

        kwargs = _replace_lw_key(kwargs)
        COLUMN_BORDER_KW.update(kwargs)

        for name, _def in self.column_definitions.items():
            if "border" in _def:
                col = self.columns[name]

                y0, y1 = col.yrange

                if "l" in _def["border"].lower() or _def["border"].lower() == "both":
                    x = col.xrange[0]
                    self.ax.plot([x, x], [y0, y1], **COLUMN_BORDER_KW)

                if "r" in _def["border"].lower() or _def["border"].lower() == "both":
                    x = col.xrange[1]
                    self.ax.plot([x, x], [y0, y1], **COLUMN_BORDER_KW)

    def _build_col_label_row(self, idx: int, content: list[str | Number]) -> Row:
        """Creates the Column Label Row.

        Args:
            idx (int): index of the Row
            content (list[str  |  Number]): content that is plotted as text.

        Returns:
            Row: Column Label Row
        """
        widths = self.column_infos.pluck("width", 1)

        if "height" in self.col_label_cell_kw:
            height = self.col_label_cell_kw["height"]
        else:
            height = 1

        row = Row(cells=[], index=idx)

        for col_idx, (colname, width, _content, x) in enumerate(
            zip(self.column_names, widths, content, list(accumulate([0] + widths)))
        ):
            col_def = self.column_definitions[colname]
            textprops = self._get_column_textprops(col_def)

            # don't apply bbox around text in header
            if "bbox" in textprops:
                textprops.pop("bbox")

            cell = create_cell(
                # column_type=ColumnType.STRING,
                xy=(
                    x,
                    idx + 1 - height,
                ),  # if height is different from 1 we need to adjust y
                content=_content,
                row_idx=idx,
                col_idx=col_idx,
                width=width,
                height=height,
                rect_kw=self.col_label_cell_kw,
                textprops=textprops,
                ax=self.ax,
                column_definition=col_def,
                boxprops=col_def.get("boxprops", {}),
            )

            row.append(cell)
            cell.draw()

        return row

    def _plot_subplots(self) -> None:
        self.subplots = {}
        for key, cell in self.cells.items():
            if isinstance(cell, SubplotCell):
                self.subplots[key] = cell.make_axes_inset()
                self.subplots[key].axis("off")
                cell.draw()
                cell.plot()

    def _get_column_textprops(self, col_def: ColumnDefinition) -> dict[str, Any]:
        textprops = self.textprops.copy()
        column_textprops = col_def.get("textprops", {})
        textprops.update(column_textprops)
        textprops["multialignment"] = textprops["ha"]

        return textprops

    def _build_row(self, idx: int, content: Any) -> Row:
        widths = self.column_infos.pluck("width", 1)

        row = Row(cells=[], index=idx)

        for col_idx, (colname, width, _content, x) in enumerate(
            zip(self.column_names, widths, content, list(accumulate([0] + widths)))
        ):
            col_def = self.column_definitions[colname]

            cell = create_cell(
                xy=(x, idx),
                content=_content,
                plot_fn=col_def.get("plot_fn", None),
                plot_kw=col_def.get("plot_kw", {}),
                row_idx=idx,
                col_idx=col_idx,
                width=width,
                rect_kw=self.cell_kw,
                ax=self.ax,
                column_definition=col_def,
                textprops=self._get_column_textprops(col_def),
                boxprops=col_def.get("boxprops", {}),
            )

            row.append(cell)
            self.columns[colname].append(cell)
            self.cells[(idx, col_idx)] = cell
            cell.draw()

        return row

    def autoset_fontcolors(
        self, fn: Callable = None, colnames: list[str] = None, **kwargs
    ) -> RichTable:
        """Sets the fontcolor of each table cell based on the facecolor of its rectangle patch.

        Args:
            fn (Callable, optional):
                Callable that takes the rectangle patches facecolor as
                rgba-value as argument.
                Defaults to plottable.font.contrasting_font_color if fn is None.
            colnames (list[str], optional):
                columns to apply the function to
            kwargs are passed to fn.

        Returns:
            plottable.table.Table
        """

        if fn is None:
            fn = contrasting_font_color
            if "thresh" not in kwargs:
                kwargs.update({"thresh": 150})

        if colnames is not None:
            cells = []
            for name in colnames:
                cells.extend(self.columns[name].cells)

        else:
            cells = self.cells.values()

        for cell in cells:
            if hasattr(cell, "text"):
                text_bbox = cell.text.get_bbox_patch()

                if text_bbox:
                    bg_color = text_bbox.get_facecolor()
                else:
                    bg_color = cell.rectangle_patch.get_facecolor()

                textcolor = fn(bg_color, **kwargs)
                cell.text.set_color(textcolor)

        return self

    def _adjust_axes(self):
        self.ax.axis("off")
        self.ax.set_xlim(-0.025, sum(self.column_infos.pluck("width", 1)) + 0.025)

        ymax = self.n_rows
        ymin = -self.col_label_row.height
        if self.col_group_cells:
            ymin -= 0.5  # FIXME hardcoded value
            # ymin -= 1  # FIXME hardcoded value

        self.ax.set_ylim(ymin - 0.025, ymax + 0.05)
        self.ax.invert_yaxis()

        #####################
        group_height = 0
        if list(self.col_group_cells.values()):
            group_height += list(self.col_group_cells.values())[0].height

        footer_height = 0
        if self._footer:
            footer_height += self._footer.height
        ymin = -(
            self.col_label_row.height + group_height
            # - coords.height
        )
        ymax = (
            self.n_rows
            # + self.col_label_row.height
            # + list(self.col_group_cells.values())[0].height
            + footer_height
        )
        #####################
