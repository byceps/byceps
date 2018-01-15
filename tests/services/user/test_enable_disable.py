"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.typing import UserID

from byceps.services.user import event_service, service as user_service

from tests.base import AbstractAppTestCase


ADMIN_ID = UserID('5a4e04b4-7258-4e61-9f36-090baa683150')


class UserEnabledFlagTest(AbstractAppTestCase):

    def test_enable(self):
        user_id = self.create_user(enabled=False).id

        user_before = user_service.find_user(user_id)
        assert not user_before.enabled

        events_before = event_service.get_events_for_user(user_before.id)
        assert len(events_before) == 0

        # -------------------------------- #

        user_service.enable_user(user_id, ADMIN_ID)

        # -------------------------------- #

        user_after = user_service.find_user(user_id)
        assert user_after.enabled

        events_after = event_service.get_events_for_user(user_after.id)
        assert len(events_after) == 1

        user_enabled_event = events_after[0]
        assert user_enabled_event.event_type == 'user-enabled'
        assert user_enabled_event.data == {
            'initiator_id': str(ADMIN_ID),
        }

    def test_disable(self):
        user_id = self.create_user(enabled=True).id

        user_before = user_service.find_user(user_id)
        assert user_before.enabled

        events_before = event_service.get_events_for_user(user_before.id)
        assert len(events_before) == 0

        # -------------------------------- #

        user_service.disable_user(user_id, ADMIN_ID)

        # -------------------------------- #

        user_after = user_service.find_user(user_id)
        assert not user_after.enabled

        events_after = event_service.get_events_for_user(user_after.id)
        assert len(events_after) == 1

        user_disabled_event = events_after[0]
        assert user_disabled_event.event_type == 'user-disabled'
        assert user_disabled_event.data == {
            'initiator_id': str(ADMIN_ID),
        }
