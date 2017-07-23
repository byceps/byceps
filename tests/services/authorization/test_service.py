"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.authorization import service as authorization_service

from testfixtures.user import create_user

from tests.base import AbstractAppTestCase


class AuthorizationServiceTestCase(AbstractAppTestCase):

    def test_get_permission_ids_for_user(self):
        board_moderator_role = self.create_role_with_permissions('board_moderator', [
            'board_topic_hide',
            'board_topic_pin',
        ])
        news_editor_role = self.create_role_with_permissions('news_editor', [
            'news_item_create',
        ])

        user = self.create_user()

        permissions_before = authorization_service.get_permission_ids_for_user(user.id)
        self.assertEqual(permissions_before, frozenset())

        self.assign_roles_to_user(user.id, {board_moderator_role, news_editor_role})

        permissions_after = authorization_service.get_permission_ids_for_user(user.id)
        self.assertEqual(permissions_after, {
            'board_topic_hide',
            'board_topic_pin',
            'news_item_create',
        })

    # -------------------------------------------------------------------- #
    # helpers

    def create_user(self):
        user = create_user('Alice')

        self.db.session.add(user)
        self.db.session.commit()

        return user

    def create_role_with_permissions(self, role_id, permission_ids):
        role = authorization_service.create_role(role_id, role_id)

        for permission_id in permission_ids:
            permission = authorization_service.create_permission(permission_id,
                                                                 permission_id)
            authorization_service.assign_permission_to_role(permission.id, role.id)

        return role

    def assign_roles_to_user(self, user_id, roles):
        for role in roles:
            authorization_service.assign_role_to_user(user_id, role.id)
