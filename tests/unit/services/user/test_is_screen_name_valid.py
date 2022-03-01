"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.user import screen_name_validator


@pytest.mark.parametrize(
    'screen_name, expected',
    [
        (''                         , False),  # denied: empty string
        ('      '                   , False),  # denied: only whitespace

        ('12'                       , False),  # denied: too short
        ('123'                      , True ),  # okay: long enough
        ('123456789012345678901234' , True ),  # okay: short enough
        ('1234567890123456789012345', False),  # denied: too long

        ('!$*-./<=>[]_'             , True ),  # okay: selected ASCII chars
        ('<anglebrackets>'          , True ),
        ('space character'          , False),
        ('double"quote'             , False),
        ('number#sign'              , False),
        ('percent%sign'             , False),
        ('ampersand&'               , False),
        ("single'quote"             , False),
        ('opening(parenthesis'      , False),
        ('closing(parenthesis'      , False),
        ('plus+sign'                , False),
        ('comma,'                   , False),
        ('colon:'                   , False),
        ('semicolon;'               , False),
        ('question?mark'            , False),
        ('at@sign'                  , False),
        (r'back\slash'              , False),
        ('caret^'                   , False),
        ('back`tick'                , False),
        ('opening{curlybrace'       , False),
        ('vertical|bar'             , False),
        ('closing{curlybrace'       , False),
        ('tilde~'                   , False),

        ('byceps'                   , True ),
        ('Gemüsebrätwörßt'          , True ),  # okay: German umlauts and szett
        ('Быцепс'                   , False),  # denied: Cyrillic/non-latin letters
    ],
)
def test_is_screen_name_valid(screen_name, expected):
    assert screen_name_validator.is_screen_name_valid(screen_name) == expected
