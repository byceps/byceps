"""
byceps.services.board.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BoardCategoryAlreadyAtBottomError:
    pass


@dataclass(frozen=True)
class BoardCategoryAlreadyAtTopError:
    pass


class ReactionDeniedError:
    """User's reaction to a posting has been denied.

    Reasons include not being logged in and being the author of the
    posting.
    """


class ReactionExistsError:
    pass


class ReactionDoesNotExistError:
    pass
