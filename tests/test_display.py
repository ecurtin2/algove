from algove.display import truncated_print


def test_truncated_print_large_limit(capsys):
    n_lines = 20
    truncated_print(n_lines)("a\n" * 10)
    stdout, _ = capsys.readouterr()
    assert len(stdout.splitlines()) == 10


def test_truncated_print_small_limit(capsys):
    n_lines = 5
    truncated_print(n_lines)("a\n" * 10)
    stdout, _ = capsys.readouterr()
    assert len(stdout.splitlines()) == n_lines
