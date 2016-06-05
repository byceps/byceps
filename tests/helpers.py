# -*- coding: utf-8 -*-

"""
tests.helpers
~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from contextlib import contextmanager

from flask import appcontext_pushed, g


@contextmanager
def current_party_set(app, party):
    def handler(sender, **kwargs):
        g.party = party

    with appcontext_pushed.connected_to(handler, app):
        yield


@contextmanager
def current_user_set(app, user):
    def handler(sender, **kwargs):
        g.current_user = user

    with appcontext_pushed.connected_to(handler, app):
        yield
