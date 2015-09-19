# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort

from ...util.framework import create_blueprint

from .service import get_current_version_of_snippet_with_name, SnippetNotFound
from .templating import render_snippet_as_page, render_snippet_as_partial


blueprint = create_blueprint('snippet', __name__)

blueprint.add_app_template_global(render_snippet_as_partial, 'render_snippet')


def view_latest_by_name(name):
    """Show the latest version of the snippet with the given name."""
    # TODO: Fetch snippet via mountpoint
    # endpoint suffix != snippet name
    try:
        current_version = get_current_version_of_snippet_with_name(name)
    except SnippetNotFound:
        abort(404)

    return render_snippet_as_page(current_version)
