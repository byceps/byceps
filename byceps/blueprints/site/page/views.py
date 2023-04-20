"""
byceps.blueprints.site.page.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g

from byceps.services.page import page_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.l10n import get_default_locale, get_locale_str

from .templating import render_page, url_for_page


blueprint = create_blueprint('page', __name__)

blueprint.add_app_template_global(url_for_page)


@blueprint.get('/<path:url_path>')
def view(url_path):
    """Show the current version of the page that is mounted for the
    current site at the given URL path.
    """
    url_path = '/' + url_path

    version = _get_page_version(url_path, get_locale_str())
    if version is None:
        version = _get_page_version(url_path, get_default_locale())

    if version is None:
        abort(404)

    page = page_service.get_page(version.page_id)

    return render_page(page, version)


def _get_page_version(url_path: str, language_code: str):
    return page_service.find_current_version_for_url_path(
        g.site_id, url_path, language_code
    )
