from __future__ import annotations

from typing import Any, Callable, Sequence

import matplotlib as mpl

from plottable.basecell import TableCell, TextCell
from plottable.colorcell import FlexiTextCell, HighlightTextCell
from plottable.column_def import ColumnDefinition, ColumnType
from plottable.richtext.richtextcell import RichTextCell


def create_cell(
    column_type: ColumnType = ColumnType.STRING,
    *args,
    **kwargs,
) -> TableCell:
    """Factory Function to create a specific TableCell depending on `column_type`.

    Change the behaviour to rely on kwargs to define the right TableCell

    TODO: TextCell should be defined by ColDef subclasses

    Args:
        column_type (ColumnType): plottable.column_def.ColumnType

    Returns:
        TableCell: plottable.cell.TableCell
    """
    cdef = kwargs.get("column_definition")
    """
    if cdef:
        print(f"({kwargs['row_idx']}, {kwargs['col_idx']}): {cdef.type}")
    else:
        print(f"({kwargs['row_idx']}, {kwargs['col_idx']}): No cdef")
    """

    if plot_fn := kwargs.get("plot_fn"):
        return SubplotCell(*args, **kwargs)

    content = kwargs.get("content")
    if content and "</>" in str(content):
        return FlexiTextCell(*args, **kwargs)
    if content and "::{" in str(content):
        return HighlightTextCell(*args, **kwargs)

    is_richtextcell = (
        getattr(cdef, "type", None) is ColumnType.RICHTEXT or 
        kwargs.get("rich_textprops")
    )  # fmt: off

    if is_richtextcell:
        return RichTextCell(*args, **kwargs)

    return TextCell(*args, **kwargs)


class SubplotCell(TableCell):
    """A SubplotTableCell class for a plottable.table.Table that creates a subplot on top of
    its rectangle patch.
    """

    def __init__(
        self,
        xy: tuple[float, float],
        content: Any,
        row_idx: int,
        col_idx: int,
        plot_fn: Callable,
        plot_kw: dict[str, Any] = {},
        width: float = 1,
        height: float = 1,
        ax: mpl.axes.Axes = None,
        rect_kw: dict[str, Any] = {},
        column_definition: ColumnDefinition | None = None,
        table=None,
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
            plot_fn (Callable):
                function that draws onto the created subplot.
            plot_kw (Dict[str, Any], optional):
                keywords for the plot_fn. Defaults to {}.
            width (float, optional):
                width of the rectangle cell. Defaults to 1.
            height (float, optional):
                height of the rectangle cell. Defaults to 1.
            ax (mpl.axes.Axes, optional):
                matplotlib Axes object. Defaults to None.
            rect_kw (Dict[str, Any], optional):
                keywords passed to matplotlib.patches.Rectangle. Defaults to {}.
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

        self._plot_fn = plot_fn
        self._plot_kw = plot_kw
        self.fig = self.ax.figure
        self.table = table
        self.draw()

    def plot(self):
        values = self.table[self.column_definition.name].to_list()
        self._plot_kw["values"] = values

        self._plot_fn(ax=self.axes_inset, val=self.content, **self._plot_kw)

    def make_axes_inset(self):
        rect_fig_coords = self._get_rectangle_bounds()
        self.axes_inset = self.fig.add_axes(rect_fig_coords)
        return self.axes_inset

    def _get_rectangle_bounds(self, padding: float = 0.2) -> list[float]:
        transformer = self.fig.transFigure.inverted()
        display_coords = self.rectangle_patch.get_window_extent()
        (xmin, ymin), (xmax, ymax) = transformer.transform(display_coords)
        y_range = ymax - ymin
        return [
            xmin,
            ymin + padding * y_range,
            xmax - xmin,
            ymax - ymin - 2 * padding * y_range,
        ]

    def draw(self):
        self.ax.add_patch(self.rectangle_patch)

    def __repr__(self) -> str:
        return f"SubplotCell(xy={self.xy}, row_idx={self.index[0]}, col_idx={self.index[1]})"  # noqa
