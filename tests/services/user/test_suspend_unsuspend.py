"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.typing import UserID

from byceps.services.user import event_service, service as user_service

from tests.base import AbstractAppTestCase


ADMIN_ID = UserID('5a4e04b4-7258-4e61-9f36-090baa683150')


class UserSuspendedFlagTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.user = self.create_user()

    def test_suspend(self):
        reason = 'User has been caught cheating.'

        user_before = user_service.find_user(self.user.id)
        assert not user_before.suspended

        events_before = event_service.get_events_for_user(user_before.id)
        assert len(events_before) == 0

        # -------------------------------- #

        user_service.suspend_account(self.user.id, ADMIN_ID, reason)

        # -------------------------------- #

        user_after = user_service.find_user(self.user.id)
        assert user_after.suspended

        events_after = event_service.get_events_for_user(user_after.id)
        assert len(events_after) == 1

        user_enabled_event = events_after[0]
        assert user_enabled_event.event_type == 'user-suspended'
        assert user_enabled_event.data == {
            'initiator_id': str(ADMIN_ID),
            'reason': reason,
        }

    def test_unsuspend(self):
        self.user.suspended = True

        reason = 'User showed penitence. Drop the ban.'

        user_before = user_service.find_user(self.user.id)
        assert user_before.suspended

        events_before = event_service.get_events_for_user(user_before.id)
        assert len(events_before) == 0

        # -------------------------------- #

        user_service.unsuspend_account(self.user.id, ADMIN_ID, reason)

        # -------------------------------- #

        user_after = user_service.find_user(self.user.id)
        assert not user_after.suspended

        events_after = event_service.get_events_for_user(user_after.id)
        assert len(events_after) == 1

        user_disabled_event = events_after[0]
        assert user_disabled_event.event_type == 'user-unsuspended'
        assert user_disabled_event.data == {
            'initiator_id': str(ADMIN_ID),
            'reason': reason,
        }
