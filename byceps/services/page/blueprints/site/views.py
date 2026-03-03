"""
byceps.services.page.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from babel import Locale
from flask import abort, g
from flask_babel import get_locale

from byceps.services.page import page_service
from byceps.services.page.models import PageAggregate
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.l10n import get_default_locale

from .templating import render_page, url_for_page


blueprint = create_blueprint('page', __name__)

blueprint.add_app_template_global(url_for_page)


@blueprint.get('/<path:url_path>')
def view(url_path):
    """Show the current version of the page that is mounted for the
    current site at the given URL path.
    """
    url_path = '/' + url_path

    page = _get_current_page(url_path, get_locale())
    if page is None:
        locale = get_default_locale()
        page = _get_current_page(url_path, locale)

    if page is None:
        abort(404)

    if page.hidden:
        abort(404)

    return render_page(page)


def _get_current_page(url_path: str, locale: Locale) -> PageAggregate | None:
    version = page_service.find_current_version_for_url_path(
        g.site.id, url_path, locale.language
    )
    if version is None:
        return None

    page = page_service.get_page(version.page_id)

    return page_service.build_page_aggregate(page, version)
