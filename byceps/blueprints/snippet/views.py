"""
byceps.blueprints.snippet.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g

from ...services.snippet import mountpoint_service
from ...util.framework.blueprint import create_blueprint

from .templating import render_snippet_as_page, render_snippet_as_partial


blueprint = create_blueprint('snippet', __name__)

blueprint.add_app_template_global(render_snippet_as_partial, 'render_snippet')


def view_current_version_by_name(name):
    """Show the current version of the snippet that is mounted with that
    name.
    """
    # Note: endpoint suffix != snippet name
    version = mountpoint_service.find_current_snippet_version_for_mountpoint(
        g.site_id, name
    )

    if version is None:
        abort(404)

    return render_snippet_as_page(version)
