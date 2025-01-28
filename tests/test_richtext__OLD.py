import pytest

from plottable.richtext.formatters import _init_formatters
from plottable.richtext.richtext__OLD import (
    RichTextContainer,
    _init_content,
)
from plottable.richtext.utils import depth

from .conftest import parametrize


@pytest.fixture
def list_content():
    return ["a test", "from a list"]


@pytest.fixture
def multiline_content():
    return "a test\non 2 lines"


@pytest.fixture
def style():
    return {"fontsize": 8, "weight": "normal", "style": "italic"}


@pytest.fixture
def at_wrap_formatter():
    return "@@{}@@".format


def test_init_with_string():
    rt = RichTextContainer("test string")


@pytest.mark.parametrize(
    ["style", "format", "text", "expected"],
    [
        (
            {"fontsize": 16, "weight": "bold"},
            "{}",
            "a text",
            "a text",
        ),
        (
            {"fontsize": 8},
            "{}".format,
            "a text",
            "a text",
        ),
        (
            {"fontsize": 8, "weight": "normal", "style": "italic"},
            lambda x: f"--{x}--",
            "text",
            "--text--",
        ),
    ],
    ids=["string formatter", "format method", "lambda"],
)
def test_format_scalar_content(style, format, text, expected):
    rt = RichTextContainer(text, styles=style, formatters=format)

    assert rt.format() == expected


def test_ml_content_should_turn_to_list(multiline_content):
    expected = multiline_content.splitlines()
    rt = RichTextContainer(multiline_content)
    rt2 = RichTextContainer(multiline_content.splitlines())

    assert rt.content == expected
    assert rt.content == rt2.content


@pytest.mark.skip
def test_mline_formatting(multiline_content, style, at_wrap_formatter):
    rt = RichTextContainer(
        multiline_content, styles=style, formatters=at_wrap_formatter
    )

    assert rt.format() == [
        ("@@a test@@", style),
        ("@@on 2 lines@@", style),
    ]


def test_format_should_return_the_right_thing():
    rt = RichTextContainer(
        content=["Entry T.O.", "(2023)"],
        styles=[
            {
                "fontsize": 16,
                "weight": "bold",
            },
            {
                "fontsize": 8,
                "weight": "normal",
            },
        ],
    )


@parametrize(
    ["value", "expected"],
    {
        "empty str": ("", ""),
        "empty list": ([], []),
        "text": ("text", "text"),
        "list": (["text", "text"], ["text", "text"]),
        "multi_list": (
            [
                ["text", "text"],
                ["text", "text"],
            ],
            [
                ["text", "text"],
                ["text", "text"],
            ],
        ),
        "multi_line": ("text\ntext", ["text", "text"]),
        "multi_line_in_list": (
            [
                ["text", "text"],
                "text\ntext",
            ],
            [
                ["text", "text"],
                ["text", "text"],
            ],
        ),
        # "nested_mline": ([["text\ntext"]], [["text", "text"]]),
    },
)
def test_init_content(value, expected):
    assert _init_content(value) == expected


# Formatters


# 1 fmter will broadcast on all content unit
@parametrize(
    ["value", "expected"],
    {
        "empty str": ("", "@@@@"),
        "text": ("text", "@@text@@"),
        "empty list": ([], []),
        "list": (["text", "text"], ["@@text@@", "@@text@@"]),
        "multi_list": (
            [
                ["text", "text"],
                ["text", "text"],
            ],
            [
                ["text", "text"],
                ["@@text@@", "@@text@@"],
            ],
        ),
        # "nested_mline": ([["text\ntext"]], [["text", "text"]]),
    },
)
@pytest.mark.skip
def test_format_all_content_types(value, expected, at_wrap_formatter):
    rt = RichTextContainer(value, formatters=at_wrap_formatter)
    assert rt.format(with_styles=True) == (expected, None)


@pytest.mark.skip
def test_from_ppa():
    content = [
        "Only:",
        "Cross-Seller:",
        "Average:",
    ]
    expected = [
        "Shoes Only:",
        "Cross-Seller:",
        "Average:",
    ]
    formatters = [lambda val: f"Shoes {val}", None, None]

    rt = RichTextContainer(content, formatters=formatters)

    rt.format()


def test_1D_Sequence_with_0D_formatter_must_propagate():
    content = [
        "Only:",
        "Cross-Seller:",
        "Average:",
    ]
    expected = [
        "Shoes Only:",
        "Shoes Cross-Seller:",
        "Shoes Average:",
    ]
    formatters = "Shoes {}".format

    rt = RichTextContainer(content, formatters=formatters)

    assert rt.format() == expected


def test_1D_Sequence_with_1D_formatter_matching_length():
    content = [
        "Only:",
        "Cross-Seller:",
        "Average:",
    ]
    expected = [
        "Shoes Only:",
        "1111 Cross-Seller: 1111",
        "222 Average: 222",
    ]
    formatters = ["Shoes {}".format, "1111 {} 1111".format, "222 {} 222".format]

    rt = RichTextContainer(content, formatters=formatters)

    rt.format()


def test_1D_Sequence_with_1D_formatter_shorter():
    content = [
        "Only:",
        "Cross-Seller:",
        "Average:",
    ]
    expected = [
        "Shoes Only:",
        "Cross-Seller:",
        "Average:",
    ]
    formatters = [lambda val: f"Shoes {val}", None, None]

    rt = RichTextContainer(content, formatters=formatters)

    rt.format()


@parametrize(
    ["formatter", "expected"],
    {
        # 0D formatters
        "None": (None, str),
        "empty str": ("", str),
        "empty list": ([], str),
        "False": (False, str),
        "str callable": (str.upper, str.upper),
    },
)
def test__init_formatters_with_0D(formatter, expected):
    assert _init_formatters(formatter) == expected


param_dict_1D = {
    # 1D formatters
    "None": ([None, None], [str, str]),
    "empty str": (["", ""], [str, str]),
    "empty list": ([[], []], [str, str]),
    "False": ([False, False], [str, str]),
    "str callable": ([str.upper, str.lower], [str.upper, str.lower]),
    "str to format ": (["{}", "@{}@"], ["{}".format, "@{}@".format]),
}


@parametrize(
    ["formatter", "expected"],
    param_dict_1D,
)
def test__init_formatters_with_1D(formatter, expected):
    assert _init_formatters(formatter) == expected


param_dict_2D = {
    key: tuple([[value[0], value[0]], [value[1], value[1]]])
    for key, value in param_dict_1D.items()
}


@parametrize(
    ["formatter", "expected"],
    param_dict_2D,
)
def test__init_formatters_with_2D(formatter, expected):
    print(_init_formatters(formatter))
    assert _init_formatters(formatter) == expected


@parametrize(
    ["value", "expected"],
    {
        "0D": ("test", 0),
        "1D": ([1, 2, 3], 1),
        "2D": ([[1, 2], [3]], 2),
        "3D": ([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], 3),
    },
)
def test_depth_iterables(value, expected):
    assert depth(value) == expected
