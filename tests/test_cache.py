from algove.cache import Cache

import pytest


@pytest.fixture()
def cache(local_fs):
    return Cache(local_fs)


def test_cache(cache: Cache):
    n_call = 0

    def func():
        nonlocal n_call
        n_call += 1
        return "bye"

    cached = cache("my_func")(func)
    assert cached() == func()
    cached()
    # 3 calls overall, Two from cached, one from func()
    assert n_call == 2


def test_cache_display(cache: Cache, capsys):
    def func():
        return "bye"

    cache.display = print
    cached = cache("my_func")(func)
    assert cached() == func()

    stdout, _ = capsys.readouterr()
    assert "bye" in stdout
