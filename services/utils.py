from urllib.parse import urlparse, urlunparse, urlencode

from typing import Optional, Dict, Union


def add_url_params(base_url: str, params):
    url_parts = list(urlparse(base_url))
    url_parts[4] = urlencode(params)
    return urlunparse(url_parts)


def get_next_page_url(
    base_url: str, offset: int, limit: int, count: int, order_by: Optional[str] = None
) -> Optional[str]:
    next_offset = offset + limit
    if next_offset >= count:
        return None
    params: Dict[str, Union[str, int]] = {"offset": next_offset, "limit": limit}
    if order_by:
        params.update({order_by: order_by})
    return add_url_params(base_url, params)


def get_prev_page_url(base_url: str, offset: int, limit: int, order_by: Optional[str] = None) -> Optional[str]:
    prev_offset = offset - limit
    if prev_offset < 0:
        return None
    params: Dict[str, Union[str, int]] = {"offset": prev_offset, "limit": limit}
    if order_by:
        params.update({order_by: order_by})
    return add_url_params(base_url, params)
