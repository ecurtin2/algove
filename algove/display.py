from typing import Callable


def truncated_print(n_chars: int) -> Callable:
    def trunc_print(name: str, obj):
        header = f"###### {name} ######\n"
        print(header)
        print("\n".join(str(obj).splitlines()[:n_chars]))
        print(f"\n#### end {name} ####\n")

    return trunc_print
