"""
byceps.blueprints.ticketing.notification_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import g

from ...services.email import service as email_service
from ...services.party import service as party_service
from ...services.site import service as site_service
from ...services.ticketing.models.ticket import Ticket
from ...services.user import service as user_service
from ...services.user.transfer.models import User


def notify_appointed_user(ticket: Ticket, user: User, manager: User) -> None:
    party_title = _get_party_title()

    subject = '{} hat dir Ticket {} zugewiesen.' \
        .format(manager.screen_name, ticket.code)

    body = '{} hat dir Ticket {} zugewiesen, was dich zur Teilnahme ' \
        'an der {} berechtigt.' \
        .format(manager.screen_name, ticket.code, party_title)

    _enqueue_email(user, subject, body)


def notify_withdrawn_user(ticket: Ticket, user: User, manager: User) -> None:
    party_title = _get_party_title()

    subject = '{} hat Ticket {} zurückgezogen.' \
        .format(manager.screen_name, ticket.code)

    body = '{} hat das dir bisher zugewiesene Ticket {} für die {} ' \
        'zurückgezogen.' \
        .format(manager.screen_name, ticket.code, party_title)

    _enqueue_email(user, subject, body)


def notify_appointed_user_manager(
    ticket: Ticket, user: User, manager: User
) -> None:
    party_title = _get_party_title()

    subject = '{} hat dir die Nutzerverwaltung für Ticket {} übertragen.' \
        .format(manager.screen_name, ticket.code)

    body = '{} hat dir die Verwaltung des Nutzers von Ticket {} für die {} ' \
        'übertragen.' \
        .format(manager.screen_name, ticket.code, party_title)

    _enqueue_email(user, subject, body)


def notify_withdrawn_user_manager(
    ticket: Ticket, user: User, manager: User
) -> None:
    party_title = _get_party_title()

    subject = '{} hat die Übertragung der Nutzerverwaltung für Ticket {} ' \
        'an dich zurückgezogen.' \
        .format(manager.screen_name, ticket.code)

    body = '{} hat die dir bisher übertragene Verwaltung des Nutzers ' \
        'von Ticket {} für die {} zurückgezogen.' \
        .format(manager.screen_name, ticket.code, party_title)

    _enqueue_email(user, subject, body)


def notify_appointed_seat_manager(
    ticket: Ticket, user: User, manager: User
) -> None:
    party_title = _get_party_title()

    subject = '{} hat dir die Sitzplatzverwaltung für Ticket {} übertragen.' \
        .format(manager.screen_name, ticket.code)

    body = '{} hat dir die Verwaltung des Sitzplatzes von Ticket {} ' \
        'für die {} übertragen.' \
        .format(manager.screen_name, ticket.code, party_title)

    _enqueue_email(user, subject, body)


def notify_withdrawn_seat_manager(
    ticket: Ticket, user: User, manager: User
) -> None:
    party_title = _get_party_title()

    subject = '{} hat die Übertragung der Sitzplatzverwaltung für Ticket {} ' \
        'an dich zurückgezogen.' \
        .format(manager.screen_name, ticket.code)

    body = '{} hat die dir bisher übertragene Verwaltung des Sitzplatzes ' \
        'von Ticket {} für die {} zurückgezogen.' \
        .format(manager.screen_name, ticket.code, party_title)

    _enqueue_email(user, subject, body)


def _get_party_title():
    party = party_service.get_party(g.party_id)
    return party.title


def _enqueue_email(recipient: User, subject: str, body: str) -> None:
    site = site_service.get_site(g.site_id)
    email_config = email_service.get_config(site.email_config_id)
    sender = email_config.sender

    recipient_address = user_service.get_email_address(recipient.id)
    recipients = [recipient_address]

    salutation = 'Hallo {},\n\n'.format(recipient.screen_name)
    body = salutation + body

    email_service.enqueue_email(sender, recipients, subject, body)
