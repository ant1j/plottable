from typing import Protocol

from plottable.richtext.utils import depth


class Content(Protocol):
    def format(self, formatter): ...


class ScalarContent(Content):
    dim: int = 0

    def __init__(self, content):
        self.content = content

    def format(self, formatter):
        """Delegate to the formatter's logic for scalar content."""
        return formatter.format_content(self.content)


class ListContent(Content):
    dim: int = 1

    def __init__(self, content):
        self.content = content

    def format(self, formatter):
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
