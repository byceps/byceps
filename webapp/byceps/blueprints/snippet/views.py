# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint

from .models import Snippet
from .templating import load_template, render_snippet_as_page, \
    render_snippet_as_partial


blueprint = create_blueprint('snippet', __name__)

blueprint.add_app_template_global(render_snippet_as_partial, 'render_snippet')


def view_latest_by_name(name):
    """Show the latest version of the snippet with the given name."""
    # TODO: Fetch snippet via mountpoint
    # endpoint suffix != snippet name
    snippet = Snippet.query \
        .for_current_party() \
        .filter_by(name=name) \
        .one()
    return render_snippet_as_page(snippet.get_latest_version())
