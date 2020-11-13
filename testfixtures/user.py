"""
testfixtures.user
~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date, datetime

from byceps.database import generate_uuid
from byceps.services.user.models.detail import UserDetail
from byceps.services.user import creation_service as user_creation_service


def create_user(
    screen_name='Faith',
    *,
    user_id=None,
    created_at=None,
    email_address=None,
    email_address_verified=False,
    initialized=True,
    suspended=False,
    deleted=False,
    legacy_id=None,
):
    if not user_id:
        user_id = generate_uuid()

    if not created_at:
        created_at = datetime.utcnow()

    if not email_address:
        email_address = f'user{user_id}@users.test'

    user = user_creation_service.build_user(
        created_at, screen_name, email_address
    )
    user.id = user_id
    user.email_address_verified = email_address_verified
    user.initialized = initialized
    user.suspended = suspended
    user.deleted = deleted
    user.legacy_id = legacy_id

    return user


DEFAULT_DATE_OF_BIRTH = date(1993, 2, 15)


def create_user_with_detail(
    screen_name='Faith',
    *,
    user_id=None,
    email_address=None,
    initialized=True,
    suspended=False,
    deleted=False,
    legacy_id=None,
    first_names='John Joseph',
    last_name='Doe',
    date_of_birth=DEFAULT_DATE_OF_BIRTH,
    country='State of Mind',
    zip_code='31337',
    city='Atrocity',
    street='Elite Street 1337',
    phone_number='555-CALL-ME-MAYBE',
):
    user = create_user(
        screen_name,
        user_id=user_id,
        email_address=email_address,
        initialized=initialized,
        suspended=suspended,
        deleted=deleted,
        legacy_id=legacy_id,
    )

    detail = UserDetail(user=user)
    detail.first_names = first_names
    detail.last_name = last_name
    detail.date_of_birth = date_of_birth
    detail.country = country
    detail.zip_code = zip_code
    detail.city = city
    detail.street = street
    detail.phone_number = phone_number

    return user
