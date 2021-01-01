"""
byceps.blueprints.site.terms.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g

from ....services.terms import version_service as terms_version_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated


blueprint = create_blueprint('terms', __name__)


@blueprint.route('/')
@templated
def view_current():
    """Show the current version of this brand's terms and conditions."""
    version = terms_version_service.find_current_version_for_brand(g.brand_id)

    if version is None:
        abort(404)

    return {
        'version': version,
    }
