from __future__ import annotations

from itertools import zip_longest
from numbers import Number
from typing import Any, Callable, Dict, List, Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt
from flexitext import flexitext
from highlight_text import HighlightText
from matplotlib.offsetbox import AnnotationBbox, HPacker, TextArea, VPacker
from matplotlib.patches import Circle, Rectangle
from matplotlib.transforms import ScaledTranslation

from plottable.column_def import ColumnDefinition, ColumnType


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
    if cdef := kwargs.get("col_def"):
        print(f"({kwargs['row_idx']}, {kwargs['col_idx']}): {cdef.type}")
    else:
        print(f"({kwargs['row_idx']}, {kwargs['col_idx']}): No cdef")

    if plot_fn := kwargs.get("plot_fn"):
        return SubplotCell(*args, **kwargs)

    content = kwargs.get("content")
    if content and "</>" in str(content):
        return FlexiTextCell(*args, **kwargs)
    if content and "::{" in str(content):
        return HighlightTextCell(*args, **kwargs)

    is_richtextcell = (
        getattr(cdef, "type", None) is ColumnType.RICHTEXT or "rich_textprops" in kwargs
    )

    if is_richtextcell:
        return RichTextCell(*args, **kwargs)

    return TextCell(*args, **kwargs)


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
        col_def: ColumnDefinition | None = None,
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
        self.column_definition = col_def

        self.rect_kw.update(rect_kw)
        self.rectangle_patch = Rectangle(xy, **self.rect_kw)

    def draw(self):
        self.ax.add_patch(self.rectangle_patch)

    def __repr__(self) -> str:
        return (
            f"TableCell(xy={self.xy}, row_idx={self.index[0]}, col_idx={self.index[1]})"  # noqa
        )


class SubplotCell(TableCell):
    """A SubplotTableCell class for a plottable.table.Table that creates a subplot on top of
    it's rectangle patch.
    """

    def __init__(
        self,
        xy: Tuple[float, float],
        content: Any,
        row_idx: int,
        col_idx: int,
        plot_fn: Callable,
        plot_kw: Dict[str, Any] = {},
        width: float = 1,
        height: float = 1,
        ax: mpl.axes.Axes = None,
        rect_kw: Dict[str, Any] = {},
        col_def: ColumnDefinition | None = None,
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
            col_def=col_def,
        )

        self._plot_fn = plot_fn
        self._plot_kw = plot_kw
        self.fig = self.ax.figure
        self.draw()

    def plot(self):
        self._plot_fn(self.axes_inset, self.content, **self._plot_kw)

    def make_axes_inset(self):
        rect_fig_coords = self._get_rectangle_bounds()
        self.axes_inset = self.fig.add_axes(rect_fig_coords)
        return self.axes_inset

    def _get_rectangle_bounds(self, padding: float = 0.2) -> List[float]:
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


