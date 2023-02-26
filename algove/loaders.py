import urllib.request


def download(url: str) -> str:
    with urllib.request.urlopen(url) as f:
        return f.read().decode("utf-8")
