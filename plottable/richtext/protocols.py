from collections.abc import Sequence
from typing import Protocol


class Content(Protocol):
    def format(self, formatter) -> str: ...


class Formatter(Protocol):
    def format_content(self, value) -> str: ...

    def format_content_sequence(self, values) -> Sequence[str]: ...

    def format_content_nested(self, values) -> Sequence[Sequence[str]]: ...