class TextCell(TableCell):
    """A TextCell class for a plottable.table.Table that creates a text inside it's rectangle patch."""

    def __init__(
        self,
        xy: Tuple[float, float],
        content: str | Number,
        row_idx: int,
        col_idx: int,
        width: float = 1,
        height: float = 1,
        ax: mpl.axes.Axes = None,
        rect_kw: Dict[str, Any] = {},
        textprops: Dict[str, Any] = {},
        padding: float = 0.1,
        col_def: ColumnDefinition | None = None,
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
            col_def=col_def,
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

        self.text = self.ax.text(x, y, str(self.content), **self.textprops)

    def _get_text_xy(self):
        x, y = self.xy

        if self.ha == "left":
            x = x + self.padding * self.width
        elif self.ha == "right":
            x = x + (1 - self.padding) * self.width
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
            y = y + (1 - self.padding) * self.height
        elif self.va == "top":
            # CHANGED
            y = y + self.padding * self.height

        return x, y

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(xy={self.xy}, content={self.content}, row_idx={self.index[0]}, col_idx={self.index[1]})"  # noqa


class HighlightTextCell(TextCell):
    """A HighlightTextCell class for a plottable.table.Table that creates a text inside its rectangle patch."""

    def __init__(
        self,
        xy: Tuple[float, float],
        content: str | Number,
        row_idx: int,
        col_idx: int,
        width: float = 1,
        height: float = 1,
        ax: mpl.axes.Axes = None,
        rect_kw: Dict[str, Any] = {},
        textprops: Dict[str, Any] = {},
        highlight_textprops: Dict[str, Any] | None = None,
        padding: float = 0.1,
        col_def: ColumnDefinition | None = None,
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
            textprops=textprops,
            padding=padding,
            col_def=col_def,
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
        xy: Tuple[float, float],
        content: str | Number,
        row_idx: int,
        col_idx: int,
        width: float = 1,
        height: float = 1,
        ax: mpl.axes.Axes = None,
        rect_kw: Dict[str, Any] = {},
        textprops: Dict[str, Any] = {},
        flexitext_props: Dict[str, Any] | None = None,
        padding: float = 0.1,
        col_def: ColumnDefinition | None = None,
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
            textprops=textprops,
            padding=padding,
            col_def=col_def,
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


class RichTextCell(TextCell):
    """A RichTextCell class for a plottable.table.Table that creates a text inside its rectangle patch."""

    def __init__(
        self,
        xy: Tuple[float, float],
        content: str | Number,
        row_idx: int,
        col_idx: int,
        width: float = 1,
        height: float = 1,
        ax: mpl.axes.Axes = None,
        rect_kw: Dict[str, Any] = {},
        textprops: Dict[str, Any] = {},
        rich_textprops: Dict[str, Any] = {},
        padding: float = 0.1,
        col_def: ColumnDefinition | None = None,
        **kwargs,
    ):
        """
        Args:
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
            col_def=col_def,
        )

        self.rich_textprops = rich_textprops

    def set_text(self):
        x, y = self._get_text_xy()

        offsetbox = self._build_text_grid(
            self.content,
            rich_textprops=self.rich_textprops,
            textprops=self.textprops,
        )

        ######
        # Show point of alignement for text
        trans = self.ax.figure.dpi_scale_trans + ScaledTranslation(
            x, y, self.ax.transData
        )

        self.ax.add_artist(Circle((0, 0), 0.05, color="red", transform=trans))

        ######
        self.text = AnnotationBbox(
            offsetbox,
            (x, y),
            # bboxprops=dict(boxstyle="sawtooth"), # only works if frameon=True
            frameon=False,
            box_alignment=(0.5, 0),
            pad=0,
        )

        self.ax.add_artist(self.text)

    def _build_text_grid(
        self,
        texts: CellSequence | str,
        rich_textprops: CellSequence[dict],
        textprops: dict = {},
    ) -> VPacker:
        """_summary_

        Args:
            texts (Sequence | str): _description_
            rich_textprops (Sequence[dict]): _description_
            textprops (dict, optional): _description_. Defaults to {}.

        Raises:
            ValueError: _description_
            ValueError: _description_

        Returns:
            VPacker: _description_
        """

        DEFAULT_TEXTPROPS = {
            "ha": "center",
            "va": "center",
        }

        textprops_value_fn = lambda val: {}
        if isinstance(rich_textprops, Callable):
            textprops_value_fn = rich_textprops
            rich_textprops = {}

        if isinstance(texts, str):
            texts = texts.split("\n")
            # FIXME remove this check
            if len(texts) < 0:
                raise ValueError(
                    "RichTextCell content cannot be a single-line string. Use TextCell instead."
                )

        if all(isinstance(item, str) for item in texts):
            # List of strings - considered as single-column grid
            textarea_grid = []

            for text_line, props_line in zip_longest(
                texts, rich_textprops, fillvalue={}
            ):
                textarea_row = []
                if isinstance(text_line, str):
                    text_line = [text_line]
                for text, props in zip_longest(
                    text_line, props_line, fillvalue=DEFAULT_TEXTPROPS
                ):
                    txtarea_txtprops = props.update(textprops_value_fn(text))
                    textarea_row.append(TextArea(text, textprops=txtarea_txtprops))
                textarea_grid.append(
                    HPacker(children=textarea_row, pad=0, sep=0, align="center")
                )
            return VPacker(children=textarea_grid, pad=0, sep=8, align="center")

        raise ValueError("Invalid format for texts parameter")


class CellSequence:  # Row and Column can inherit from this
    """A Sequence of Table Cells."""

    def __init__(self, cells: List[TableCell], index: int):
        """

        Args:
            cells (List[TableCell]): List of TableCells.
            index (int): an index denoting the sequences place in a Table.
        """
        self.cells = cells
        self.index = index

    def append(self, cell: TableCell):
        """Appends another TableCell to its `cells` propery.

        Args:
            cell (TableCell): A TableCell object
        """
        self.cells.append(cell)

    def set_alpha(self, *args) -> CellSequence:
        """Sets the alpha for all cells of the Sequence and returns self.

        Return:
            self[Sequence]: A Sequence of Cells
        """
        for cell in self.cells:
            cell.rectangle_patch.set_alpha(*args)
        return self

    def set_color(self, *args) -> CellSequence:
        """Sets the color for all cells of the Sequence and returns self.

        Return:
            self[Sequence]: A Sequence of Cells
        """
        for cell in self.cells:
            cell.rectangle_patch.set_color(*args)
        return self

    def set_facecolor(self, *args) -> CellSequence:
        """Sets the facecolor for all cells of the Sequence and returns self.

        Return:
            self[Sequence]: A Sequence of Cells
        """
        for cell in self.cells:
            cell.rectangle_patch.set_facecolor(*args)
        return self

    def set_edgecolor(self, *args) -> CellSequence:
        """Sets the edgecolor for all cells of the Sequence and returns self.

        Return:
            self[Sequence]: A Sequence of Cells
        """
        for cell in self.cells:
            cell.rectangle_patch.set_edgecolor(*args)
        return self

    def set_fill(self, *args) -> CellSequence:
        """Sets the fill for all cells of the Sequence and returns self.

        Return:
            self[Sequence]: A Sequence of Cells
        """
        for cell in self.cells:
            cell.rectangle_patch.set_fill(*args)
        return self

    def set_hatch(self, *args) -> CellSequence:
        """Sets the hatch for all cells of the Sequence and returns self.

        Return:
            self[Sequence]: A Sequence of Cells
        """
        for cell in self.cells:
            cell.rectangle_patch.set_hatch(*args)
        return self

    def set_linestyle(self, *args) -> CellSequence:
        """Sets the linestyle for all cells of the Sequence and returns self.

        Return:
            self[Sequence]: A Sequence of Cells
        """
        for cell in self.cells:
            cell.rectangle_patch.set_linestyle(*args)
        return self

    def set_linewidth(self, *args) -> CellSequence:
        """Sets the linewidth for all cells of the Sequence and returns self.

        Return:
            self[Sequence]: A Sequence of Cells
        """
        for cell in self.cells:
            cell.rectangle_patch.set_linewidth(*args)
        return self

    def set_fontcolor(self, *args) -> CellSequence:
        """Sets the fontcolor for all cells texts of the Sequence and returns self.

        Return:
            self[Sequence]: A Sequence of Cells
        """
        for cell in self.cells:
            if hasattr(cell, "text"):
                cell.text.set_color(*args)
        return self

    def set_fontfamily(self, *args) -> CellSequence:
        """Sets the fontfamily for all cells texts of the Sequence and returns self.

        Return:
            self[Sequence]: A Sequence of Cells
        """
        for cell in self.cells:
            if hasattr(cell, "text"):
                cell.text.set_fontfamily(*args)
        return self

    def set_fontsize(self, *args) -> CellSequence:
        """Sets the fontsize for all cells texts of the Sequence and returns self.

        Return:
            self[Sequence]: A Sequence of Cells
        """
        for cell in self.cells:
            if hasattr(cell, "text"):
                cell.text.set_fontsize(*args)
        return self

    def set_fontstyle(self, *args) -> CellSequence:
        """Sets the fontsize for all cells texts of the Sequence and returns self.

        Return:
            self[Sequence]: A Sequence of Cells
        """
        for cell in self.cells:
            if hasattr(cell, "text"):
                cell.text.set_fontstyle(*args)
        return self

    def set_ha(self, *args) -> CellSequence:
        """Sets the horizontal alignment for all cells texts of the Sequence and returns self.

        Return:
            self[Sequence]: A Sequence of Cells
        """
        for cell in self.cells:
            if hasattr(cell, "text"):
                cell.text.set_ha(*args)
        return self

    def set_ma(self, *args) -> CellSequence:
        """Sets the multialignment for all cells tests of the Sequence and returns self.

        Return:
            self[Sequence]: A Sequence of Cells
        """
        for cell in self.cells:
            if hasattr(cell, "text"):
                cell.text.set_ma(*args)
        return self


class Row(CellSequence):
    """A Row of TableCells."""

    def __init__(self, cells: List[TableCell], index: int):
        super().__init__(cells=cells, index=index)

    @property
    def xrange(self) -> Tuple[float, float]:
        """Gets the xrange of the Row.

        Returns:
            Tuple[float, float]: Tuple of min and max x.
        """
        return min([cell.xy[0] for cell in self.cells]), max(
            [cell.xy[0] + cell.width for cell in self.cells]
        )

    @property
    def yrange(self) -> Tuple[float, float]:
        """Gets the yrange of the Row.

        Returns:
            Tuple[float, float]: Tuple of min and max y.
        """
        cell = self.cells[0]
        return cell.xy[1], cell.xy[1] + cell.height

    @property
    def x(self) -> float:
        return self.cells[0].xy[0]

    @property
    def y(self) -> float:
        return self.cells[0].xy[1]

    @property
    def height(self) -> float:
        return self.cells[0].height

    def __repr__(self) -> str:
        return f"Row(cells={self.cells}, index={self.index})"


class Column(CellSequence):
    """A Column of TableCells."""

    def __init__(self, cells: List[TableCell], index: int, name: str = None):
        super().__init__(cells=cells, index=index)
        self.name = name

    @property
    def xrange(self) -> Tuple[float, float]:
        """Gets the xrange of the Column.

        Returns:
            Tuple[float, float]: Tuple of min and max x.
        """
        cell = self.cells[0]
        return cell.xy[0], cell.xy[0] + cell.width

    @property
    def yrange(self) -> Tuple[float, float]:
        """Gets the yrange of the Column.

        Returns:
            Tuple[float, float]: Tuple of min and max y.
        """
        return min([cell.xy[1] for cell in self.cells]), max(
            [cell.xy[1] + cell.height for cell in self.cells]
        )

    @property
    def x(self) -> float:
        return self.cells[0].xy[0]

    @property
    def y(self) -> float:
        return self.cells[0].xy[1]

    @property
    def width(self) -> float:
        return self.cells[0].width

    def __repr__(self) -> str:
        return f"Column(cells={self.cells}, index={self.index})"
