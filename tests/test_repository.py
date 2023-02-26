import pytest
from algove.repository import LocalFS


def test_local_get_path(local_fs: LocalFS):
    assert local_fs.get_path("thing", str).suffix == ".txt"


def test_local_save(local_fs: LocalFS):
    local_fs.save("this is a string", "test_arti")


def test_local_save_throws_if_name_exists(local_fs: LocalFS):
    local_fs.save("hi", "test")
    with pytest.raises(ValueError):
        local_fs.save("bye", "test")


def test_local_infer_type(local_fs: LocalFS):
    local_fs.save("test string", "my_artifact")
    assert local_fs.infer_type("my_artifact") == str


def test_local_infer_type_error_if_dupes(local_fs: LocalFS):
    local_fs.save("test string", "test_dupe")
    p = local_fs.get_path("test_dupe", str)
    p.with_suffix(".dummy").write_text("")
    with pytest.raises(ValueError):
        local_fs.infer_type("test")


def test_local_fs_true_after_save(local_fs: LocalFS):
    local_fs.save("test_obj", "some name")
    assert local_fs.exists("some name")


def test_local_fs_false_if_no_save(local_fs: LocalFS):
    assert not local_fs.exists("some name")


def test_local_fs_str_roundtrip(local_fs: LocalFS):
    obj = "stuff"
    local_fs.save(obj, "name")
    assert obj == local_fs.load("name")
