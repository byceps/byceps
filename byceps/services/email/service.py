# -*- coding: utf-8 -*-

"""
byceps.services.email.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ... import email


def send_email(*args, **kwargs):
    """Send e-mail."""
    email.send(*args, **kwargs)
