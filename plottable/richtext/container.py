from plottable.richtext.content import make_content
from plottable.richtext.formatters import make_formatter


def richformat(data, fmt):
    """
    Create the appropriate Content and Formatter objects,
    then apply the latter to the former.
    """
    content_obj = make_content(data)
    formatter_obj = make_formatter(fmt)
    return content_obj.format(formatter_obj)
