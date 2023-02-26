from typing import Callable


def truncated_print(n_chars: int) -> Callable:
    def trunc_print(obj):
        print("\n".join(str(obj).splitlines()[:n_chars]))

    return trunc_print
