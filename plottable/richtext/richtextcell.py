from __future__ import annotations

from itertools import zip_longest
from numbers import Number
from typing import Any, Callable, Dict, Sequence, Tuple

from matplotlib.axes import Axes
from matplotlib.offsetbox import AnnotationBbox, HPacker, TextArea, VPacker

from plottable.basecell import TextCell
from plottable.column_def import RichTextColumnDefinition


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
        ax: Axes = None,
        rect_kw: Dict[str, Any] = {},
        textprops: Dict[str, Any] = {},
        rich_textprops: Dict[str, Any] = {},
        padding: float = 0.1,
        column_definition: RichTextColumnDefinition | None = None,
        **kwargs,
    ):
        """ """
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

        self.rich_textprops = rich_textprops

        # if rich_textprops:
        #     self.rich_textprops = rich_textprops
        # else:
        #     if self.column_definition:
        #         self.rich_textprops = self.column_definition.get("richtext_props")

        # if not self.rich_textprops:
        #     self.rich_textprops = lambda x: {}

    def set_text(self):
        x, y = self._get_text_xy()

        content = self.format_content()

        offsetbox = self._build_text_grid(
            content,
            rich_textprops=self.rich_textprops,
            textprops=self.textprops,
        )

        ######
        # Show point of alignement for text

        # trans = self.ax.figure.dpi_scale_trans + ScaledTranslation(
        #     x, y, self.ax.transData
        # )

        # self.ax.add_artist(Circle((0, 0), 0.05, color="red", transform=trans))

        ######
        self.text = AnnotationBbox(
            offsetbox,
            (x, y),
            # bboxprops=dict(boxstyle="sawtooth"),  # only works if frameon=True
            frameon=False,
            pad=0,  # apply to the frame / bbox only; not within the text Packers
            #
            # ha = 'right' => 1; va = 'center' => 0.5
            box_alignment=(1, 0.5),
        )

        self.ax.add_artist(self.text)

    def format_content(self):
        print(self.content)
        return self.content
        # return super().format_content()

    def _build_text_grid(
        self,
        texts: Sequence | str,
        rich_textprops: Sequence[dict],
        textprops: dict = {},
    ) -> VPacker:
        """_summary_

        Args:
            texts (Sequence | str): _description_
            rich_textprops (Sequence[dict]):
                Sequence of textproperty to apply to the relevant text it refers to.
                Its structure should strictly follow the `texts` structure
            textprops (dict, optional): properties to be applied to each span of text. Defaults to {}.

        Raises:
            ValueError: _description_
            ValueError: _description_

        Returns:
            VPacker: _description_
        """

        DEFAULT_TEXTPROPS = {
            "ha": "right",
            "va": "center",
            # "style": "italic",
            # "color": "red",
        }

        # FIXME Probably not the right way
        textprops_value_fn = lambda val: {}
        if isinstance(rich_textprops, Callable):
            textprops_value_fn = rich_textprops
            rich_textprops = {}

        # TODO
        # Here we need to:
        # * check if it is a list
        # * Apply the number formatter to the value (should be a number [? or not...])
        # * Retrieve the potential textprops to apply
        #
        # There are 2 dimensions here between the number format (eg ".1f") and the 'textprops' (eg. color=green, weight=bold...)
        # There should be addressed separately

        if isinstance(texts, str):
            texts = texts.split("\n")
            # FIXME remove this check
            if len(texts) < 0:
                raise ValueError(
                    "RichTextCell content cannot be a single-line string. Use TextCell instead."
                )

        # FIXME if we have list of number (now probably the most frequent case), this fails
        if all(isinstance(item, str) for item in texts) or 1:
            # List of strings - considered as single-column grid
            textarea_grid = []

            # IDEA `rich_textprops`. `props_line`, `props` should be replaced by a `style` thing that manage itself to apply to the content
            # TODO Deal with 1D first, then with 2D (YAGNI anyway)
            for text_line, props_line in zip_longest(
                texts, rich_textprops, fillvalue={}
            ):
                textarea_row = []
                if not isinstance(text_line, Sequence) or isinstance(text_line, str):
                    text_line = [text_line]
                for text, props in zip_longest(
                    text_line, props_line, fillvalue=DEFAULT_TEXTPROPS
                ):
                    props.update(
                        textprops_value_fn(text)
                        | self.column_definition.richtext_props(text)
                    )  # update returns None. Do not assign
                    text = self.column_definition.formatter(text)
                    textarea_row.append(TextArea(text, textprops=props))
                textarea_grid.append(
                    HPacker(children=textarea_row, pad=0, sep=0, align="center")
                )
            return VPacker(children=textarea_grid, pad=0, sep=4, align="center")

        raise ValueError("Invalid format for texts parameter")
