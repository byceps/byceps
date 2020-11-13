"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.util.l10n import set_locale


def test_set_locale_with_valid_locale():
    set_locale('en_US.utf8')


def test_set_locale_with_invalid_locale():
    with pytest.warns(UserWarning) as record:
        set_locale('invalid')

    assert len(record) == 1
    assert record[0].message.args[0] == 'Could not set locale to "invalid".'
