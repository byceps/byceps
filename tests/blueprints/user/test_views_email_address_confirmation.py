"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.authorization import service as authorization_service

from tests.base import AbstractAppTestCase
from tests.helpers import (
    create_email_config,
    create_site,
    create_user,
    http_client,
)

from testfixtures.verification_token import (
    create_verification_token_for_email_address_confirmation as create_confirmation_token,
)


class EmailAddressConfirmationTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        create_email_config()
        create_site()

        self.user = create_user(initialized=False)
        assert not self.user.initialized

    def test_confirm_email_address_with_valid_token(self):
        authorization_service.create_role('board_user', 'Board User')

        verification_token = create_confirmation_token(self.user.id)
        self.db.session.add(verification_token)
        self.db.session.commit()

        # -------------------------------- #

        response = self._confirm(verification_token)

        # -------------------------------- #

        assert response.status_code == 302
        assert self.user.initialized
        assert _get_role_ids(self.user.id) == {'board_user'}

    def test_confirm_email_address_with_unknown_token(self):
        verification_token = create_confirmation_token(self.user.id)
        verification_token.token = 'wZdSLzkT-zRf2x2T6AR7yGa3Nc_X3Nn3F3XGPvPtOhw'

        # -------------------------------- #

        response = self._confirm(verification_token)

        # -------------------------------- #

        assert response.status_code == 404
        assert not self.user.initialized
        assert _get_role_ids(self.user.id) == set()

    def _confirm(self, verification_token):
        url = f'/users/email_address/confirmation/{verification_token.token}'
        with http_client(self.app) as client:
            return client.get(url)


def _get_role_ids(user_id):
    return authorization_service.find_role_ids_for_user(user_id)
