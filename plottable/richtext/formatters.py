from itertools import zip_longest
from typing import Protocol, Sequence, TypeVar, runtime_checkable

from plottable.richtext.content import ListContent, ScalarContent
from plottable.richtext.protocols import Formatter
from plottable.richtext.utils import apply, depth

T = TypeVar("T")


def _init_formatters(formatters: T) -> T:
    def to_default_formatter(fmt):
        fmt = str if not fmt else fmt
        if isinstance(fmt, str):
            fmt = fmt.format

        if not callable(fmt):
            raise TypeError(
                f"formatter {fmt} should be a callable, or converted to a callable by now."
            )

        return fmt

    return apply(to_default_formatter, formatters)


@runtime_checkable
class FormatFunction(Protocol):
    def __call__(self, Any) -> str: ...


class ScalarFormatter:
    def __init__(self, formatters: FormatFunction):
        self.formatters = _init_formatters(formatters)

    def format_content(self, value) -> str:
        return self.formatters(value)

    def format_content_sequence(self, content) -> Sequence[str]:
        # Apply the single callable to each item
        return [self.format_content(value) for value in content]

    def format_content_nested(self, content):
        # Recursively apply the single callable to each item in the nested list
        return [self.format_content_sequence(row) for row in content]


class ListFormatter:
    def __init__(self, formatters: Sequence[FormatFunction]):
        # funcs could be a list of callables or nested lists of callables
        self.formatters = _init_formatters(formatters)

    def format_content(self, content) -> str:
        raise NotImplementedError("Cannot use a ListFormatter for a ScalarContent.")

    def format_content_sequence(self, content_seq) -> Sequence[str]:
        formatters = self.formatters

        # result = []
        # for content, formatter in zip_longest(content_seq, formatters, fillvalue=str):
        #     # print(content, formatter.__qualname__)
        #     sc = ScalarContent(content)
        #     # print(sc)
        #     sf = ScalarFormatter(formatter)
        #     # print(sf)
        #     result.append(sc.format(sf))

        # return result

        return [
            ScalarContent(content).format(ScalarFormatter(formatter))
            for content, formatter in zip_longest(
                content_seq,
                formatters,
                fillvalue=str,
            )
        ]

    def format_content_nested(self, content) -> Sequence[Sequence[str]]:
        # return [self.format_content_sequence(row, self.formatters) for row in content]
        formatters = self.formatters

        # result = []
        # for content_row, formatter_row in zip_longest(
        #     content, formatters, fillvalue=str
        # ):
        #     # print(content_row, formatter_row.__qualname__)
        #     lc = ListContent(content_row)
        #     # print(lc)
        #     sf = ScalarFormatter(formatter_row)
        #     # print(lc)
        #     result.append(lc.format(sf))

        # return result

        return [
            ListContent(content_row).format(ScalarFormatter(formatter_row))
            for content_row, formatter_row in zip_longest(
                content, formatters, fillvalue=str
            )
        ]


class MatrixFormatter:
    def __init__(self, formatters: Sequence[Sequence[FormatFunction]]):
        # funcs could be a list of callables or nested lists of callables
        self.formatters = _init_formatters(formatters)

    def format_content(
        self,
        content,
    ) -> str:
        raise NotImplementedError("Cannot use a MatrixFormatter for a ScalarContent.")

    def format_content_sequence(self, content) -> Sequence[str]:
        raise NotImplementedError("Cannot use a MatrixFormatter for a ListContent.")

    def format_content_nested(self, content) -> Sequence[Sequence[str]]:
        formatters = self.formatters
        return [
            ListContent(content_row).format(ListFormatter(formatter_row))
            for content_row, formatter_row in zip_longest(
                content, formatters, fillvalue=[str]
            )
        ]


#########################################


#
# Factory function to produce the correct Formatter subclass
#
def make_formatter(f) -> Formatter:
    _DEPTH_TO_FORMATTERS = {
        0: ScalarFormatter,
        1: ListFormatter,
        2: MatrixFormatter,
    }

    formatter_class = _DEPTH_TO_FORMATTERS[depth(f)]

    return formatter_class(f)
