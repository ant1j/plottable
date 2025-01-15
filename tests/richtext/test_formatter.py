from itertools import product

import pytest

import plottable.richtext.container as container
from plottable.richtext.utils import depth
from tests.conftest import parametrize


@pytest.fixture
def list_content():
    return ["a test", "from a list"]


@pytest.fixture
def func_dict():
    return dict(
        upper=str.upper,
        reverse=lambda x: x[::-1],
        lower=str.lower,
        wrap_with_=lambda x: f"_{x}_",
    )


@pytest.fixture
def contents():
    return {
        "0D": "Hello",
        "1D": ["Hello", "World"],
        "2D": [["Hello", "World"], ["Foo", "Bar"]],
    }


@pytest.fixture
def formatters(func_dict):
    d = func_dict
    return {
        "0D upper": d["upper"],
        "1D upper, reverse": [d["upper"], d["reverse"]],
        "1D reverse short by 1": [d["reverse"]],
        "2D up/lower, wrap/None": [[d["upper"], d["lower"]], [d["wrap_with_"], None]],
    }


@pytest.fixture
def expected_formats(contents, func_dict):
    return {
        ("0D", "0D upper"): "HELLO",
        ("0D", "1D upper, reverse"): None,
        ("0D", "1D reverse short by 1"): None,
        ("0D", "2D up/lower, wrap/None"): None,
        #
        ("1D", "0D upper"): ["HELLO", "WORLD"],
        ("1D", "1D upper, reverse"): ["HELLO", "dlroW"],
        ("1D", "1D reverse short by 1"): ["olleH", "World"],
        ("1D", "2D up/lower, wrap/None"): None,
        #
        ("2D", "0D upper"): [["HELLO", "WORLD"], ["FOO", "BAR"]],
        ("2D", "1D upper, reverse"): [["HELLO", "WORLD"], ["ooF", "raB"]],
        ("2D", "1D reverse short by 1"): [["olleH", "dlroW"], ["Foo", "Bar"]],
        ("2D", "2D up/lower, wrap/None"): [["HELLO", "world"], ["_Foo_", "Bar"]],
    }


def test_with_multiple_cases(contents, formatters, expected_formats):
    for (cname, content), (fname, formatter) in product(
        contents.items(), formatters.items()
    ):
        content_depth, formatter_depth = depth(content), depth(formatter)
        expected = expected_formats[(cname, fname)]
        if content_depth < formatter_depth:
            continue
        result = container.richformat(content, formatter)
        # print(f"_{(cname, fname)}_")
        assert result == expected


@parametrize(
    ["content", "formatter", "expected"],
    {
        ("2D content, [upper, reverse]"): (
            [["Hello", "World"], ["Foo", "Bar"]],
            [str.upper, lambda x: x[::-1]],
            [["HELLO", "WORLD"], ["ooF", "raB"]],
        ),
        ("2D content, [reverse] alone"): (
            [["Hello", "World"], ["Foo", "Bar"]],
            [lambda x: x[::-1]],
            [["olleH", "dlroW"], ["Foo", "Bar"]],
        ),
    },
)
def test_2D_content_1D_formatter(content, formatter, expected):
    assert container.richformat(content, formatter) == expected
