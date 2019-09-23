"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.database import db
from byceps.services.user import command_service as user_command_service
from byceps.services.user.models.detail import UserDetail

from tests.helpers import create_user_with_detail

from ...conftest import database_recreated


@pytest.fixture(scope='module')
def app(admin_app, db):
    with admin_app.app_context():
        with database_recreated(db):
            yield


def test_set_and_remove(app):
    user_id = create_user_with_detail('set-and-remove').id

    # Make sure field is `NULL`.
    assert get_extras(user_id) is None

    # Add first entry.
    user_command_service.set_user_detail_extra(user_id, 'hobbies', 'Science!')
    assert get_extras(user_id) == {'hobbies': 'Science!'}

    # Add second entry.
    user_command_service.set_user_detail_extra(user_id, 'size_of_shoes', 42)
    assert get_extras(user_id) == {'hobbies': 'Science!', 'size_of_shoes': 42}

    # Remove first entry.
    user_command_service.remove_user_detail_extra(user_id, 'hobbies')
    assert get_extras(user_id) == {'size_of_shoes': 42}

    # Remove second entry.
    user_command_service.remove_user_detail_extra(user_id, 'size_of_shoes')
    assert get_extras(user_id) == {}


def test_remove_unknown_key_from_null_extras(app):
    user_id = create_user_with_detail('null-extras').id

    assert get_extras(user_id) is None

    user_command_service.remove_user_detail_extra(user_id, 'dunno')
    assert get_extras(user_id) is None


def test_remove_unknown_key_from_empty_extras(app):
    user_id = create_user_with_detail('empty-extras').id

    set_extras_to_empty_dict(user_id)
    assert get_extras(user_id) == {}

    user_command_service.remove_user_detail_extra(user_id, 'dunno')
    assert get_extras(user_id) == {}


def get_extras(user_id):
    return db.session \
        .query(UserDetail.extras) \
        .filter_by(user_id=user_id) \
        .scalar()


def set_extras_to_empty_dict(user_id):
    detail = UserDetail.query \
        .filter_by(user_id=user_id) \
        .one()

    detail.extras = {}
    db.session.commit()
