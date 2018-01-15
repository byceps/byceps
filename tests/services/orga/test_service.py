"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.orga import service as orga_service

from tests.base import AbstractAppTestCase


class OrgaServiceTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()

    def test_is_user_orga(self):
        user = self.create_user()

        assert not orga_service.is_user_orga(user.id)

        orga_service.create_orga_flag(self.brand.id, user.id)

        assert orga_service.is_user_orga(user.id)
