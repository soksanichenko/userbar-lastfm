from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import make_response


def nocache(view: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that adds no-cache headers to any Flask view response."""
    @wraps(view)
    def no_cache(*args: Any, **kwargs: Any) -> Any:
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    return no_cache
