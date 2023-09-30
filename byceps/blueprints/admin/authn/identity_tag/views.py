"""
byceps.blueprints.admin.authn.identity_tag.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.authn.identity_tag import authn_identity_tag_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated
from byceps.util.views import permission_required


blueprint = create_blueprint('authn_identity_tag_admin', __name__)


@blueprint.get('')
@permission_required('authn_identity_tag.view')
@templated
def index():
    """List tags."""
    tags = authn_identity_tag_service.get_all_tags()

    return {'tags': tags}
