# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet.init
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from flask import current_app

from .models import Mountpoint
from .views import blueprint, view_latest_by_name


def add_routes_for_snippets(party_id):
    """Register routes for snippets with the application."""
    mountpoints = Mountpoint.query.for_party_with_id(party_id).all()
    for mountpoint in mountpoints:
        add_route_for_snippet(mountpoint)


def add_route_for_snippet(mountpoint):
    """Register a route for the snippet."""
    endpoint = '{}.{}'.format(blueprint.name, mountpoint.endpoint_suffix)
    defaults = {'name': mountpoint.snippet.name}

    current_app.add_url_rule(
        mountpoint.url_path,
        endpoint,
        view_func=view_latest_by_name,
        defaults=defaults)
