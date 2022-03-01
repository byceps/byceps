"""
byceps.services.ticketing.exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""


class TicketBelongsToDifferentParty(Exception):
    """Indicate an error caused by the ticket being issued for a
    different party than the one the user is trying to check in for.
    """


class TicketIsRevoked(Exception):
    """Indicate an error caused by the ticket being revoked."""


class TicketLacksUser(Exception):
    """Indicate a (failed) attempt to check a user in with a ticket
    which has no user set.
    """


class UserAccountDeleted(Exception):
    """Indicate that an action failed because the user account has been
    deleted.
    """


class UserAccountSuspended(Exception):
    """Indicate that an action failed because the user account is suspended."""


class UserAlreadyCheckedIn(Exception):
    """Indicate that user check-in failed because a user has already
    been checked in with the ticket.
    """


class UserIdUnknown(Exception):
    """Indicate that a user ID is unknown."""


class SeatChangeDeniedForBundledTicket(Exception):
    """Indicate that the ticket belongs to a bundle and, thus, must not
    be used to occupy (or release) a single seat.
    """


class SeatChangeDeniedForGroupSeat(Exception):
    """Indicate that the seat belongs to a group and, thus, cannot be
    occupied by a single ticket that does not belong to a bundle, and
    cannot be released on its own.
    """


class TicketCategoryMismatch(Exception):
    """Indicate that the provided ticket category does not match the one
    of the target item.
    """
