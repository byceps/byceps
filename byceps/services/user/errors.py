"""
byceps.services.user.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class InvalidScreenNameError:
    """Screen name is invalid."""

    value: str


@dataclass(frozen=True)
class InvalidEmailAddressError:
    """E-mail address is invalid."""

    value: str


@dataclass(frozen=True)
class AccountAlreadyInitializedError:
    """User account cannot be initialized as it has already been."""


@dataclass(frozen=True)
class NothingChangedError:
    """An update was requested but no data has changed."""
