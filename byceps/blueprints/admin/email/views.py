"""
byceps.blueprints.admin.email.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....services.email import service as email_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated

from ...common.authorization.decorators import permission_required
from ...common.authorization.registry import permission_registry

from .authorization import EmailConfigPermission


blueprint = create_blueprint('email_admin', __name__)


permission_registry.register_enum(EmailConfigPermission)


@blueprint.route('/')
@permission_required(EmailConfigPermission.view)
@templated
def index():
    """List all e-mail configs."""
    configs = email_service.get_all_configs()

    return {
        'configs': configs,
    }
