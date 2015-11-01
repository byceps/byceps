# -*- coding: utf-8 -*-

from byceps.blueprints.authorization_admin.authorization import RolePermission
from byceps.blueprints.board_admin.authorization import BoardCategoryPermission
from byceps.blueprints.news_admin.authorization import NewsItemPermission
from byceps.blueprints.newsletter_admin.authorization import NewsletterPermission
from byceps.blueprints.orga_admin.authorization import OrgaBirthdayPermission, \
    OrgaDetailPermission, OrgaTeamPermission
from byceps.blueprints.orga_presence.authorization import OrgaPresencePermission
from byceps.blueprints.party_admin.authorization import PartyPermission
from byceps.blueprints.shop_admin.authorization import ShopArticlePermission, \
    ShopOrderPermission
from byceps.blueprints.snippet_admin.authorization import SnippetPermission
from byceps.blueprints.terms_admin.authorization import TermsPermission
from byceps.blueprints.ticket_admin.authorization import TicketPermission
from byceps.blueprints.user_admin.authorization import UserPermission
from byceps.util.navigation import Navigation, NavigationItem


users = Navigation('Benutzer')
users.add_item('user_admin.index', 'Benutzer', id='user_admin', required_permission=UserPermission.list)
users.add_item('authorization_admin.role_index', 'Rollen', id='authorization_admin.roles', required_permission=RolePermission.list)
users.add_item('authorization_admin.permission_index', 'Rechte', id='authorization_admin.permissions', required_permission=RolePermission.list)
users.add_item('ticket_admin.index', 'Tickets', id='ticket_admin', required_permission=TicketPermission.list)

orgas = Navigation('Orgas')
orgas.add_item('orga_admin.persons', 'Personen', id='orga_admin.persons', required_permission=OrgaDetailPermission.view)
orgas.add_item('orga_admin.birthdays', 'Geburtstage', id='orga_admin.birthdays', required_permission=OrgaBirthdayPermission.list)
orgas.add_item('orga_admin.teams', 'Teams', id='orga_admin.teams', required_permission=OrgaTeamPermission.list)
orgas.add_item('orga_presence.index', 'Anwesenheit', id='orga_presence', required_permission=OrgaPresencePermission.list)

shop = Navigation('Shop')
shop.add_item('shop_admin.article_index', 'Artikel', id='shop_admin.articles', required_permission=ShopArticlePermission.list)
shop.add_item('shop_admin.order_index', 'Bestellungen', id='shop_admin.orders', required_permission=ShopOrderPermission.list)

misc = Navigation('Verschiedenes')
misc.add_item('party_admin.index', 'Parties', id='party_admin', required_permission=PartyPermission.list)
misc.add_item('snippet_admin.index', 'Snippets', id='snippet_admin', required_permission=SnippetPermission.list)
misc.add_item('news_admin.index', 'News', id='news_admin', required_permission=NewsItemPermission.list)
misc.add_item('terms_admin.index', 'AGB', id='terms_admin', required_permission=TermsPermission.list)
misc.add_item('newsletter_admin.index', 'Newsletter', id='newsletter_admin', required_permission=NewsletterPermission.view_subscriptions)
misc.add_item('board_admin.index', 'Board', id='board_admin', required_permission=BoardCategoryPermission.list)


def get_blocks():
    return [users, orgas, shop, misc]
