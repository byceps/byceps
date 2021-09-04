"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.database import db
from byceps.services.user import command_service as user_command_service
from byceps.services.user.dbmodels.detail import UserDetail


def test_set_and_remove(admin_app, make_user):
    user_id = make_user('set-and-remove').id

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


def test_remove_unknown_key_from_null_extras(admin_app, make_user):
    user_id = make_user('null-extras').id

    assert get_extras(user_id) is None

    user_command_service.remove_user_detail_extra(user_id, 'dunno')
    assert get_extras(user_id) is None


def test_remove_unknown_key_from_empty_extras(admin_app, make_user):
    user_id = make_user('empty-extras').id

    set_extras_to_empty_dict(user_id)
    assert get_extras(user_id) == {}

    user_command_service.remove_user_detail_extra(user_id, 'dunno')
    assert get_extras(user_id) == {}


# helpers


def get_extras(user_id):
    return db.session \
        .query(UserDetail.extras) \
        .filter_by(user_id=user_id) \
        .scalar()


def set_extras_to_empty_dict(user_id):
    detail = db.session \
        .query(UserDetail) \
        .filter_by(user_id=user_id) \
        .one()

    detail.extras = {}
    db.session.commit()
