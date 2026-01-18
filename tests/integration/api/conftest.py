"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)

API-specific fixtures
"""

import pytest

from byceps.services.authn.api import authn_api_service
from byceps.services.authn.api.models import ApiToken
from byceps.services.authz.models import PermissionID


@pytest.fixture(scope='package')
def api_client(api_app):
    """Provide a test HTTP client against the API."""
    return api_app.test_client()


@pytest.fixture(scope='package')
def api_token(admin_user) -> ApiToken:
    permissions: set[PermissionID] = set()
    return authn_api_service.create_api_token(admin_user.id, permissions)


@pytest.fixture(scope='package')
def api_client_authz_header(api_token: ApiToken):
    return 'Authorization', f'Bearer {api_token.token}'
