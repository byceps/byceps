"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.authentication.api import authn_api_domain_service
from byceps.services.authorization.models import PermissionID
from byceps.typing import UserID

from tests.helpers import generate_uuid


def test_create_api_token():
    creator_id = UserID(generate_uuid())
    permissions = set([PermissionID('do_this'), PermissionID('do_that')])
    num_bytes = 64
    description = 'For this and that'

    actual = authn_api_domain_service.create_api_token(
        creator_id, permissions, num_bytes=num_bytes, description=description
    )

    assert actual.id is not None
    assert actual.created_at is not None
    assert len(actual.token) >= 64
    assert actual.token.startswith('api_')
    assert actual.permissions == permissions
    assert actual.description == description
    assert not actual.suspended
