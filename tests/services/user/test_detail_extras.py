"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.database import db
from byceps.services.user.models.detail import UserDetail
from byceps.services.user import service as user_service

from tests.base import AbstractAppTestCase


class UserDetailExtrasTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.user_id = self.create_user_with_detail().id

    def test_set_and_remove(self):
        # Make sure field is `NULL`.
        assert self.get_extras() is None

        # Add first entry.
        user_service.set_user_detail_extra(self.user_id, 'hobbies', 'Science!')
        assert self.get_extras() == {'hobbies': 'Science!'}

        # Add second entry.
        user_service.set_user_detail_extra(self.user_id, 'size_of_shoes', 42)
        assert self.get_extras() == {'hobbies': 'Science!', 'size_of_shoes': 42}

        # Remove first entry.
        user_service.remove_user_detail_extra(self.user_id, 'hobbies')
        assert self.get_extras() == {'size_of_shoes': 42}

        # Remove second entry.
        user_service.remove_user_detail_extra(self.user_id, 'size_of_shoes')
        assert self.get_extras() == {}

    def test_remove_unknown_key_from_null_extras(self):
        assert self.get_extras() is None

        user_service.remove_user_detail_extra(self.user_id, 'dunno')
        assert self.get_extras() is None

    def test_remove_unknown_key_from_empty_extras(self):
        self.set_extras_to_empty_dict()
        assert self.get_extras() == {}

        user_service.remove_user_detail_extra(self.user_id, 'dunno')
        assert self.get_extras() == {}

    def get_extras(self):
        return self.db.session \
            .query(UserDetail.extras) \
            .filter_by(user_id=self.user_id) \
            .scalar()

    def set_extras_to_empty_dict(self):
        detail = UserDetail.query \
            .filter_by(user_id=self.user_id) \
            .one()

        detail.extras = {}
        self.db.session.commit()
