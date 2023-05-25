"""
byceps.services.ticketing.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""


class TicketBelongsToDifferentPartyError(Exception):
    """Indicate an error caused by the ticket being issued for a
    different party than the one the user is trying to check in for.
    """


class TicketIsRevokedError(Exception):
    """Indicate an error caused by the ticket being revoked."""


class TicketLacksUserError(Exception):
    """Indicate a (failed) attempt to check a user in with a ticket
    which has no user set.
    """


class UserAccountDeletedError(Exception):
    """Indicate that an action failed because the user account has been
    deleted.
    """


class UserAccountSuspendedError(Exception):
    """Indicate that an action failed because the user account is suspended."""


class UserAlreadyCheckedInError(Exception):
    """Indicate that user check-in failed because a user has already
    been checked in with the ticket.
    """


class UserIdUnknownError(Exception):
    """Indicate that a user ID is unknown."""


class SeatChangeDeniedForBundledTicketError(Exception):
    """Indicate that the ticket belongs to a bundle and, thus, must not
    be used to occupy (or release) a single seat.
    """


class SeatChangeDeniedForGroupSeatError(Exception):
    """Indicate that the seat belongs to a group and, thus, cannot be
    occupied by a single ticket that does not belong to a bundle, and
    cannot be released on its own.
    """


class TicketCategoryMismatchError(Exception):
    """Indicate that the provided ticket category does not match the one
    of the target item.
    """
