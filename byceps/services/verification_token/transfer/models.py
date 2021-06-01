"""
byceps.services.verification_token.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from enum import Enum


Purpose = Enum(
    'Purpose', ['email_address_confirmation', 'password_reset', 'terms_consent']
)
