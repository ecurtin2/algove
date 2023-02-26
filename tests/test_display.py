from algove.display import truncated_print


def test_truncated_print_large_limit(capsys):
    n_lines = 20
    header_footer_size = 5
    truncated_print(n_lines)("test_obj", "a\n" * 10)
    stdout, _ = capsys.readouterr()
    assert len(stdout.splitlines()) == 10 + header_footer_size
    assert "test_obj" in stdout


def test_truncated_print_small_limit(capsys):
    n_lines = 5
    header_footer_size = 5
    truncated_print(n_lines)("test_obj", "a\n" * 10)
    stdout, _ = capsys.readouterr()
    assert len(stdout.splitlines()) == n_lines + header_footer_size
    assert "test_obj" in stdout
