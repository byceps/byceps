"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.authentication.password.models import Credential
from byceps.services.authentication.password import service as password_service
from byceps.services.user import event_service

from tests.base import AbstractAppTestCase


class UpdatePasswordHashTest(AbstractAppTestCase):

    def test_update_password_hash(self):
        orga_id = self.create_user('Party_Orga').id

        user = self.create_user('Party_User')
        user_id = user.id
        password_service.create_password_hash(user_id, 'InitialPassw0rd')

        password_hash_before = get_password_hash(user_id)
        assert password_hash_before is not None

        events_before = event_service.get_events_for_user(user_id)
        assert len(events_before) == 0

        # -------------------------------- #

        password_service.update_password_hash(user_id, 'ReplacementPassw0rd', orga_id)

        # -------------------------------- #

        password_hash_after = get_password_hash(user_id)
        assert password_hash_after is not None
        assert password_hash_after != password_hash_before

        events_after = event_service.get_events_for_user(user_id)
        assert len(events_after) == 1

        password_updated_event = events_after[0]
        assert password_updated_event.event_type == 'password-updated'
        assert password_updated_event.data == {
            'initiator_id': str(orga_id),
        }


def get_password_hash(user_id):
    credential = Credential.query.get(user_id)
    return credential.password_hash
