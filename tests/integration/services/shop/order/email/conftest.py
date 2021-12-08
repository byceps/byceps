"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.shop.order import (
    sequence_service as order_sequence_service,
)
from byceps.services.shop.order.transfer.models.number import (
    OrderNumberSequenceID,
)
from byceps.services.shop.shop.transfer.models import Shop
from byceps.services.shop.storefront import service as storefront_service
from byceps.services.shop.storefront.transfer.models import (
    Storefront,
    StorefrontID,
)
from byceps.services.snippet.transfer.models import SnippetID
from byceps.services.user.transfer.models import User

from tests.integration.services.shop.helpers import create_shop_fragment


pytest.register_assert_rewrite(f'{__package__}.helpers')


@pytest.fixture(scope='package')
def order_admin(make_user):
    return make_user()


@pytest.fixture
def make_order_number_sequence_id(shop: Shop):
    def _wrapper(value: int) -> OrderNumberSequenceID:
        sequence_id = order_sequence_service.create_order_number_sequence(
            shop.id, 'AC-14-B', value=value
        )

        if sequence_id is None:
            raise Exception('Got no order number sequence ID')

        return sequence_id

    return _wrapper


@pytest.fixture
def make_storefront(shop: Shop):
    def _wrapper(order_number_sequence_id: OrderNumberSequenceID) -> Storefront:
        return storefront_service.create_storefront(
            StorefrontID(f'{shop.id}-storefront'),
            shop.id,
            order_number_sequence_id,
            closed=False,
        )

    return _wrapper


@pytest.fixture
def email_footer_snippet_id(shop: Shop, order_admin: User) -> SnippetID:
    return create_shop_fragment(
        shop.id,
        order_admin.id,
        'email_footer',
        '''
Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: noreply@acmecon.test
''',
    )


@pytest.fixture
def email_payment_instructions_snippet_id(
    shop: Shop, order_admin: User
) -> SnippetID:
    return create_shop_fragment(
        shop.id,
        order_admin.id,
        'email_payment_instructions',
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
