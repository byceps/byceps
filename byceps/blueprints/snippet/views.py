# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g

from ...services.snippet import service as snippet_service
from ...services.snippet.service import SnippetNotFound
from ...util.framework.blueprint import create_blueprint

from .templating import render_snippet_as_page, render_snippet_as_partial


blueprint = create_blueprint('snippet', __name__)

blueprint.add_app_template_global(render_snippet_as_partial, 'render_snippet')


def view_latest_by_name(name):
    """Show the latest version of the snippet with the given name."""
    # TODO: Fetch snippet via mountpoint
    # endpoint suffix != snippet name
    try:
        current_version = snippet_service \
            .get_current_version_of_snippet_with_name(g.party, name)
    except SnippetNotFound:
        abort(404)

    return render_snippet_as_page(current_version)
