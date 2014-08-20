# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet.init
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from flask import current_app

from .models import Snippet
from .views import blueprint, view_latest_by_name


def add_routes_for_snippets():
    """Register routes for snippets with the application."""
    party_id = current_app.party_id
    snippets = Snippet.query.for_party_with_id(party_id).all()
    for snippet in snippets:
        add_route_for_snippet(snippet)


def add_route_for_snippet(snippet):
    """Register a route for the snippet."""
    endpoint = '{}.{}'.format(blueprint.name, snippet.name)
    defaults = {'name': snippet.name}

    current_app.add_url_rule(
        snippet.url_path,
        endpoint,
        view_func=view_latest_by_name,
        defaults=defaults)
