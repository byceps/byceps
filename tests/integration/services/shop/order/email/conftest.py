"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.shop.shop.models import Shop
from byceps.services.snippet.models import SnippetID
from byceps.services.user.models.user import User

from tests.helpers.shop import create_shop_snippet


pytest.register_assert_rewrite(f'{__package__}.helpers')


@pytest.fixture(scope='package')
def order_admin(make_user):
    return make_user()


@pytest.fixture
def email_payment_instructions_snippet_id(
    shop: Shop, order_admin: User
) -> SnippetID:
    return create_shop_snippet(
        shop.id,
        order_admin.id,
        'email_payment_instructions',
        'de',
        '''
Bitte überweise den Gesamtbetrag auf folgendes Konto:

  Zahlungsempfänger: <Name>
  IBAN: <IBAN>
  BIC: <BIC>
  Bank: <Kreditinstitut>
  Verwendungszweck: {{ order_number }}

Wir werden dich informieren, sobald wir deine Zahlung erhalten haben.

Hier kannst du deine Bestellungen einsehen: https://www.acmecon.test/shop/orders
''',
    )
