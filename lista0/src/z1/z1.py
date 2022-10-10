import urllib.request
import json


def edit_binary(name: str) -> bytes:
    """
    funkcja odpowiedzialna za wczytanie oraz edycję pliku binarnego.
    na początek pliku binarnego dopisane zostają: b'\xFF\xD8\xFF'.

    :param name: string = nazwa pliku json.
    :return: bytes = zawartość pliku binarnego po edycji.
    """
    with open(f'{name}', 'r+b') as file:
        _bytes = b'\xFF\xD8\xFF'
        file.seek(0)
        data = file.read()
    with open(f'bin_{name}', 'w+b') as new_file:
        new_file.write(_bytes)
        new_file.write(data)
        new_file.seek(0)
        return new_file.read()


def edit_json(name: str, key: str, val: any) -> dict | list:
    """
    Funkcja odpowiedzialna za wczytanie oraz edycję pliku json.

    :param name: string = nazwa pliku json.
    :param key: string = klucz w pliku json który będzie zmieniany.
    :param val: string = nowa wartość podanego wcześniej klucza.
    :return: dict | list = zawartość pliku json po edycji.
    """
    with open(f'{name}', 'r+') as file:
        try:
            data = json.load(file)
        except ValueError:
            raise ValueError("Nie udało się odczytać pliku json")
        try:
            data[key] = val
            file.seek(0)
            json.dump(data, file, indent=4)
        except KeyError:
            raise KeyError("Nie znaleziono klucza w pliku json")
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
    data = sorted(data, key=lambda x: x[key], reverse=False)
    return data


if __name__ == '__main__':
    print(edit_binary('file.json'))
    print(edit_json('test.json', 'name', 'test_name'))
    print(get_json("https://pastebin.com/raw/xCiX51aK"))
