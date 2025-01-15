from numbers import Number
from typing import Any

import matplotlib as mpl
from flexitext import flexitext
from highlight_text import HighlightText

from plottable.basecell import TextCell
from plottable.column_def import ColumnDefinition


class HighlightTextCell(TextCell):
    """A HighlightTextCell class for a plottable.table.Table that creates a text inside its rectangle patch."""

    def __init__(
        self,
        xy: tuple[float, float],
        content: str | Number,
        row_idx: int,
        col_idx: int,
        width: float = 1,
        height: float = 1,
        ax: mpl.axes.Axes = None,
        rect_kw: dict[str, Any] = {},
        textprops: dict[str, Any] = {},
        highlight_textprops: dict[str, Any] | None = None,
        padding: float = 0.1,
        column_definition: ColumnDefinition | None = None,
        **kwargs,
    ):
        """
        Args:
            xy (tuple[float, float]):
                lower left corner of a rectangle
            content (Any):
                the content of the cell
            row_idx (int):
                row index
            col_idx (int):
                column index
            width (float, optional):
                width of the rectangle cell. Defaults to 1.
            height (float, optional):
                height of the rectangle cell. Defaults to 1.
            ax (mpl.axes.Axes, optional):
                matplotlib Axes object. Defaults to None.
            rect_kw (dict[str, Any], optional):
                keywords passed to matplotlib.patches.Rectangle. Defaults to {}.
            textprops (dict[str, Any], optional):
                textprops passed to matplotlib.text.Text. Defaults to {}.
            padding (float, optional):
                Padding around the text within the rectangle patch. Defaults to 0.1.

        """
        super().__init__(
            xy=xy,
            width=width,
            height=height,
            content=content,
            row_idx=row_idx,
            col_idx=col_idx,
            ax=ax,
            rect_kw=rect_kw,
            textprops=textprops,
            padding=padding,
            column_definition=column_definition,
        )

        self.highlight_textprops = highlight_textprops

    def set_text(self):
        x, y = self._get_text_xy()

        content = str(self.content)

        self.text = HighlightText(
            x,
            y,
            content,
            highlight_textprops=self.highlight_textprops,
            ax=self.ax,
            textalign="right",
            **self.textprops,
        )


class FlexiTextCell(TextCell):
    """A FlexiTextCell class for a plottable.table.Table that creates a text inside its rectangle patch."""

    def __init__(
        self,
        xy: tuple[float, float],
        content: str | Number,
        row_idx: int,
        col_idx: int,
        width: float = 1,
        height: float = 1,
        ax: mpl.axes.Axes = None,
        rect_kw: dict[str, Any] = {},
        textprops: dict[str, Any] = {},
        flexitext_props: dict[str, Any] | None = None,
        padding: float = 0.1,
        column_definition: ColumnDefinition | None = None,
        **kwargs,
    ):
        """
        Args:
            xy (tuple[float, float]):
                lower left corner of a rectangle
            content (Any):
                the content of the cell
            row_idx (int):
                row index
            col_idx (int):
                column index
            width (float, optional):
                width of the rectangle cell. Defaults to 1.
            height (float, optional):
                height of the rectangle cell. Defaults to 1.
            ax (mpl.axes.Axes, optional):
                matplotlib Axes object. Defaults to None.
            rect_kw (dict[str, Any], optional):
                keywords passed to matplotlib.patches.Rectangle. Defaults to {}.
            textprops (dict[str, Any], optional):
                textprops passed to matplotlib.text.Text. Defaults to {}.
            padding (float, optional):
                Padding around the text within the rectangle patch. Defaults to 0.1.

        """
        super().__init__(
            xy=xy,
            width=width,
            height=height,
            content=content,
            row_idx=row_idx,
            col_idx=col_idx,
            ax=ax,
            rect_kw=rect_kw,
            textprops=textprops,
            padding=padding,
            column_definition=column_definition,
        )

        self.flexitext_props = flexitext_props

    def set_text(self):
        x, y = self._get_text_xy()

        content = str(self.content)

        self.text = flexitext(
            x,
            y,
            s=content,
            ha=self.textprops.get("ha", "right"),
            va=self.textprops.get("va", "center"),
            ma=self.textprops.get("ha", "right"),
            mva=self.textprops.get("va", "center"),
            ax=self.ax,
            # xycoords="figure fraction",
            # **self.textprops,
        )
