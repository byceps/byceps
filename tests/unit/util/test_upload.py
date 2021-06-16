"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from io import BytesIO

from pytest import raises

from byceps.util.upload import delete, store


SOURCE_BYTES = BytesIO(b'\x04\x08\x15\x16\x23\x42')


def test_store(tmp_path):
    target_path = tmp_path / 'famous-words.txt'
    assert not target_path.exists()

    store(SOURCE_BYTES, target_path)

    assert target_path.exists()


def test_store_with_existent_target_path(tmp_path):
    target_path = tmp_path / 'famous-words.txt'
    target_path.touch(exist_ok=False)
    assert target_path.exists()

    with raises(FileExistsError):
        store(SOURCE_BYTES, target_path)


def test_store_with_nonexistent_parent_path1(tmp_path):
    target_path = tmp_path / 'nonexistent' / 'famous-words.txt'

    with raises(FileNotFoundError):
        store(SOURCE_BYTES, target_path)


def test_store_with_nonexistent_parent_path2(tmp_path):
    target_path = tmp_path / 'nonexistent' / 'famous-words.txt'

    store(SOURCE_BYTES, target_path, create_parent_path_if_nonexistent=True)


# -------------------------------------------------------------------- #


def test_delete_with_existent_path(tmp_path):
    path = tmp_path / 'to-be-removed.png'
    path.touch(exist_ok=False)
    assert path.exists()

    delete(path)

    assert not path.exists()


def test_delete_with_nonexistent_path(tmp_path):
    path = tmp_path / 'fake.png'
    assert not path.exists()

    delete(path)
