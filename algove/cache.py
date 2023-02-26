from functools import wraps
from algove.repository import LocalFS
from typing import Callable
from logging import getLogger
from algove.logger import Status

logger = getLogger(__name__)


def _noop(*args, **kwargs):
    pass


class Cache:
    def __init__(self, fs: LocalFS, display: Callable = _noop):
        self.fs = fs
        self.display = display

    def __call__(self, name: str):
        def wrapper(f: Callable):
            @wraps(f)
            def wrapped(*args, **kwargs):
                if self.fs.exists(name):
                    logger.info(f"{Status.CACHE_HIT}: {name}")
                    result = self.fs.load(name)
                else:
                    logger.info(f"{Status.COMPUTING}: {name}")
                    result = f(*args, **kwargs)
                    self.fs.save(result, name)

                self.display(result)
                return result

            return wrapped

        return wrapper
