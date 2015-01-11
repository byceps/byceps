# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from flask import abort

from ...util.framework import create_blueprint

from .service import find_latest_version_of_snippet, SnippetNotFound
from .templating import load_template, render_snippet_as_page, \
    render_snippet_as_partial


blueprint = create_blueprint('snippet', __name__)

blueprint.add_app_template_global(render_snippet_as_partial, 'render_snippet')


def view_latest_by_name(name):
    """Show the latest version of the snippet with the given name."""
    # TODO: Fetch snippet via mountpoint
    # endpoint suffix != snippet name
    try:
        latest_version = find_latest_version_of_snippet(name)
    except SnippetNotFound:
        abort(404)

    return render_snippet_as_page(latest_version)
