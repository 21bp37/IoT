from z1.z1 import *


def test_edit_binary():
    with open('test_binary.bin', 'w+b') as test_file:
        test_file.write(b'\x00\x00\x00')
    assert edit_binary('test_binary.bin') == b'\xFF\xD8\xFF\x00\x00\x00'


def test_edit_json():
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
    with open('test_case.json', 'w+') as test_file:
        test_file.write(test_json)
    assert edit_json('test_case.json', 'car', 'test_car') == json.loads(expected)


def test_get_json():
    test_case = json.loads("""[{"name": "E"},
        {"name": "A"},
        {"name": "B"},
        {"name": "Z"},
        {"name": "Q"},
        {"name": "C"},
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
