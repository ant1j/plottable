from __future__ import annotations

from plottable.basecell import TableCell


class CellSequence:  # Row and Column can inherit from this
    """A Sequence of Table Cells."""

    def __init__(self, cells: list[TableCell], index: int):
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

    def __init__(self, cells: list[TableCell], index: int):
        super().__init__(cells=cells, index=index)

    @property
    def xrange(self) -> tuple[float, float]:
        """Gets the xrange of the Row.

        Returns:
            Tuple[float, float]: Tuple of min and max x.
        """
        return min([cell.xy[0] for cell in self.cells]), max(
            [cell.xy[0] + cell.width for cell in self.cells]
        )

    @property
    def yrange(self) -> tuple[float, float]:
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

    def __init__(self, cells: list[TableCell], index: int, name: str = None):
        super().__init__(cells=cells, index=index)
        self.name = name

    @property
    def xrange(self) -> tuple[float, float]:
        """Gets the xrange of the Column.

        Returns:
            Tuple[float, float]: Tuple of min and max x.
        """
        cell = self.cells[0]
        return cell.xy[0], cell.xy[0] + cell.width

    @property
    def yrange(self) -> tuple[float, float]:
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
