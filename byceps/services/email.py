# -*- coding: utf-8 -*-

"""
byceps.services.email
~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from .. import email


def send(*args, **kwargs):
    """Send e-mail."""
    email.send(*args, **kwargs)
