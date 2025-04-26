"""
byceps.services.ticketing.blueprints.site.notification_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import g
from flask_babel import gettext

from byceps.services.email import email_config_service, email_service
from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.util.l10n import force_user_locale


def notify_appointed_user(ticket: DbTicket, user: User, manager: User) -> None:
    party_title = g.party.title

    with force_user_locale(user):
        subject = gettext(
            '%(screen_name)s has assigned ticket %(ticket_code)s to you.',
            screen_name=manager.screen_name,
            ticket_code=ticket.code,
        )

        body = gettext(
            '%(screen_name)s has assigned ticket %(ticket_code)s to you which entitles you to attend %(party_title)s.',
            screen_name=manager.screen_name,
            ticket_code=ticket.code,
            party_title=party_title,
        )

    _enqueue_email(user, subject, body)


def notify_withdrawn_user(ticket: DbTicket, user: User, manager: User) -> None:
    party_title = g.party.title

    with force_user_locale(user):
        subject = gettext(
            '%(screen_name)s has withdrawn ticket %(ticket_code)s from you.',
            screen_name=manager.screen_name,
            ticket_code=ticket.code,
        )

        body = gettext(
            '%(screen_name)s has withdrawn ticket %(ticket_code)s for %(party_title)s, which was previously assigned to you, from you.',
            screen_name=manager.screen_name,
            ticket_code=ticket.code,
            party_title=party_title,
        )

    _enqueue_email(user, subject, body)


def notify_appointed_user_manager(
    ticket: DbTicket, user: User, manager: User
) -> None:
    party_title = g.party.title

    with force_user_locale(user):
        subject = gettext(
            '%(screen_name)s has assigned user management for ticket %(ticket_code)s to you.',
            screen_name=manager.screen_name,
            ticket_code=ticket.code,
        )

        body = gettext(
            '%(screen_name)s has assigned user management for ticket %(ticket_code)s for %(party_title)s to you.',
            screen_name=manager.screen_name,
            ticket_code=ticket.code,
            party_title=party_title,
        )

    _enqueue_email(user, subject, body)


def notify_withdrawn_user_manager(
    ticket: DbTicket, user: User, manager: User
) -> None:
    party_title = g.party.title

    with force_user_locale(user):
        subject = gettext(
            '%(screen_name)s has withdrawn user management for ticket %(ticket_code)s from you.',
            screen_name=manager.screen_name,
            ticket_code=ticket.code,
        )

        body = gettext(
            '%(screen_name)s has withdrawn user management for ticket %(ticket_code)s for %(party_title)s, which was previously assigned to you, from you.',
            screen_name=manager.screen_name,
            ticket_code=ticket.code,
            party_title=party_title,
        )

    _enqueue_email(user, subject, body)


def notify_appointed_seat_manager(
    ticket: DbTicket, user: User, manager: User
) -> None:
    party_title = g.party.title

    with force_user_locale(user):
        subject = gettext(
            '%(screen_name)s has assigned seat management for ticket %(ticket_code)s to you.',
            screen_name=manager.screen_name,
            ticket_code=ticket.code,
        )

        body = gettext(
            '%(screen_name)s has assigned seat management for ticket %(ticket_code)s for %(party_title)s to you.',
            screen_name=manager.screen_name,
            ticket_code=ticket.code,
            party_title=party_title,
        )

    _enqueue_email(user, subject, body)


def notify_withdrawn_seat_manager(
    ticket: DbTicket, user: User, manager: User
) -> None:
    party_title = g.party.title

    with force_user_locale(user):
        subject = gettext(
            '%(screen_name)s has withdrawn seat management for ticket %(ticket_code)s from you.',
            screen_name=manager.screen_name,
            ticket_code=ticket.code,
        )

        body = gettext(
            '%(screen_name)s has withdrawn seat management for ticket %(ticket_code)s for %(party_title)s, which was previously assigned to you, from you.',
            screen_name=manager.screen_name,
            ticket_code=ticket.code,
            party_title=party_title,
        )

    _enqueue_email(user, subject, body)


def _enqueue_email(recipient: User, subject: str, body: str) -> None:
    email_config = email_config_service.get_config(g.site.brand_id)
    sender = email_config.sender

    recipient_address = user_service.get_email_address(recipient.id)
    recipients = [recipient_address]

    with force_user_locale(recipient):
        salutation = (
            gettext('Hello %(screen_name)s,', screen_name=recipient.screen_name)
            + '\n\n'
        )
    body = salutation + body

    email_service.enqueue_email(sender, recipients, subject, body)
