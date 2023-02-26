from functools import singledispatch
from typing import Dict, Union, TypeVar, Type, Callable
import json
from io import BytesIO
import polars as pl

SupportedBound = Union[int, str, pl.DataFrame, dict]
SupportedObj = TypeVar("SupportedObj", bound=SupportedBound)

type_to_extension: Dict[type, str] = {
    str: ".txt",
    dict: ".json",
    pl.DataFrame: ".parquet",
}


@singledispatch
def to_bytes(obj: SupportedBound) -> bytes:
    raise NotImplementedError(f"Not implemented for type {type(obj)}")


@to_bytes.register
def str_to_bytes(s: str) -> bytes:
    return s.encode()


@to_bytes.register
def dict_to_bytes(d: dict) -> bytes:
    return json.dumps(d, indent=2).encode()


@to_bytes.register
def polars_to_bytes(df: pl.DataFrame) -> bytes:
    fp = BytesIO()
    df.write_parquet(fp)
    fp.seek(0)
    return fp.read()


def str_from_bytes(b: bytes) -> str:
    return b.decode("utf-8")


def polars_from_bytes(b: bytes) -> pl.DataFrame:
    fp = BytesIO(b)
    return pl.read_parquet(fp)


decoders: Dict[Type[SupportedBound], Callable[[bytes], SupportedBound]] = {
    str: str_from_bytes,
    pl.DataFrame: polars_from_bytes,
}


def from_bytes(b: bytes, t: Type[SupportedBound]) -> SupportedBound:
    if t not in decoders:
        raise KeyError(f"Unsupported type to decode: {t}")

    return decoders[t](b)
