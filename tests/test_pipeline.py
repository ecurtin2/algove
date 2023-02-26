from algove.pipeline import Pipeline


def test_pipeline():
    def addone(x):
        return x + 1

    def multwo(x):
        return x * 2

    pipe = Pipeline("test_pipe") | addone | multwo
    assert pipe(0) == 2
