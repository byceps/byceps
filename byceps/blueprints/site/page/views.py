"""
byceps.blueprints.site.page.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g

from ....services.page import service as page_service
from ....util.framework.blueprint import create_blueprint

from .templating import render_page


blueprint = create_blueprint('page', __name__)


@blueprint.get('/<path:url_path>')
def view(url_path):
    """Show the current version of the page that is mounted for the
    current site at the given URL path.
    """
    url_path = '/' + url_path

    version = page_service.find_current_version_for_url_path(
        g.site_id, url_path
    )

    if version is None:
        abort(404)

    page = page_service.get_page(version.page_id)

    return render_page(page, version)
