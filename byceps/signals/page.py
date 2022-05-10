"""
byceps.signals.page
~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


page_signals = Namespace()


page_created = page_signals.signal('page-created')
page_updated = page_signals.signal('page-updated')
page_deleted = page_signals.signal('page-deleted')
