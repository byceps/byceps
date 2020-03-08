"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope


def create_shop_fragment(shop_id, admin_id, name, body):
    scope = Scope('shop', shop_id)

    snippet_service.create_fragment(scope, name, admin_id, body)
