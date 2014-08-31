# -*- coding: utf-8 -*-

from byceps.blueprints.authorization_admin.authorization import RolePermission
from byceps.blueprints.orga_admin.authorization import OrgaTeamPermission
from byceps.blueprints.party_admin.authorization import PartyPermission
from byceps.blueprints.snippet_admin.authorization import SnippetPermission
from byceps.blueprints.terms_admin.authorization import TermsPermission
from byceps.blueprints.user_admin.authorization import UserPermission
from byceps.util.navigation import Navigation, NavigationItem


info = Navigation('Informationen')
info.add_item('party.info', 'Partydetails', id='party')
info.add_item('orga.index', 'Orgas', id='orga')
info.add_item('user_group.index', 'Benutzergruppen', id='user_group')
info.add_item('seating.index', 'Sitzplan', id='seating')
info.add_item('terms.view_current', 'AGB', id='terms')
info.add_item('board.category_index', 'Forum', id='board')

admin = Navigation('Verwaltung')
admin.add_item('authorization_admin.role_index', 'Rollen', id='authorization_admin', required_permission=RolePermission.list)
admin.add_item('party_admin.index', 'Parties', id='party_admin', required_permission=PartyPermission.list)
admin.add_item('snippet_admin.index', 'Snippets', id='snippet_admin', required_permission=SnippetPermission.list)
admin.add_item('terms_admin.index', 'AGB', id='terms_admin', required_permission=TermsPermission.list)
admin.add_item('user_admin.index', 'Benutzer', id='user_admin', required_permission=UserPermission.list)
admin.add_item('orga_admin.index', 'Orgateams', id='orga_admin', required_permission=OrgaTeamPermission.list)

blocks = [info, admin]
