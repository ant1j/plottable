from __future__ import annotations

from numbers import Number
from typing import Any, Dict, Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from plottable.column_def import ColumnDefinition
from plottable.formatters import apply_formatter


class Cell:
    """A cell is a rectangle defined by the lower left corner xy and it's width and height."""

    def __init__(self, xy: Tuple[float, float], width: float = 1, height: float = 1):
        """
        Args:
            xy (Tuple[float, float]): lower left corner of a rectangle
            width (float, optional): width of the rectangle cell. Defaults to 1.
            height (float, optional): height of the rectangle cell. Defaults to 1.
        """
        self.xy = xy
        self.width = width
        self.height = height

    @property
    def x(self) -> float:
        return self.xy[0]

    @property
    def y(self) -> float:
        return self.xy[1]

    def __repr__(self) -> str:
        return f"Cell({self.xy}, {self.width}, {self.height})"


class TableCell(Cell):
    """A TableCell class for a plottable.table.Table."""

    def __init__(
        self,
        xy: Tuple[float, float],
        content: Any,
        row_idx: int,
        col_idx: int,
        width: float = 1,
        height: float = 1,
        ax: mpl.axes.Axes = None,
        rect_kw: Dict[str, Any] = {},
        column_definition: ColumnDefinition | None = None,
    ):
        """
        Args:
            xy (Tuple[float, float]):
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
            rect_kw (Dict[str, Any], optional):
                keywords passed to matplotlib.patches.Rectangle. Defaults to {}.
        """

        super().__init__(xy, width, height)
        self.index = (row_idx, col_idx)
        self.content = content
        self.row_idx = row_idx
        self.col_idx = col_idx
        self.ax = ax or plt.gca()
        self.rect_kw = {
            "linewidth": 0.0,
            "edgecolor": self.ax.get_facecolor(),
            "facecolor": self.ax.get_facecolor(),
            "width": width,
            "height": height,
        }
        self.column_definition = column_definition

        self.rect_kw.update(rect_kw)
        self.rectangle_patch = Rectangle(xy, **self.rect_kw)

    def draw(self):
        self.ax.add_patch(self.rectangle_patch)

    def __repr__(self) -> str:
        return (
            f"TableCell(xy={self.xy}, row_idx={self.index[0]}, col_idx={self.index[1]})"  # noqa
        )


class TextCell(TableCell):
    """A TextCell class for a plottable.table.Table that creates a text inside it's rectangle patch."""

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
        padding: float = 0.05,
        column_definition: ColumnDefinition | None = None,
        **kwargs,
    ):
        """
        Args:
            xy (Tuple[float, float]):
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
            rect_kw (Dict[str, Any], optional):
                keywords passed to matplotlib.patches.Rectangle. Defaults to {}.
            textprops (Dict[str, Any], optional):
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
            column_definition=column_definition,
        )

        self.textprops = {"ha": "right", "va": "center"}
        self.textprops.update(textprops)
        self.ha = self.textprops["ha"]
        self.va = self.textprops["va"]
        self.padding = padding

    def draw(self):
        self.ax.add_patch(self.rectangle_patch)
        self.set_text()

    def set_text(self):
        x, y = self._get_text_xy()

        content = self.format_content()

        self.text = self.ax.text(x, y, content, **self.textprops)

    def format_content(self):
        formatter = str
        if self.column_definition:
            formatter = self.column_definition.get("formatter", str)
            # Can still return None if the key exists but the value is None
            formatter = formatter or str

        return apply_formatter(formatter, self.content)

    def _get_text_xy(self, padding: float | None = None):
        x, y = self.xy

        padding = padding or self.padding

        # FIXME Remove padding being proportional to the size of the cell.
        if self.ha == "left":
            # x = x + padding * self.width
            x = x + padding
        elif self.ha == "right":
            # x = x + (1 - padding) * self.width
            x = x + self.width - padding
        elif self.ha == "center":
            x = x + self.width / 2
        else:
            raise ValueError(
                f"ha can be either 'left', 'center' or 'right'. You provided {self.ha}."
            )

        if self.va == "center":
            y += self.height / 2
        elif self.va == "bottom":
            # CHANGED
            # y = y + (1 - padding) * self.height
            y = y + self.height - padding
        elif self.va == "top":
            # CHANGED
            # y = y + padding * self.height
            y = y + padding

        return x, y

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(xy={self.xy}, content={self.content}, row_idx={self.index[0]}, col_idx={self.index[1]})"  # noqa
