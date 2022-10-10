import urllib.request
import json


def binary_edit(name: str) -> bytes:
    with open(f'{name}', 'r+b') as file:
        _bytes = b'\xFF\xD8\xFF'
        file.seek(0)
        data = file.read()
    with open(f'bin_{name}', 'w+b') as new_file:
        # new_file.seek(0)
        new_file.write(_bytes)
        new_file.write(data)
        return new_file.read()


def load_json(name: str) -> dict:
    with open(f'{name}', 'r+') as file:
        data = json.load(file)
        _id = str(input("Wpisz id do zmodyfikowania: "))
        _val = str(input("Wpisz nowa wartosc: "))
        try:
            data[_id] = _val
            file.seek(0)
            json.dump(data, file, indent=4)
        except KeyError:
            print('nie znaleziono klucza')
        print(data)
        return data


def get_json(url: str) -> list:
    content = urllib.request.urlopen(url).read()
    data = json.loads(content)
    data = sorted(data, key=lambda x: x['name'], reverse=False)
    print(data)
    return data


if __name__ == '__main__':
    # filename = str(input("Nazwa Pliku: "))
    binary_edit('file.json')
    load_json("test.json")
    get_json("https://raw.githubusercontent.com/Wysciguvvka/IoT/main/lista0/file.json")
