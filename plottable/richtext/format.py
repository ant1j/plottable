from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from numbers import Number
from typing import Any, Sequence

from plottable.richtext.content import make_content
from plottable.richtext.formatters import make_formatter
from plottable.richtext.utils import (
    _dict_to_funcdict,
    apply_to_list,
    iterable_not_string,
)


def richformat(data, formatter: Callable):
    """
    Create the appropriate Content and Formatter objects,
    then apply the latter to the former.
    """
    content_obj = make_content(data)
    formatter_obj = make_formatter(formatter)
    return content_obj.format(formatter_obj)


@dataclass
class RichContent:
    value: Any
    formatted_value: str
    style_props: dict = field(default_factory=dict)


@dataclass
class RichContentSequence:
    values: str | Sequence
    formatted_values: str | Sequence
    style_props: dict = field(default_factory=dict)

    @classmethod
    def from_formatting_funcs(
        cls, data: Sequence | str, values_formatter=None, props_formatter=None
    ) -> RichContentSequence:
        if isinstance(data, str):
            data = data.splitlines()

        values_formatter = values_formatter or str
        props_formatter = _dict_to_funcdict(props_formatter or (lambda x: {}))

        formatted_values = richformat(data=data, formatter=values_formatter)
        style_props = richformat(data=data, formatter=props_formatter)

        return cls(
            values=data, formatted_values=formatted_values, style_props=style_props
        )

    def _dict_to_funcdict(self, props_formatter):
        """IF we have dicts in, we want functions returning those dicts out."""

        def lamdaize_dict(dict_call):
            return dict_call if callable(dict_call) else (lambda x: dict_call)

        return apply_to_list(lamdaize_dict, props_formatter)

    def to_dict(self):
        return asdict(self)

    def to_records(self, data=None) -> list[RichContent] | list[list[RichContent]]:
        if data is None:
            values, formatted_values, style_props = (
                self.values,
                self.formatted_values,
                self.style_props,
            )
        else:
            # recursion
            values, formatted_values, style_props = data

        records = []
        for val, fmt_val, props in zip(values, formatted_values, style_props):
            if iterable_not_string(val):
                records.append(self.to_records(data=(val, fmt_val, props)))
            else:
                records.append(
                    RichContent(
                        **{
                            "value": val,
                            "formatted_value": fmt_val,
                            "style_props": props,
                        }
                    )
                )
        return records


def apply_rich_formatting(data, values_formatter=None, props_formatter=None):
    return RichContentSequence.from_formatting_funcs(
        data=data, values_formatter=values_formatter, props_formatter=props_formatter
    ).to_dict()


if __name__ == "__main__":
    import wat

    data = [[0.306134, -0.0617, 0.043836, 0], [0.306134, -0.0617, 0.043836, 0]]

    def pick_colour(val: Number):
        if val < -0.05:
            return "darkred"
        elif val > 0.05:
            return "darkgreen"
        else:
            return "dimgray"

    def fontcolour_from_value(val: Any):
        if isinstance(val, Number):
            return dict(color=pick_colour(val))
        return {}

    def pct(x):
        if isinstance(x, Number):
            return f"{x:+.0%}"
        return x

    # rc = RichContentSequence.from_formatting_funcs(
    #     data=data[0], values_formatter=pct, props_formatter=fontcolour_from_value
    # )

    # # res = apply_rich_formatting(
    # #     data=data, values_formatter=pct, props_formatter=fontcolour_from_value
    # # )
    # wat.short(rc.to_dict())
    # wat.short(list(rc.to_records()))

    group_label_style = [
        dict(fontsize=14, weight="demibold"),
        dict(style="italic"),
    ]

    rc2 = RichContentSequence.from_formatting_funcs(
        data="Entry T.O.\n(2023)",
        values_formatter=pct,
        props_formatter=group_label_style,
    )

    # wat.short(rc2.to_dict())
    wat.short(list(rc2.to_records()))
