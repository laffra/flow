"""
CopyRight (c) 2024 - Chris Laffra - All Rights Reserved.

This module creates a preview for a Flow node.
"""


import base64
import io
import json
import matplotlib

def get_image_data(figure):
    """
    Converts a Matplotlib figure to an HTML image representation.
    
    Args:
        figure (matplotlib.figure.Figure): The Matplotlib figure to convert.
    
    Returns:
        str: An HTML string representing the figure as an image.
    """
    #
    # Use the built-in agg backend.
    # This reduces rendering time for plots from ~6s to 70ms
    #
    matplotlib.use("agg")
    bytes_io = io.BytesIO()
    figure.set_edgecolor("#BBB")
    figure.savefig(bytes_io, bbox_inches="tight", format="png")
    bytes_io.seek(0)
    matplotlib.pyplot.close(figure)
    encoded = base64.b64encode(bytes_io.read())
    return f"""<img src="data:image/png;base64,{encoded.decode('utf-8')}">"""

def get_dict_table(result):
    """
    Recursively generates an HTML table representation of a dictionary.
    
    Args:
        result (dict): The dictionary to be represented as an HTML table.
    
    Returns:
        str: An HTML table representation of the input dictionary.
    """
    if not isinstance(result, dict):
        raise ValueError(f"Expected a dict, got {type(result)}")
    return "".join([
        "<table border='1' class='dict_table'>",
            "<thead>",
                "<tr><th>key</th><th>value</th></tr>",
            "</thead>",
            "<tbody>",
                "".join(f"<tr><td>{key}</td><td>{get_dict_table(value)}</td></tr>" for key, value in result.items()),
            "</thead>",
        "</table>",
    ])


def create_preview(result): # pylint: disable=too-many-return-statements
    """
    Creates a preview of the given result object.
    
    The preview can be in the form of an HTML representation, an image, or a
    string representation, depending on the type of the result object.
    
    Args:
        result: The result object to create a preview for.
    
    Returns:
        A string representation of the preview.
    """
    if isinstance(result, (str, int, float)):
        return result
    if isinstance(result, (tuple, list)):
        if len(result) > 100:
            first = json.dumps(result[:50], indent=4)
            last = json.dumps(result[-50:], indent=4)
            preview = f"{first[:-2]}\n    ...\n{last[2:]}"
        else:
            preview = json.dumps(result, indent=4)
        return f"{result.__class__.__name__} with {len(result)} items: <pre>{preview}</pre>"
    if str(result) == "DataFrame":
        return str(result)
    if "plotly" in str(type(result)):
        try:
            import plotly # pylint: disable=import-outside-toplevel
            html = plotly.io.to_html(result, default_width=500, default_height=500)
            return html
        except ImportError:
            pass
    try:
        return get_image_data(result)
    except Exception: # pylint: disable=broad-except
        pass  # print(traceback.format_exc())
    try:
        return get_image_data(result.get_figure())
    except Exception: # pylint: disable=broad-except
        pass  # print(traceback.format_exc())
    try:
        return result._repr_html_() # pylint: disable=protected-access
    except Exception: # pylint: disable=broad-except
        pass  # print(traceback.format_exc())
    try:
        html = io.StringIO()
        result.save(html, "html")
        return html.getvalue()
    except Exception: # pylint: disable=broad-except
        pass  # traceback.print_exc()
    try:
        return get_dict_table(result)
    except Exception: # pylint: disable=broad-except
        pass  # print(traceback.format_exc())
    try:
        return f"{result.getbuffer().nbytes} bytes"
    except Exception: # pylint: disable=broad-except
        pass  # print(traceback.format_exc())
    try:
        return json.dumps({result})
    except Exception: # pylint: disable=broad-except
        pass  # print(traceback.format_exc())
    try:
        return repr(result)
    except Exception: # pylint: disable=broad-except
        pass  # print(traceback.format_exc())
    return f"<pre>&lt;{type(result).__name__}&gt;<pre>"
