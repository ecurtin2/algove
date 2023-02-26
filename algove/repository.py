from typing import Optional, List, Tuple, Type
from pathlib import Path
from os import PathLike

from algove.datatypes import (
    to_bytes,
    SupportedObj,
    SupportedBound,
    type_to_extension,
    from_bytes,
)
from algove.logger import Status

import logging

logger = logging.getLogger(__name__)


class LocalFS:
    root: Path

    def __init__(self, root: Optional[PathLike] = None):
        self.root = Path.cwd() / "algove_data" if root is None else Path(root)

    def get_path(self, name: str, type: Type[SupportedObj]) -> Path:
        return (self.root / name).with_suffix(type_to_extension[type])

    def exists(self, name: str) -> bool:
        """Check if the named artifact exists



        Raises
        --------

        ValueError - if there is ambiguity (i.e. multiple files same stem)
        """
        listed = self.list_saved(name)  # type: ignore[var-annotated]
        if len(listed) == 0:
            return False
        elif len(listed) == 1:
            return True
        else:
            raise ValueError(f"Artifactname is ambiguous: {name} found: {listed}")

    def list_saved(self, name: str) -> List[Tuple[Type[SupportedObj], Path]]:
        possibilities = [
            (t, (self.root / name).with_suffix(ext))
            for t, ext in type_to_extension.items()
        ]
        return [(t, p) for t, p in possibilities if p.exists()]

    def infer_type(self, name: str) -> Type[SupportedObj]:
        matches = self.list_saved(name)  # type: ignore[var-annotated]
        if len(matches) == 1:
            return matches[0][0]
        elif len(matches) > 1:
            raise ValueError(
                f"Cannot infer name, there are multiple files with it {name}: {matches}"
            )
        else:
            raise ValueError(f"Could not find {name}")

    def save(self, obj: SupportedObj, name: str) -> SupportedObj:
        matches = self.list_saved(name)  # type: ignore[var-annotated]
        if matches:
            raise ValueError(f"Cannot save {name}, already exists at {matches}")

        dest = self.get_path(name, type(obj))
        dest.parent.mkdir(exist_ok=True, parents=True)
        logger.info(f"{Status.SAVING} {name} -> {dest}")
        dest.write_bytes(to_bytes(obj))
        return obj

    def load(self, name: str) -> SupportedBound:
        t = self.infer_type(name)  # type: ignore[var-annotated]
        p = self.get_path(name, type=t)
        logger.info(f"{Status.LOADING}: {name} <-- {p}")
        b = p.read_bytes()
        return from_bytes(b, t)
