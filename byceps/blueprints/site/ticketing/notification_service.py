"""
byceps.blueprints.site.ticketing.notification_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import g

from ....services.email import service as email_service
from ....services.party import service as party_service
from ....services.site import service as site_service
from ....services.ticketing.models.ticket import Ticket
from ....services.user import service as user_service
from ....services.user.transfer.models import User


def notify_appointed_user(ticket: Ticket, user: User, manager: User) -> None:
    party_title = _get_party_title()

    subject = f'{manager.screen_name} hat dir Ticket {ticket.code} zugewiesen.'

    body = (
        f'{manager.screen_name} hat dir Ticket {ticket.code} zugewiesen, '
        f'was dich zur Teilnahme an der {party_title} berechtigt.'
    )

    _enqueue_email(user, subject, body)


def notify_withdrawn_user(ticket: Ticket, user: User, manager: User) -> None:
    party_title = _get_party_title()

    subject = f'{manager.screen_name} hat Ticket {ticket.code} zurückgezogen.'

    body = (
        f'{manager.screen_name} hat das dir bisher zugewiesene Ticket '
        f'{ticket.code} für die {party_title} zurückgezogen.'
    )

    _enqueue_email(user, subject, body)


def notify_appointed_user_manager(
    ticket: Ticket, user: User, manager: User
) -> None:
    party_title = _get_party_title()

    subject = (
        f'{manager.screen_name} hat dir die Nutzerverwaltung '
        f'für Ticket {ticket.code} übertragen.'
    )

    body = (
        f'{manager.screen_name} hat dir die Verwaltung des Nutzers '
        f'von Ticket {ticket.code} für die {party_title} übertragen.'
    )

    _enqueue_email(user, subject, body)


def notify_withdrawn_user_manager(
    ticket: Ticket, user: User, manager: User
) -> None:
    party_title = _get_party_title()

    subject = (
        f'{manager.screen_name} hat die Übertragung der Nutzerverwaltung '
        f'für Ticket {ticket.code} an dich zurückgezogen.'
    )

    body = (
        f'{manager.screen_name} hat die dir bisher übertragene Verwaltung '
        f'des Nutzers von Ticket {ticket.code} für die {party_title} '
        'zurückgezogen.'
    )

    _enqueue_email(user, subject, body)


def notify_appointed_seat_manager(
    ticket: Ticket, user: User, manager: User
) -> None:
    party_title = _get_party_title()

    subject = (
        f'{manager.screen_name} hat dir die Sitzplatzverwaltung '
        f'für Ticket {ticket.code} übertragen.'
    )

    body = (
        f'{manager.screen_name} hat dir die Verwaltung des Sitzplatzes '
        f'von Ticket {ticket.code} für die {party_title} übertragen.'
    )

    _enqueue_email(user, subject, body)


def notify_withdrawn_seat_manager(
    ticket: Ticket, user: User, manager: User
) -> None:
    party_title = _get_party_title()

    subject = (
        f'{manager.screen_name} hat die Übertragung der Sitzplatzverwaltung '
        f'für Ticket {ticket.code} an dich zurückgezogen.'
    )

    body = (
        f'{manager.screen_name} hat die dir bisher übertragene Verwaltung '
        f'des Sitzplatzes von Ticket {ticket.code} für die {party_title} '
        'zurückgezogen.'
    )

    _enqueue_email(user, subject, body)


def _get_party_title():
    party = party_service.get_party(g.party_id)
    return party.title


def _enqueue_email(recipient: User, subject: str, body: str) -> None:
    site = site_service.get_site(g.site_id)
    email_config = email_service.get_config_for_brand(site.brand_id)
    sender = email_config.sender

    recipient_address = user_service.get_email_address(recipient.id)
    recipients = [recipient_address]

    salutation = f'Hallo {recipient.screen_name},\n\n'
    body = salutation + body

    email_service.enqueue_email(sender, recipients, subject, body)
