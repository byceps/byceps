"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from decimal import Decimal

from flask_babel import refresh
import pytest

from byceps.services.authentication.session import service as session_service
from byceps.util.money import format_euro_amount

from tests.helpers import current_user_set


CURRENT_USERS = {
    locale: session_service.get_anonymous_current_user(locale)
    for locale in {'en', 'de'}
}


@pytest.mark.parametrize(
    'locale, value, expected',
    [
        ('en', Decimal(      '0.00' ),         '€0.00'    ),
        ('en', Decimal(      '0.01' ),         '€0.01'    ),
        ('en', Decimal(      '0.5'  ),         '€0.50'    ),
        ('en', Decimal(      '1.23' ),         '€1.23'    ),
        ('en', Decimal(    '123.45' ),       '€123.45'    ),
        ('en', Decimal(    '123.456'),       '€123.46'    ),
        ('en', Decimal('1234567'    ), '€1,234,567.00'    ),
        ('en', Decimal('1234567.89' ), '€1,234,567.89'    ),
        ('de', Decimal(      '0.00' ),         '0,00\xa0€'),
        ('de', Decimal(      '0.01' ),         '0,01\xa0€'),
        ('de', Decimal(      '0.5'  ),         '0,50\xa0€'),
        ('de', Decimal(      '1.23' ),         '1,23\xa0€'),
        ('de', Decimal(    '123.45' ),       '123,45\xa0€'),
        ('de', Decimal(    '123.456'),       '123,46\xa0€'),
        ('de', Decimal('1234567'    ), '1.234.567,00\xa0€'),
        ('de', Decimal('1234567.89' ), '1.234.567,89\xa0€'),
    ],
)
def test_format_euro_amount(admin_app, locale, value, expected):
    app = admin_app
    current_user = CURRENT_USERS[locale]

    with current_user_set(app, current_user), app.app_context():
        refresh()
        assert format_euro_amount(value) == expected
