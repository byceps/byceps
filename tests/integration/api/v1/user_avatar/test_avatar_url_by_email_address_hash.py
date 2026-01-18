"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import hashlib
from pathlib import Path

from secret_type import secret

from byceps.services.user import (
    user_avatar_service,
    user_command_service,
    user_creation_service,
)
from byceps.util.image.image_type import ImageType


def test_existent_user_with_avatar(api_client):
    email_address = 'user1@users.test'
    user = create_initialized_user('UserWithAvatar', email_address)
    avatar_id = set_avatar(user)
    email_address_hash = hash_email_address(email_address)

    response = send_request(api_client, email_address_hash)

    assert response.status_code == 302
    assert_redirect(response, f'/data/global/users/avatars/{avatar_id}.jpeg')


def test_existent_user_without_avatar(api_client):
    email_address = 'user2@users.test'
    create_initialized_user('UserWithoutAvatar', email_address)
    email_address_hash = hash_email_address(email_address)

    response = send_request(api_client, email_address_hash)

    assert_redirect(response, '/static/user_avatar_fallback.svg')


def test_unrecognized_hash(api_client):
    unrecognized_email_address_hash = '00000000000000000000000000000000'

    response = send_request(api_client, unrecognized_email_address_hash)

    assert_redirect(response, '/static/user_avatar_fallback.svg')


# helpers


def create_initialized_user(screen_name, email_address):
    password = secret('long enough')
    user, _ = user_creation_service.create_user(
        screen_name, email_address, password
    ).unwrap()
    user_command_service.initialize_account(user, assign_roles=False)
    return user


def set_avatar(user):
    with Path('tests/fixtures/images/image.jpeg').open('rb') as f:
        avatar, _ = user_avatar_service.update_avatar_image(
            user, f, {ImageType.jpeg}, user
        ).unwrap()
    return avatar.id


def hash_email_address(email_address):
    return hashlib.md5(
        email_address.encode('utf-8'), usedforsecurity=False
    ).hexdigest()  # noqa: S324


def send_request(api_client, email_address_hash):
    url = f'http://api.acmecon.test/v1/user_avatars/by_email_hash/{email_address_hash}'
    return api_client.get(url)


def assert_redirect(response, expected_location):
    assert response.status_code == 302
    assert response.location == expected_location
