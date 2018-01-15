"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.authorization import service

from tests.base import AbstractAppTestCase


class RoleToUserAssignmentTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.permission_id = 'board_topic_hide'

        self.role = create_role_with_permission('board_moderator',
                                                self.permission_id)

        self.user = self.create_user()

    def test_assign_role_to_user(self):
        role_id = self.role.id
        user_id = self.user.id

        user_permission_ids_before = service.get_permission_ids_for_user(user_id)
        assert self.permission_id not in user_permission_ids_before

        service.assign_role_to_user(user_id, role_id)

        user_permission_ids_after = service.get_permission_ids_for_user(user_id)
        assert self.permission_id in user_permission_ids_after

    def test_deassign_role_from_user(self):
        role_id = self.role.id
        user_id = self.user.id

        service.assign_role_to_user(user_id, role_id)

        user_permission_ids_before = service.get_permission_ids_for_user(user_id)
        assert self.permission_id in user_permission_ids_before

        service.deassign_role_from_user(user_id, role_id)

        user_permission_ids_after = service.get_permission_ids_for_user(user_id)
        assert self.permission_id not in user_permission_ids_after


def create_role_with_permission(role_id, permission_id):
    role = service.create_role(role_id, role_id)

    permission = service.create_permission(permission_id, permission_id)
    service.assign_permission_to_role(permission.id, role.id)

    return role
