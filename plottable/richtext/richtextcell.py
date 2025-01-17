from __future__ import annotations

from collections import ChainMap
from itertools import zip_longest
from numbers import Number
from typing import Any, Callable, Sequence

from matplotlib.axes import Axes
from matplotlib.offsetbox import AnnotationBbox, HPacker, TextArea, VPacker

from plottable.basecell import TextCell
from plottable.column_def import RichTextColumnDefinition
from plottable.richtext.format import RichContentSequence


class RichTextCell(TextCell):
    """A RichTextCell class for a RichTable that creates a text inside its rectangle patch."""

    HORIZONTAL_ALIGNMENT = {"center": 0.5, "left": 0, "right": 1}
    VERTICAL_ALIGNMENT = {"center": 0.5, "top": 1, "bottom": 0}

    def __init__(
        self,
        xy: tuple[float, float],
        content: str | Number,
        row_idx: int,
        col_idx: int,
        width: float = 1,
        height: float = 1,
        ax: Axes = None,
        rect_kw: dict[str, Any] = {},
        padding: float = 0.05,
        textprops: dict[str, Any] = {},
        rich_textprops: dict[str, Any] = {},
        boxprops: dict[str, Any] = {},
        values_formatter: Callable = str,
        textprops_formatter: Callable | None = None,
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
        self.boxprops = boxprops
        self.values_formatter = (
            values_formatter or self.column_definition.get("formatter") or str
        )
        self.textprops_formatter = textprops_formatter

        # if rich_textprops:
        #     self.rich_textprops = rich_textprops
        # else:
        #     if self.column_definition:
        #         self.rich_textprops = self.column_definition.get("richtext_props")

        # if not self.rich_textprops:
        #     self.rich_textprops = lambda x: {}

    def set_text(self):
        x, y = self._get_text_xy()

        # offsetbox = self._build_text_grid(
        #     self.content, rich_textprops=self.rich_textprops
        # )

        offsetbox = self._build_content(content=self.content)

        ######
        # Show point of alignement for text
        # self.ax.add_artist(
        #     Circle(
        #         (0, 0),
        #         0.05,
        #         color="red",
        #         transform=self.ax.figure.dpi_scale_trans
        #         + ScaledTranslation(x, y, self.ax.transData),
        #     )
        # )
        ######

        self.text = AnnotationBbox(
            offsetbox,
            (x, y),
            bboxprops=dict(
                boxstyle="square", lw=1, ec="lightpink"
            ),  # only works if frameon=True
            frameon=False,
            pad=0,  # apply to the frame / bbox only; not within the text Packers
            #
            # ha = 'right' => 1; va = 'center' => 0.5
            #
            # Defines how the Box will be drawn, from the reference point xy
            # (0.5, 0.5) = ref point is in the middle of the bbox (5 on a numpad)
            # (1, 0.5) = ref point is on the right side, middle vertically ('6' on a numpad)
            box_alignment=(
                self.HORIZONTAL_ALIGNMENT[self.textprops.get("ha", "right")],
                self.VERTICAL_ALIGNMENT[self.textprops.get("va", "center")],
            ),
        )

        self.ax.add_artist(self.text)

    def _build_text_grid(
        self,
        content: Sequence | str,
        rich_textprops: Sequence[dict],
        textprops: dict = {},
        boxprops: dict | ChainMap = {},
    ) -> VPacker:
        """_summary_

        Args:
            texts (Sequence | str): _description_
            rich_textprops (Sequence[dict]):
                Sequence of textproperty to apply to the relevant text it refers to.
                Its structure should strictly follow the `texts` structure
            textprops (dict, optional): properties to be applied to each span of text. Defaults to {}.



        Returns:
            VPacker: _description_
        """

        DEFAULT_TEXTPROPS = {
            "ha": "right",
            "va": "center",
            # "style": "italic",
            # "color": "red",
        }

        boxprops = ChainMap(boxprops, self.boxprops, dict(ha="center", va="center"))

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

        if isinstance(content, str):
            content = content.splitlines()

        # FIXME if we have list of number (now probably the most frequent case), this fails
        if all(isinstance(item, str) for item in content) or 1:
            # List of strings - considered as single-column grid
            textarea_grid = []

            # IDEA `rich_textprops`. `props_line`, `props` should be replaced by a `style` thing that manage itself to apply to the content
            # TODO Deal with 1D first, then with 2D (YAGNI anyway)
            for text_line, props_line in zip_longest(
                content, rich_textprops, fillvalue={}
            ):
                textarea_row = []
                if not isinstance(text_line, Sequence) or isinstance(text_line, str):
                    text_line = [text_line]
                if isinstance(props_line, dict):
                    props_line = [props_line]

                for text, props in zip_longest(
                    text_line, props_line, fillvalue=DEFAULT_TEXTPROPS
                ):
                    col_def_props = {}
                    fmtter = str

                    if self.column_definition:
                        col_def_props = self.column_definition.richtext_props(text)
                        fmtter = self.column_definition.formatter

                    # print(props)

                    props.update(
                        textprops_value_fn(text) | col_def_props
                    )  # update returns None. Do not assign
                    text = fmtter(text)

                    txtp = (
                        props
                        | dict(
                            ha="center",
                            va="baseline",  # FIXME This is key to get the right centered overall (VPacker) within the AnnotationBBox
                            # bbox=dict(
                            #         boxstyle="square,pad=0",
                            #         facecolor="none",
                            #         edgecolor="black",
                            #     ),
                        )
                    )

                    textarea_row.append(TextArea(text, textprops=txtp))

                textarea_grid.append(
                    HPacker(children=textarea_row, pad=0, sep=0, align=boxprops["va"])
                )

            return VPacker(
                children=textarea_grid,
                pad=0,
                # Space between the children
                sep=4,
                # defines how the children are aligned - this should use the `textprops` defined early
                # We want the richcell content (a group of text) to align just like a regular text
                align=boxprops["ha"],
            )

        raise ValueError("Invalid format for texts parameter")

    def _build_content(
        self,
        content: Sequence | str,
    ) -> VPacker:
        """Build Content"""

        boxprops = dict(ha="center", va="center") | self.boxprops

        if isinstance(self.rich_textprops, Callable):
            print("Use textprops_formatter now please")

        textprops_formatter = (
            self.textprops_formatter
            or self.rich_textprops
            or self.column_definition.richtext_props
            or (lambda x: {})
        )

        rich_content_seq = RichContentSequence.from_formatting_funcs(
            data=content,
            values_formatter=self.values_formatter,
            props_formatter=textprops_formatter,
        )

        textarea_grid = []
        for rc_seq in rich_content_seq.to_records():
            textarea_row = []

            if not isinstance(rc_seq, Sequence):
                rc_seq = [rc_seq]

            for rich_content in rc_seq:
                textarea_row.append(
                    TextArea(
                        rich_content.formatted_value, textprops=rich_content.style_props
                    )
                )

            textarea_grid.append(
                HPacker(children=textarea_row, pad=0, sep=0, align=boxprops["va"])
            )

        return VPacker(
            children=textarea_grid,
            pad=0,
            # Space between the children
            sep=4,
            # defines how the children are aligned - this should use the `textprops` defined early
            # We want the richcell content (a group of text) to align just like a regular text
            align=boxprops["ha"],
        )

    def __getattr__(self, attr):
        print(f"trying to call {attr}")
        return
