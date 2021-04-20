from django_readers_debug import get_repr
from tests.data import example


def get_file_contents(filename):
    with open(f"tests/data/{filename}") as file:
        return file.read()


def test_complex_example():
    expected = get_file_contents("example.txt")
    repr = get_repr(example.prepare)

    assert repr == expected
