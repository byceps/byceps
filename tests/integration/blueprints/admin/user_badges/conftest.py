"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.user_badge import badge_service

from tests.helpers import login_user


@pytest.fixture(scope='module')
def user_badge_admin(make_admin):
    permission_ids = {
        'admin.access',
        'user_badge.award',
        'user_badge.create',
        'user_badge.update',
        'user_badge.view',
    }
    admin = make_admin('UserBadgeAdmin', permission_ids)
    login_user(admin.id)
    return admin


@pytest.fixture(scope='module')
def badge():
    slug = 'badge-of-beauty'
    label = 'Badge of Beauty'
    image_filename = 'sooo-beautiful.svg'

    badge = badge_service.create_badge(slug, label, image_filename)

    yield badge

    badge_service.delete_badge(badge.id)
