from typing import Callable, List


class Pipeline:
    def __init__(self, name: str):
        self.name = name
        self.funcs: List[Callable] = []

    def __or__(self, other: Callable):
        self.funcs.append(other)
        return self

    def __call__(self, *args, **kwargs):
        first, *rest = self.funcs
        curr = first(*args, **kwargs)
        for f in rest:
            curr = f(curr)
        return curr
