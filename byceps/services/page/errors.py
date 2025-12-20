"""
byceps.services.page.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PageAlreadyExistsError:
    pass


@dataclass(frozen=True)
class PageNotFoundError:
    pass


@dataclass(frozen=True)
class PageDeletionFailedError:
    pass
