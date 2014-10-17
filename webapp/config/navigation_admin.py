# -*- coding: utf-8 -*-

from byceps.blueprints.authorization_admin.authorization import RolePermission
from byceps.blueprints.newsletter_admin.authorization import NewsletterPermission
from byceps.blueprints.orga_admin.authorization import OrgaBirthdayPermission, \
    OrgaTeamPermission
from byceps.blueprints.party_admin.authorization import PartyPermission
from byceps.blueprints.shop_admin.authorization import ShopPermission
from byceps.blueprints.snippet_admin.authorization import SnippetPermission
from byceps.blueprints.terms_admin.authorization import TermsPermission
from byceps.blueprints.user_admin.authorization import UserPermission
from byceps.util.navigation import Navigation, NavigationItem


users = Navigation('Benutzer')
users.add_item('user_admin.index', 'Benutzer', id='user_admin', required_permission=UserPermission.list)
users.add_item('authorization_admin.role_index', 'Rollen', id='authorization_admin.roles', required_permission=RolePermission.list)
users.add_item('authorization_admin.permission_index', 'Rechte', id='authorization_admin.permissions', required_permission=RolePermission.list)

orgas = Navigation('Orgas')
orgas.add_item('orga_admin.birthdays', 'Geburtstage', id='orga_admin.birthdays', required_permission=OrgaBirthdayPermission.list)
orgas.add_item('orga_admin.teams', 'Orgateams', id='orga_admin.teams', required_permission=OrgaTeamPermission.list)

shop = Navigation('Shop')
shop.add_item('shop_admin.article_index', 'Artikel', id='shop_admin.articles', required_permission=ShopPermission.list_articles)
shop.add_item('shop_admin.order_index', 'Bestellungen', id='shop_admin.orders', required_permission=ShopPermission.list_orders)

misc = Navigation('Verschiedenes')
misc.add_item('party_admin.index', 'Parties', id='party_admin', required_permission=PartyPermission.list)
misc.add_item('snippet_admin.index', 'Snippets', id='snippet_admin', required_permission=SnippetPermission.list)
misc.add_item('terms_admin.index', 'AGB', id='terms_admin', required_permission=TermsPermission.list)
misc.add_item('newsletter_admin.index', 'Newsletter', id='newsletter_admin', required_permission=NewsletterPermission.view_subscriptions)


def get_blocks():
    return [users, orgas, shop, misc]
