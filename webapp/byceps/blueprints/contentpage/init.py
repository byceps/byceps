# -*- coding: utf-8 -*-

"""
byceps.blueprints.contentpage.init
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from flask import current_app

from .models import ContentPage
from .views import blueprint, view_latest_by_name


def add_routes_for_content_pages():
    """Register routes for pages with the application."""
    party_id = current_app.party_id
    pages = ContentPage.query.for_party_with_id(party_id).all()
    for page in pages:
        add_route_for_content_page(page)


def add_route_for_content_page(page):
    """Register a route for the page."""
    endpoint = '{}.{}'.format(blueprint.name, page.name)
    defaults = {'name': page.name}
    current_app.add_url_rule(
        page.url_path,
        endpoint,
        view_func=view_latest_by_name,
        defaults=defaults)
