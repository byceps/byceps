"""
testfixtures.user
~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date, datetime

from byceps.database import generate_uuid
from byceps.services.user.models.detail import UserDetail
from byceps.services.user import creation_service as user_creation_service


def create_user(screen_name='Faith', *, user_id=None, created_at=None,
                email_address=None, initialized=True, enabled=True):
    if not user_id:
        user_id = generate_uuid()

    if not created_at:
        created_at = datetime.utcnow()

    if not email_address:
        email_address = 'user{}@example.com'.format(user_id)

    user = user_creation_service.build_user(created_at, screen_name,
                                            email_address)
    user.id = user_id
    user.initialized = initialized
    user.enabled = enabled

    return user


def create_user_with_detail(screen_name='Faith', *,
                            user_id=None,
                            email_address=None,
                            initialized=True,
                            enabled=True,
                            first_names='John Joseph',
                            last_name='Doe',
                            date_of_birth=None):
    user = create_user(screen_name, user_id=user_id,
                       email_address=email_address, initialized=initialized,
                       enabled=enabled)

    detail = UserDetail(user=user)
    detail.first_names = first_names
    detail.last_name = last_name
    detail.date_of_birth = (date_of_birth if date_of_birth else date(1993, 2, 15))
    detail.country = 'State of Mind'
    detail.zip_code = '31337'
    detail.city = 'Atrocity'
    detail.street = 'Elite Street 1337'
    detail.phone_number = '555-CALL-ME-MAYBE'

    return user
