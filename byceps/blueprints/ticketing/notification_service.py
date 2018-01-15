"""
byceps.blueprints.ticketing.notification_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import g

from ...services.email import service as email_service
from ...services.party import service as party_service
from ...services.ticketing.models.ticket import Ticket
from ...services.user.models.user import User


def notify_appointed_user(ticket: Ticket, user: User, manager: User) -> None:
    party = party_service.find_party(g.party_id)

    subject = '{} hat dir Ticket {} zugewiesen.' \
        .format(manager.screen_name, ticket.code)

    body = '{} hat dir Ticket {} zugewiesen, was dich zur Teilnahme ' \
        'an der {} berechtigt.' \
        .format(manager.screen_name, ticket.code, party.title)

    _enqueue_email(user, subject, body)


def notify_withdrawn_user(ticket: Ticket, user: User, manager: User) -> None:
    party = party_service.find_party(g.party_id)

    subject = '{} hat Ticket {} zurückgezogen.' \
        .format(manager.screen_name, ticket.code)

    body = '{} hat das dir bisher zugewiesene Ticket {} für die {} ' \
        'zurückgezogen.' \
        .format(manager.screen_name, ticket.code, party.title)

    _enqueue_email(user, subject, body)


def notify_appointed_user_manager(ticket: Ticket, user: User, manager: User
                                 ) -> None:
    party = party_service.find_party(g.party_id)

    subject = '{} hat dir die Nutzerverwaltung für Ticket {} übertragen.' \
        .format(manager.screen_name, ticket.code)

    body = '{} hat dir die Verwaltung des Nutzers von Ticket {} für die {} ' \
        'übertragen.' \
        .format(manager.screen_name, ticket.code, party.title)

    _enqueue_email(user, subject, body)


def notify_withdrawn_user_manager(ticket: Ticket, user: User, manager: User
                                 ) -> None:
    party = party_service.find_party(g.party_id)

    subject = '{} hat die Übertragung der Nutzerverwaltung für Ticket {} ' \
        'an dich zurückgezogen.' \
        .format(manager.screen_name, ticket.code)

    body = '{} hat die dir bisher übertragene Verwaltung des Nutzers ' \
        'von Ticket {} für die {} zurückgezogen.' \
        .format(manager.screen_name, ticket.code, party.title)

    _enqueue_email(user, subject, body)


def notify_appointed_seat_manager(ticket: Ticket, user: User, manager: User
                                 ) -> None:
    party = party_service.find_party(g.party_id)

    subject = '{} hat dir die Sitzplatzverwaltung für Ticket {} übertragen.' \
        .format(manager.screen_name, ticket.code)

    body = '{} hat dir die Verwaltung des Sitzplatzes von Ticket {} ' \
        'für die {} übertragen.' \
        .format(manager.screen_name, ticket.code, party.title)

    _enqueue_email(user, subject, body)


def notify_withdrawn_seat_manager(ticket: Ticket, user: User, manager: User
                                 ) -> None:
    party = party_service.find_party(g.party_id)

    subject = '{} hat die Übertragung der Sitzplatzverwaltung für Ticket {} ' \
        'an dich zurückgezogen.' \
        .format(manager.screen_name, ticket.code)

    body = '{} hat die dir bisher übertragene Verwaltung des Sitzplatzes ' \
        'von Ticket {} für die {} zurückgezogen.' \
        .format(manager.screen_name, ticket.code, party.title)

    _enqueue_email(user, subject, body)


def _enqueue_email(recipient: User, subject: str, body: str) -> None:
    sender_address = email_service.get_sender_address_for_brand(g.brand_id)

    recipients = [recipient.email_address]

    salutation = 'Hallo {},\n\n'.format(recipient.screen_name)
    body = salutation + body

    email_service.enqueue_email(sender_address, recipients, subject, body)
