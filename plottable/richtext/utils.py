from collections.abc import Callable, Iterable, Mapping
from typing import Any, TypeVar


def depth(seq: Any) -> int:
    if iterable_not_string(seq) and not isinstance(seq, Mapping):
        return 1 + max(depth(item) for item in seq) if seq else 1
    else:
        return 0


T = TypeVar("T")


def apply(func: Callable, data: T) -> T:
    """
    Recursively applies `func` to every non-iterable element
    in `data`, where `data` can be a nested list or tuple.
    """
    # Check if 'data' is a list or tuple, and not an empty one
    if iterable_not_string(data) and data:
        # Recursively apply func to each element
        return type(data)(apply(func, x) for x in data)  # type: ignore
    else:
        # Base case: not a list/tuple, so apply func directly
        return func(data)


def apply_to_list(func: Callable, data: T) -> T:
    """
    Recursively applies `func` to every non-iterable element
    in `data`, where `data` can be a nested list or tuple.
    """
    # Check if 'data' is a list or tuple, and not an empty one
    if isinstance(data, list) and data:
        # Recursively apply func to each element
        return list(apply_to_list(func, x) for x in data)  # type: ignore
    else:
        # Base case: not a list/tuple, so apply func directly
        return func(data)


def _dict_to_funcdict(props_formatter):
    """IF we have dicts in, we want functions returning those dicts out."""

    def lamdaize_dict(dict_call):
        return dict_call if callable(dict_call) else (lambda x: dict_call)

    return apply_to_list(lamdaize_dict, props_formatter)


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


if __name__ == "__main__":
    import wat

    group_label_style = [
        dict(fontsize=14, weight="demibold"),
        dict(style="italic"),
    ]

    wat.short(group_label_style)
    wat.short(_dict_to_funcdict(group_label_style))
    print()
