"""
byceps.blueprints.snippet.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from blinker import Namespace


snippet_signals = Namespace()


snippet_created = snippet_signals.signal('snippet-created')
snippet_updated = snippet_signals.signal('snippet-updated')
snippet_deleted = snippet_signals.signal('snippet-deleted')
