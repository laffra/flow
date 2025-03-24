"""
Copyright (c) 2024 laffra - All Rights Reserved. 
"""


def url_bytes(url: str) -> bytes:
    """
    Load the contents of a file from a URL.
    """
    import io # pylint: disable=import-outside-toplevel
    import urllib.request # pylint: disable=import-outside-toplevel
    return io.BytesIO(urllib.request.urlopen(url).read())
