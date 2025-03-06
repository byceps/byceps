"""
byceps.services.authz.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


authz_signals = Namespace()


role_assigned_to_user = authz_signals.signal('role-assigned-to-user')
role_deassigned_from_user = authz_signals.signal('role-deassigned-from-user')
