"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.snippet.transfer.models import Scope

from tests.helpers import log_in_user


@pytest.fixture(scope='package')
def snippet_admin(make_admin):
    permission_ids = {
        'admin.access',
        'snippet.create',
        'snippet.update',
        'snippet.delete',
        'snippet.view',
        'snippet.view_history',
        'snippet_mountpoint.create',
        'snippet_mountpoint.delete',
    }
    admin = make_admin('SnippetAdmin', permission_ids)
    log_in_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def snippet_admin_client(make_client, admin_app, snippet_admin):
    return make_client(admin_app, user_id=snippet_admin.id)


@pytest.fixture(scope='package')
def global_scope():
    return Scope('global', 'global')
