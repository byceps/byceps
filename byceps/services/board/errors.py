"""
byceps.services.shop.order.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""


class ReactionDeniedError:
    """User's reaction to a posting has been denied.

    Reasons include not being logged in and being the author of the
    posting.
    """


class ReactionExistsError:
    pass


class ReactionDoesNotExistError:
    pass
