import urllib.request


def download(url: str) -> str:  # pragma: no cover
    with urllib.request.urlopen(url) as f:
        return f.read().decode("utf-8")
