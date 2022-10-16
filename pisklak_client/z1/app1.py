import requests
from pathlib import Path


def post_file(path: str | Path, url: str = 'http://127.0.0.1:5000') -> requests.Response:
    with open(path, 'r+') as f:
        # path = Path(path) if isinstance(path, str) else path
        r = requests.post(url, files={'file': f})
        return r


def get_line(filename: str, line: int, url: str = 'http://127.0.0.1:5000') -> str:
    return str(requests.get(url, params={'file': filename, 'line': line}).content.decode())


if __name__ == '__main__':
    print(post_file('./files/test.txt').reason)
    print(get_line('./test.txt', 4))
