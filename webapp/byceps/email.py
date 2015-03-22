# -*- coding: utf-8 -*-

"""
byceps.email
~~~~~~~~~~~~

Sending e-mail.

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from flask_mail import Mail


_mail = Mail()


def init_app(app):
    _mail.init_app(app)


def send(*args, **kwargs):
    _mail.send_message(*args, **kwargs)
