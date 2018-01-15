"""
bootstrap.authorization
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.blueprints.authorization_admin.authorization import RolePermission
from byceps.blueprints.board.authorization import BoardPermission, \
    BoardPostingPermission, BoardTopicPermission
from byceps.blueprints.orga_team_admin.authorization import OrgaTeamPermission
from byceps.blueprints.party_admin.authorization import PartyPermission
from byceps.blueprints.snippet_admin.authorization import \
    MountpointPermission, SnippetPermission
from byceps.blueprints.terms_admin.authorization import TermsPermission
from byceps.blueprints.user_admin.authorization import UserPermission
from byceps.services.authorization import service as authorization_service


def create_roles_and_permissions():
    create_role_with_permissions(
        'authorization_admin',
        'Rechte und Rollen verwalten',
        [
            (RolePermission.list, 'Rollen auflisten'),
        ])

    create_role_with_permissions(
        'board_user',
        'im Forum schreiben',
        [
            (BoardPostingPermission.create, 'Beiträge im Forum erstellen'),
            (BoardPostingPermission.update, 'Beiträge im Forum bearbeiten'),
            (BoardTopicPermission.create, 'Themen im Forum erstellen'),
            (BoardTopicPermission.update, 'Themen im Forum bearbeiten'),
        ])

    create_role_with_permissions(
        'board_orga',
        'versteckte Themen und Beiträge im Forum lesen',
        [
            (BoardPermission.view_hidden, 'versteckte Themen und Beiträge im Forum anzeigen'),
        ])

    create_role_with_permissions(
        'board_moderator',
        'Forum moderieren',
        [
            (BoardPermission.hide, 'Themen und Beiträge im Forum verstecken'),
            (BoardTopicPermission.lock, 'Themen im Forum schließen'),
            (BoardTopicPermission.pin, 'Themen im Forum anpinnen'),
        ])

    create_role_with_permissions(
        'orga_team_admin',
        'Orgateams verwalten',
        [
            (OrgaTeamPermission.list, 'Orga-Teams auflisten'),
            (OrgaTeamPermission.create, 'Orga-Teams erstellen'),
            (OrgaTeamPermission.delete, 'Orga-Teams entfernen'),
            (OrgaTeamPermission.administrate_memberships, 'Orga-Team-Mitgliedschaften verwalten'),
        ])

    create_role_with_permissions(
        'party_admin',
        'Partys verwalten',
        [
            (PartyPermission.list, 'Partys auflisten'),
            (PartyPermission.create, 'Partys anlegen'),
        ])

    create_role_with_permissions(
        'snippet_admin',
        'Snippets verwalten',
        [
            (MountpointPermission.create, 'Snippet-Mountpoints erstellen'),
            (MountpointPermission.delete, 'Snippet-Mountpoints löschen'),
        ])

    create_role_with_permissions(
        'snippet_editor',
        'Snippets bearbeiten',
        [
            (SnippetPermission.list, 'Snippets auflisten'),
            (SnippetPermission.create, 'Snippets erstellen'),
            (SnippetPermission.update, 'Snippets bearbeiten'),
            (SnippetPermission.view_history, 'Versionsverlauf von Snippets anzeigen'),
        ])

    create_role_with_permissions(
        'terms_editor',
        'AGB verwalten',
        [
            (TermsPermission.list, 'AGB-Versionen auflisten'),
            (TermsPermission.create, 'neue AGB-Versionen erstellen'),
        ])

    create_role_with_permissions(
        'user_admin',
        'Benutzer verwalten',
        [
            (UserPermission.list, 'Benutzer auflisten'),
            (UserPermission.view, 'Benutzer ansehen'),
        ])


# -------------------------------------------------------------------- #
# helpers


def create_role_with_permissions(role_id, role_title, permissions_and_titles):
    role = authorization_service.create_role(role_id, role_title)

    for permission_enum_member, permission_title in permissions_and_titles:
        permission_id = permission_enum_member.__key__

        permission = authorization_service.create_permission(permission_id,
                                                             permission_title)
        authorization_service.assign_permission_to_role(permission.id, role.id)


def add_roles_to_user(roles, user):
    for role in roles:
        authorization_service.assign_role_to_user(role, user)
