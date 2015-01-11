# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from .models import Snippet


def find_latest_version_of_snippet(name):
    snippet = Snippet.query \
        .for_current_party() \
        .filter_by(name=name) \
        .one()
    return snippet.get_latest_version()
