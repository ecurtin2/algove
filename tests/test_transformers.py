import polars as pl
from algove.transformers import (
    OneHotEncoder,
    FitOneHotEncoder,
    LabelEncoder,
    FitLabelEncoder,
    NumpyForcer,
)
from polars.testing import assert_frame_equal
import numpy as np


def test_one_hot_encoder_transform():
    df = pl.DataFrame(
        {
            "text": ["a", "a", "b", "b", "b"],
        }
    )

    enc = OneHotEncoder({"text": ["a", "b"]})
    expect = pl.DataFrame(
        {"text_a": [1, 1, 0, 0, 0], "text_b": [0, 0, 1, 1, 1]}
    ).with_columns(pl.all().cast(pl.UInt8, strict=True))
    got = enc.transform(df)
    print(got)
    assert_frame_equal(got, expect)


def test_one_hot_encoder_fit():
    df = pl.DataFrame(
        {
            "text": ["a", "a", "b", "b", "b"],
        }
    )

    fitter = FitOneHotEncoder(["text"])
    encoder = fitter.fit(df)
    assert sorted(encoder.classes["text"]) == ["a", "b"]


def test_label_encoder_fit():
    df = pl.DataFrame(
        {
            "text": ["a", "a", "b", "b", "b"],
        }
    )
    fitter = FitLabelEncoder("text", "text_enc")
    encoder = fitter.fit(df)
    assert encoder.output_col == fitter.output_col
    assert sorted(encoder.vals) == ["a", "b"]


def test_label_encoder_transform():
    df = pl.DataFrame(
        {
            "text": ["a", "a", "b", "b", "b"],
        }
    )
    encoder = LabelEncoder("text", vals=["a", "b"], output_col="text_enc")
    got = encoder.transform(df)
    expect = pl.DataFrame(
        {
            "text": ["a", "a", "b", "b", "b"],
            "text_enc": [0, 0, 1, 1, 1],
        }
    )
    assert_frame_equal(got, expect)


def test_to_numpy():
    df = pl.DataFrame({"x1": [0.1, 0.2], "y": [0, 1]})
    transformer = NumpyForcer(x_cols=["x1"], y_col="y")
    got = transformer.transform(df)

    expect_x = np.array([[0.1], [0.2]])
    expect_y = np.array([0.0, 1.0])
    assert np.allclose(got.X, expect_x)
    assert np.allclose(got.y, expect_y)
