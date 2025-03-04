"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.snippet import snippet_service
from byceps.services.snippet.dbmodels import DbSnippetVersion
from byceps.services.snippet.events import SnippetCreatedEvent
from byceps.services.snippet.models import SnippetScope
from byceps.services.user.models.user import User

from tests.helpers import generate_token, log_in_user


@pytest.fixture(scope='package')
def snippet_admin(make_admin):
    permission_ids = {
        'admin.access',
        'snippet.create',
        'snippet.update',
        'snippet.delete',
        'snippet.view',
        'snippet.view_history',
    }
    admin = make_admin(permission_ids)
    log_in_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def snippet_admin_client(make_client, admin_app, snippet_admin):
    return make_client(admin_app, user_id=snippet_admin.id)


@pytest.fixture(scope='package')
def global_scope() -> SnippetScope:
    return SnippetScope('global', 'global')


@pytest.fixture()
def make_snippet(global_scope: SnippetScope, snippet_admin: User):
    def _wrapper(
        name: str | None = None,
        language_code: str = 'en',
        body: str = 'Body',
    ) -> tuple[DbSnippetVersion, SnippetCreatedEvent]:
        if name is None:
            name = generate_token()

        version, event = snippet_service.create_snippet(
            global_scope, name, language_code, snippet_admin, body
        )
        return version, event

    return _wrapper
