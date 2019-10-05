"""
byceps.blueprints.snippet.init
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import current_app

from ...services.snippet import mountpoint_service

from .views import blueprint as snippet_blueprint, view_current_version_by_name


def add_routes_for_snippets(site_id):
    """Register routes for snippets with the application."""
    mountpoints = mountpoint_service.get_mountpoints_for_site(site_id)

    for mountpoint in mountpoints:
        add_route_for_snippet(mountpoint)


def add_route_for_snippet(mountpoint):
    """Register a route for the snippet."""
    endpoint = f'{snippet_blueprint.name}.{mountpoint.endpoint_suffix}'
    defaults = {'name': mountpoint.endpoint_suffix}

    current_app.add_url_rule(
        mountpoint.url_path,
        endpoint,
        view_func=view_current_version_by_name,
        defaults=defaults,
    )
