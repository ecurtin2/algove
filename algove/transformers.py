from typing import List, Dict
from collections import namedtuple
import polars as pl


class OneHotEncoder:
    def __init__(self, classes: Dict[str, List[str]]):
        self.classes = classes

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        col_exprs = []
        out_names: List[str] = []
        for col, classes in self.classes.items():
            mapping = {c: i for i, c in enumerate(classes)}
            col_exprs.append(pl.col(col).map_dict(mapping))
            out_names.extend(f"{col}_{c}" for c in classes)

        result = pl.get_dummies(df.select(col_exprs))
        result.columns = out_names
        return result


class FitOneHotEncoder:
    def __init__(self, columns: List[str]):
        self.columns = columns

    def fit(self, df: pl.DataFrame) -> OneHotEncoder:
        classes = {
            c: list(df.select(pl.col("text").unique()).to_numpy()) for c in self.columns
        }
        return OneHotEncoder(classes=classes)


class LabelEncoder:
    def __init__(self, column: str, vals: List, output_col: str):
        self.col = column
        self.vals = vals
        self.output_col = output_col

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        mapping = {c: i for i, c in enumerate(self.vals)}
        return df.with_columns(
            pl.col(self.col).map_dict(mapping).alias(self.output_col)
        )


class FitLabelEncoder:
    def __init__(self, column: str, output_col: str):
        self.column = column
        self.output_col = output_col

    def fit(self, df: pl.DataFrame) -> LabelEncoder:
        vals = list(df.select(pl.col(self.column).unique()).to_numpy().flatten())
        return LabelEncoder(self.column, vals, output_col=self.output_col)


data = namedtuple("data", ["X", "y"])


class NumpyForcer:
    def __init__(self, x_cols: List[str], y_col: str):
        self.x_cols = x_cols
        self.y_col = y_col

    def transform(self, df: pl.DataFrame) -> data:
        y = df.select(pl.col(self.y_col).cast(pl.Float64)).to_numpy().ravel()
        x = df.select([pl.col(c).cast(pl.Float64) for c in self.x_cols]).to_numpy()
        return data(x, y)
