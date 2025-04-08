from collections.abc import Callable
from numbers import Number
from typing import Any

import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap


def pick_colour(val: float):
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


def apply_colour(val, colour_fn: Callable[[float], str], strfmt: str = "+.0%"):
    if isinstance(val, Number):
        return f"{val:{strfmt}}\n"

    return val


def kdollar(x):
    if isinstance(x, Number):
        return f"${x/1000:,.1f}k"
    return x


def percentage_points(x):
    if isinstance(x, Number):
        return f"{x:+.0f}pp"
    return x

def percentage_points_pp(x):
    if isinstance(x, Number):
        return f"{x:+.0f}ₚₚ"
    return x

def pct(x):
    if isinstance(x, Number):
        return f"{x:+.0%}"
    return x


def group_label_format(title, subtitle):
    return f"{title}\n{subtitle}"


def text_cmap_3cols(value):
    # Define the custom colormap

    colors = ["darkred", "dimgray", "darkgreen"]
    lcmap = ListedColormap(colors)

    # Define the boundaries for the colormap
    boundaries = [-np.inf, -0.05, 0.05, np.inf]
    norm = BoundaryNorm(boundaries, lcmap.N)

    return lcmap(norm(value))


def decimal_to_percent(val: float) -> str:
    """Formats Numbers to a string, replacing
        0 with "–"
        1 with "✓"
        values < 0.01 with "<1%" and
        values > 0.99 with ">99%"

    Args:
        val (float): numeric value to format

    Returns:
        str: formatted numeric value as string
    """
    if val == 0:
        return "–"
    elif val == 1:
        return "100%"
    elif val < 0.01:
        return "<1%"
    elif val > 0.99:
        return ">99%"
    else:
        return f"{val:.0%}"
