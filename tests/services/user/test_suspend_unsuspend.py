"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.typing import UserID

from byceps.services.user import command_service as user_command_service
from byceps.services.user import event_service
from byceps.services.user import service as user_service

from tests.base import AbstractAppTestCase
from tests.helpers import create_user


ADMIN_ID = UserID('5a4e04b4-7258-4e61-9f36-090baa683150')


class UserSuspendedFlagTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.user = create_user()

    def test_suspend(self):
        reason = 'User has been caught cheating.'

        user_before = user_service.find_user(self.user.id)
        assert not user_before.suspended

        events_before = event_service.get_events_for_user(user_before.id)
        assert len(events_before) == 0

        # -------------------------------- #

        user_command_service.suspend_account(self.user.id, ADMIN_ID, reason)

        # -------------------------------- #

        user_after = user_service.find_user(self.user.id)
        assert user_after.suspended

        events_after = event_service.get_events_for_user(user_after.id)
        assert len(events_after) == 1

        suspended_event = events_after[0]
        assert suspended_event.event_type == 'user-suspended'
        assert suspended_event.data == {
            'initiator_id': str(ADMIN_ID),
            'reason': reason,
        }

    def test_unsuspend(self):
        user_command_service.suspend_account(self.user.id, ADMIN_ID, 'Annoying')

        reason = 'User showed penitence. Drop the ban.'

        user_before = user_service.find_user(self.user.id)
        assert user_before.suspended

        events_before = event_service.get_events_for_user(user_before.id)
        assert len(events_before) == 1

        # -------------------------------- #

        user_command_service.unsuspend_account(self.user.id, ADMIN_ID, reason)

        # -------------------------------- #

        user_after = user_service.find_user(self.user.id)
        assert not user_after.suspended

        events_after = event_service.get_events_for_user(user_after.id)
        assert len(events_after) == 2

        unsuspended_event = events_after[1]
        assert unsuspended_event.event_type == 'user-unsuspended'
        assert unsuspended_event.data == {
            'initiator_id': str(ADMIN_ID),
            'reason': reason,
        }
