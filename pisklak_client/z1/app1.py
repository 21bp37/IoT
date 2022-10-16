import requests
from pathlib import Path


def post_file(path: str | Path) -> requests.Response:
    with open(path, 'rb') as f:
        # path = Path(path) if isinstance(path, str) else path
        r = requests.post('http://127.0.0.1:5000', files={'file': f})
        return r


def get_line(filename: str, line: int) -> str:
    return str(requests.get('http://127.0.0.1:5000', params={'file': filename, 'line': line}).content.decode())


if __name__ == '__main__':
    print(post_file('./files/test.txt').reason)
    print(get_line('./test.txt', -1))
