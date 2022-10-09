import urllib.request
import json


def binka(name: str) -> None:
    with open(f'{name}', 'r+b') as file:
        pass


def load_json(name: str) -> None:
    with open(f'{name}', 'r+') as file:
        data = json.load(file)
        _id = str(input("Wpisz id do zmodyfikowania: "))
        _val = str(input("Wpisz id nowa wartosc: "))
        try:
            data[_id] = _val
            file.seek(0)
            json.dump(data, file, indent=4)
        except KeyError:
            print('nie znaleziono klucza')
        print(data)


def get_json(url: str) -> None:
    content = urllib.request.urlopen(url).read()
    data = json.loads(content, sort_keys=True)
    data = sorted(data, key=lambda x: x['name'], reverse=True)
    print(data)

if __name__ == '__main__':
    # filename = str(input("Nazwa Pliku: "))
    # binka(filename)
    load_json("test.json")
