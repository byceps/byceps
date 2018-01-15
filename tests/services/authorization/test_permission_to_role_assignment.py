"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.authorization import service

from tests.base import AbstractAppTestCase


class PermissionToRoleAssignmentTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.permission_id = 'board_topic_hide'
        self.permission = service.create_permission(self.permission_id,
                                                    self.permission_id)

        self.role_id = 'board_moderator'
        self.role = service.create_role(self.role_id, self.role_id)

    def test_assign_permission_to_role(self):
        permission_id = self.permission.id
        role_id = self.role.id

        role_permission_ids_before = self.get_permission_ids_for_role(role_id)
        assert self.permission_id not in role_permission_ids_before

        service.assign_permission_to_role(permission_id, role_id)

        role_permission_ids_after = self.get_permission_ids_for_role(role_id)
        assert self.permission_id in role_permission_ids_after

    def test_deassign_permission_from_role(self):
        permission_id = self.permission.id
        role_id = self.role.id

        service.assign_permission_to_role(permission_id, role_id)

        role_permission_ids_before = self.get_permission_ids_for_role(role_id)
        assert self.permission_id in role_permission_ids_before

        service.deassign_permission_from_role(permission_id, role_id)

        role_permission_ids_after = self.get_permission_ids_for_role(role_id)
        assert self.permission_id not in role_permission_ids_after

    # -------------------------------------------------------------------- #
    # helpers

    def get_permission_ids_for_role(self, role_id):
        return {p.id for p in self.role.permissions}
