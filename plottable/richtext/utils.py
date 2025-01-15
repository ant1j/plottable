from collections.abc import Callable, Iterable
from typing import Any


def depth(seq: Any) -> int:
    if iterable_not_string(seq):
        return 1 + max(depth(item) for item in seq) if seq else 1
    else:
        return 0


def apply(func: Callable, data):
    """
    Recursively applies `func` to every non-iterable element
    in `data`, where `data` can be a nested list or tuple.
    """
    # Check if 'data' is a list or tuple, and not an empty one
    if iterable_not_string(data) and data:
        # Recursively apply func to each element
        return type(data)(apply(func, x) for x in data)
    else:
        # Base case: not a list/tuple, so apply func directly
        return func(data)


# https://github.com/pandas-dev/pandas/blob/main/pandas/core/dtypes/inference.py#L78
def iterable_not_string(obj: object) -> bool:
    """
    Check if the object is an iterable but not a string.

    Parameters
    ----------
    obj : The object to check.

    Returns
    -------
    is_iter_not_string : bool
        Whether `obj` is a non-string iterable.

    Examples
    --------
    >>> iterable_not_string([1, 2, 3])
    True
    >>> iterable_not_string("foo")
    False
    >>> iterable_not_string(1)
    False
    """
    return isinstance(obj, Iterable) and not isinstance(obj, str)


# https://github.com/pandas-dev/pandas/blob/main/pandas/core/common.py#L50
def flatten(line):
    """
    Flatten an arbitrarily nested sequence.

    Parameters
    ----------
    line : sequence
        The non string sequence to flatten

    Notes
    -----
    This doesn't consider strings sequences.

    Returns
    -------
    flattened : generator
    """
    for element in line:
        if iterable_not_string(element):
            yield from flatten(element)
        else:
            yield element


def is_multiline(text: str, strip=True):
    text = text.strip() if strip else text

    return len(text.splitlines()) > 1
