"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.orga import service as orga_service

from testfixtures.user import create_user

from tests.base import AbstractAppTestCase


class OrgaServiceTestCase(AbstractAppTestCase):

    def test_is_user_orga(self):
        user = self.create_user()

        self.assertFalse(orga_service.is_user_orga(user.id))

        orga_service.create_orga_flag(self.brand.id, user.id)

        self.assertTrue(orga_service.is_user_orga(user.id))

    # -------------------------------------------------------------------- #
    # helpers

    def create_user(self):
        user = create_user('Alice')

        self.db.session.add(user)
        self.db.session.commit()

        return user
