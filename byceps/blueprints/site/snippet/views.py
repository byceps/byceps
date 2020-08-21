"""
byceps.blueprints.site.snippet.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g

from ....services.snippet import mountpoint_service
from ....util.framework.blueprint import create_blueprint

from .templating import (
    render_snippet_as_page,
    render_snippet_as_partial,
    url_for_snippet,
)


blueprint = create_blueprint('snippet', __name__)

blueprint.add_app_template_global(render_snippet_as_partial, 'render_snippet')
blueprint.add_app_template_global(url_for_snippet)


@blueprint.route('/<path:url_path>')
def view(url_path):
    """Show the current version of the snippet that is mounted for the
    current site at the given URL path.
    """
    url_path = '/' + url_path

    version = mountpoint_service.find_current_snippet_version_for_url_path(
        g.site_id, url_path
    )

    if version is None:
        abort(404)

    return render_snippet_as_page(version)
