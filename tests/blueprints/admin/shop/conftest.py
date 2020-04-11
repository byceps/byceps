"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.shop.shop import service as shop_service


@pytest.fixture(scope='module')
def shop(make_email_config):
    email_config = make_email_config()
    return shop_service.create_shop('shop-01', 'Some Shop', email_config.id)
