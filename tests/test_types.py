from algove.datatypes import to_bytes, from_bytes
import polars as pl
from polars.testing import assert_frame_equal
from datetime import datetime


def test_to_bytes_string():
    to_bytes("hello")


def test_to_bytes_dict():
    to_bytes({"a": 2})


def test_from_bytes_string_roundtrip():
    s = "hello"
    assert from_bytes(s.encode(), str) == s


def test_polars_roundtrip():
    df = pl.DataFrame(
        {
            "integer": [1, 2, 3],
            "date": [
                (datetime(2022, 1, 1)),
                (datetime(2022, 1, 2)),
                (datetime(2022, 1, 3)),
            ],
            "float": [4.0, 5.0, 6.0],
        }
    )
    b = to_bytes(df)
    assert len(b) > 1
    loaded = from_bytes(b, pl.DataFrame)
    assert_frame_equal(df, loaded)
