import pytest

from algove import LocalFS
import logging

logging.getLogger().setLevel("DEBUG")


@pytest.fixture()
def local_fs(tmp_path) -> LocalFS:
    return LocalFS(root=tmp_path)
