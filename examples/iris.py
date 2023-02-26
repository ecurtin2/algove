from algove import LocalFS, download, Cache, init_logger, truncated_print, Pipeline
from algove.transformers import FitLabelEncoder, NumpyForcer
import polars as pl
from io import StringIO

from sklearn.linear_model import LogisticRegression


init_logger()
fs = LocalFS()
cache = Cache(fs, display=truncated_print(20))


@cache("iris_data")
def get_data():
    return download(
        "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
    )


@cache("iris_description")
def get_labels():
    return download(
        "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.names"
    )


@cache("parsed_data")
def parse_data(data: str) -> pl.DataFrame:
    # TODO: it shouldn't be necessary here to read string into memory
    f = StringIO(data)
    df = pl.read_csv(f, has_header=False)
    df.columns = [
        "sepal_len_cm",
        "sepal_width_cm",
        "petal_length_cm",
        "petal_width_cm",
        "class",
    ]
    return df


@cache("train_set")
def make_train(df: pl.DataFrame) -> pl.DataFrame:
    encoder = FitLabelEncoder(column="class", output_col="class_encoded").fit(df)
    return encoder.transform(df)


@cache("predictions")
def make_predictions(df: pl.DataFrame) -> pl.DataFrame:
    forcer = NumpyForcer(
        ["sepal_len_cm", "sepal_width_cm", "petal_length_cm", "petal_width_cm"],
        y_col="class_encoded",
    )
    data = forcer.transform(df)
    model = LogisticRegression()
    model.fit(data.X, data.y)
    preds = model.predict(data.X)
    pred_series = pl.Series("predictions", preds)
    return df.with_columns(pred_series)

pipeline = Pipeline("iris-demo") | get_labels | get_data | parse_data | make_train | make_predictions
pipeline()