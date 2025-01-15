from collections.abc import Sequence

from plottable.richtext.protocols import Content, Formatter
from plottable.richtext.utils import depth


class ScalarContent(Content):
    """A class to hold a scalar value, knowing that string is consider as such here."""

    dim: int = 0

    def __init__(self, content):
        """Init ScalarContent

        Args:
            content (Any): the scalar-like content
        """
        self.content = content

    def format(self, formatter: Formatter) -> str:
        """Format the Scalar Content."""
        return formatter.format_content(self.content)


class ListContent(Content):
    """A class to hold list-like values, knowing that string are not consider as such here."""

    dim: int = 1

    def __init__(self, content):
        self.content = content

    def format(self, formatter: Formatter) -> Sequence[str]:
        """Delegate to the formatter's logic for list content."""
        return formatter.format_content_sequence(self.content)


class NestedListContent(Content):
    dim: int = 2

    def __init__(self, content):
        self.content = content  # e.g., [["Hello", "World"], ["Foo", "Bar"]]

    def format(self, formatter):
        """Delegate to the formatter's logic for nested-list content."""
        return formatter.format_content_nested(self.content)


#
# Helper function to produce the correct Content subclass
#
def make_content(data):
    _DEPTH_TO_CONTENT = {
        0: ScalarContent,
        1: ListContent,
        2: NestedListContent,
    }

    content_class = _DEPTH_TO_CONTENT[depth(data)]

    return content_class(data)
