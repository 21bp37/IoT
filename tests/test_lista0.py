import pytest
import json
import urllib.request
from pisklak.lista0 import edit_binary, edit_json, get_json


def test_edit_binary(tmp_path):
    binary_path = tmp_path / 'test_binary.bin'
    with open(binary_path, 'w+b') as test_binary:
        test_binary.write(b'\x00\x00\x00')
    assert edit_binary(binary_path) == b'\xFF\xD8\xFF\x00\x00\x00'


def test_edit_json(tmp_path):
    test_json = """
        {
            "name": "asd",
            "type": 1,
            "car": null
        }
        """
    expected = """
        {
            "name": "asd",
            "type": 1,
            "car": "test_car"
        }
        """
    json_path = tmp_path / 'test_case.json'
    with open(json_path, 'w+') as test_edit:
        test_edit.write(test_json)
    assert edit_json(json_path, 'car', 'test_car') == json.loads(expected)


def test_get_json():
    test_case = json.loads("""[{"name": "E"},
        {"name": "A"},
        {"name": "B"},
        {"name": "Z"},
        {"name": "Q"},
        {"name": "C"}
        {"name": "F"}
        ]""")
    sorted_json = json.loads(
        """[
        {"name": "A"},
        {"name": "B"},
        {"name": "C"},
        {"name": "E"},
        {"name": "F"},
        {"name": "Q"},
        {"name": "Z"}
        ]""")
    url = 'https://pastebin.com/raw/xCiX51aK'
    content = json.loads(urllib.request.urlopen(url).read())
    assert content == test_case
    assert get_json(url) == sorted_json


def test_edit_invalid_json(tmp_path):
    json_path = tmp_path / 'not.json'
    with open(json_path, 'w+b') as not_json:
        not_json.write(b'\x00\x00\x00')
    with pytest.raises(ValueError):
        edit_json(json_path, 'name', 'test')


def test_get_invalid_data():
    with pytest.raises(ValueError):
        get_json('https://www.google.com')


def test_get_key_not_found():
    url = 'https://pastebin.com/raw/xCiX51aK'
    with pytest.raises(KeyError):
        get_json(url, 'key')
