from collections.abc import Callable
from dataclasses import dataclass
from itertools import zip_longest
from typing import Any, Self, Sequence

from plottable.richtext.formatters import _init_formatters
from plottable.richtext.utils import is_multiline, iterable_not_string

type FormattingFunction = Callable[[Any], str]


class RichTextContainer:
    def __init__(
        self,
        content: Sequence | str = "",
        styles: Sequence | dict | None = None,
        formatters: Any = str,
    ):
        self.content = _init_content(content)
        self.styles = styles

        self.formatters = _init_formatters(formatters)

    def _init_content(self, content):
        return _init_content(content)

    def format(self, with_styles=False):
        # print(self.formatters(self.content))

        # 1. its a 1-item formatter
        if callable(self.formatters):
            print("Callable 1-item self.formatters")

            # content is a string or a 'scalar' value (not iterable)
            if not iterable_not_string(self.content):
                formatted = self.formatters(self.content)

            # content is iterable => apply the 1-item formatter to all items
            elif iterable_not_string(self.content):
                formatted = [
                    self.formatters(cell_content) for cell_content in self.content
                ]

            # content is 2D iterable => apply the 1-item formatter to all items
            elif iterable_not_string(self.content) and all(
                iterable_not_string(content) for content in self.content
            ):
                formatted = [
                    [self.formatters(cell_content) for cell_content in cell_row]
                    for cell_row in self.content
                ]

            # TODO We clearly see a pattern here where we could recursively apply to each nested levels... but is it worth it?

            # content is something else => complain
            else:
                raise ValueError(
                    f"Applying formatters ({self.formatters}) to this content ({self.content}) is not possible."
                )

        # 2. its a 1D iterable formatter
        elif iterable_not_string(self.formatters):
            print("1D self.formatters")

            # content is a string or a 'scalar' value (not iterable)
            if not iterable_not_string(self.content):
                raise ValueError(
                    f"Applying 1-dimensional formatters ({self.formatters}) to this content ({self.content}) is not possible: \nWhich formatter to use?"
                )

            # content is iterable => apply each formatter to each item in the sequence
            elif iterable_not_string(self.content):
                formatted = [
                    formatter(cell_content)
                    for cell_content, formatter in zip_longest(
                        self.content, self.formatters, fillvalue=str
                    )
                ]

            # content is 2D iterable => apply each formatter to each row of items
            elif iterable_not_string(self.content) and all(
                iterable_not_string(content) for content in self.content
            ):
                formatted = [
                    [formatter(cell_content) for cell_content in content_row]
                    for content_row, formatter in zip_longest(
                        self.content, self.formatters, fillvalue=str
                    )
                ]

            else:
                raise ValueError(
                    f"Applying multi-dimensional formatters ({self.formatters}) to a string ({self.content}) is not possible."
                )

        # 3. its a 2D iterable formatter
        elif iterable_not_string(self.formatters) and all(
            iterable_not_string(fmt) for fmt in self.formatters
        ):
            print("2D self.formatters")

            # content is a string or a 'scalar' value (not iterable)
            if not iterable_not_string(self.content):
                raise ValueError(
                    f"Cannot apply 2-dimensional formatters ({self.formatters}) to this content ({self.content}).\n"
                    "Which formatter to use?"
                )

            # content is iterable => apply each formatter to each item in the sequence
            elif iterable_not_string(self.content):
                raise ValueError(
                    f"Cannot apply 2-dimensional formatters ({self.formatters}) to 1-d content ({self.content}).\n"
                    "Which formatter to use?"
                )

            # content is 2D iterable => apply each formatter to each items
            elif iterable_not_string(self.content) and all(
                iterable_not_string(content) for content in self.content
            ):
                formatted = [
                    [
                        cell_formatter(cell_content)
                        for cell_content, cell_formatter in zip_longest(
                            content_row, formatter_row, fillvalue=str
                        )
                    ]
                    for content_row, formatter_row in zip(self.content, self.formatters)
                ]

        else:
            raise ValueError(
                f"Cannot apply formatters ({self.formatters}) to content ({self.content})."
            )

        if with_styles:
            return formatted, self.styles
        return formatted


def _init_content(content) -> Sequence:
    """Convert the `content` parameter to a suitable format

    This will split multi-line text to list of strings, recursively.


    Args:
        content (Any): the input content

    Returns:
        Any: structured content to be processed
    """
    if isinstance(content, str):
        if is_multiline(content):
            return content.strip().splitlines()
        return content

    if iterable_not_string(content):
        return [_init_content(inner_content) for inner_content in content]

    return content


@dataclass
class Formatter:
    formatter: Callable[[Any], str]

    @classmethod
    def init(cls, formatter=None) -> Self:
        if formatter is None:
            return cls(str)
        if isinstance(formatter, str):
            # should be a string format:
            return cls(formatter.format)
        else:
            raise ValueError()

    def format(self, content: Any) -> str:
        return self.formatter(content)


@dataclass
class FormatterList:
    formatters: list[Formatter]

    @classmethod
    def init(cls, formatter=None):
        if formatter is None:
            return cls(formatters=[Formatter.init(formatter)])
        if isinstance(formatter, str):
            # should be a string format:
            return cls(formatter.format)

    def format(self, content: Any) -> str:
        return self.formatters(content)


def apply_formatters(content, formatters):
    if callable(formatters):
        # We have only one function/callable, apply.
        pass
