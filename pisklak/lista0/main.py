from pathlib import Path

import urllib.request
import json

import typing


def edit_binary(name: str | Path) -> bytes:
    """
    funkcja odpowiedzialna za wczytanie oraz edycję pliku binarnego.
    na początek pliku binarnego dopisane zostają: b'\xFF\xD8\xFF'.

    :param name: string | Path = nazwa pliku json.
    :return: bytes = zawartość pliku binarnego po edycji.
    """
    _path = Path(name) if isinstance(name, str) else name
    with open(_path, 'r+b') as file:
        _bytes = b'\xFF\xD8\xFF'
        file.seek(0)
        data = file.read()
    new_path = Path(_path.parent) / f'bin_{_path.name}'
    with open(new_path, 'w+b') as new_file:
        new_file.write(_bytes)
        new_file.write(data)
        new_file.seek(0)
        return new_file.read()


def edit_json(name: str | Path, key: str, val: typing.Any) -> dict | list:
    """
    Funkcja odpowiedzialna za wczytanie oraz edycję pliku json.

    :param name: string | Path = nazwa pliku json.
    :param key: string = klucz w pliku json który będzie zmieniany.
    :param val: string = nowa wartość podanego wcześniej klucza.
    :return: dict | list = zawartość pliku json po edycji.
    """
    with open(f'{name}', 'r+') as file:
        try:
            data = json.load(file)
        except ValueError:
            raise ValueError("Nie udało się odczytać pliku json")
        data[key] = val
        file.seek(0)
        json.dump(data, file, indent=4)
        return data


def get_json(url: str, key: str = 'name') -> list:
    """
    Funkcja odpowiedzialna za wczytanie  oraz posortowanie pliku json z adresu URL (HTTP GET).
    :param url: string = adres url z któego zostanie pobrany plik json.
    :param key: string = klucz według którego będzie sortowany plik.
    :return: list = posortowana lista z pliku json.
    """
    content = urllib.request.urlopen(url).read()
    try:
        data = json.loads(content)
    except ValueError:
        raise ValueError("Nie udało się odczytać pliku json")
    try:
        data = sorted(data, key=lambda x: x[key], reverse=False)
    except KeyError:
        raise KeyError("Nie znaleziono klucza")
    return data


if __name__ == '__main__':  # pragma: no cover
    with open('file.bin', 'w+b') as test_file:
        test_file.write(b'\x00\x00\x00')
    print(edit_binary('file.bin'))
    print(edit_json('test.json', 'name', 'test_name'))
    print(get_json("https://pastebin.com/raw/xCiX51aK"))
