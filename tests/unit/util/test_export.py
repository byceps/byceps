"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.export import serialize_dicts_to_csv, serialize_tuples_to_csv


def test_serialize_dicts_to_csv():
    field_names = ['name', 'color']
    rows = [
        {'name': 'Sonic the Hedgehog', 'color': 'blue'},
        {'name': 'Pac-Man', 'color': 'yellow'},
        {'name': 'Ultraman', 'color': 'white/red'},
    ]

    actual = serialize_dicts_to_csv(field_names, rows, delimiter=';')

    assert list(actual) == [
        'name;color\r\n',
        'Sonic the Hedgehog;blue\r\n',
        'Pac-Man;yellow\r\n',
        'Ultraman;white/red\r\n',
    ]


def test_serialize_tuples_to_csv():
    rows = [
        ('name', 'color'),
        ('Sonic the Hedgehog', 'blue'),
        ('Pac-Man', 'yellow'),
        ('Ultraman', 'white/red'),
    ]

    actual = serialize_tuples_to_csv(rows)

    assert list(actual) == [
        'name,color\r\n',
        'Sonic the Hedgehog,blue\r\n',
        'Pac-Man,yellow\r\n',
        'Ultraman,white/red\r\n',
    ]
