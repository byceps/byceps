"""
byceps.blueprints.admin.api.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import current_app
from flask_babel import gettext

from ....services.authentication.api import service as api_service
from ....services.user import service as user_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.views import permission_required, respond_no_content


blueprint = create_blueprint('api_admin', __name__)


@blueprint.get('')
@permission_required('api.administrate')
@templated
def index():
    """Show API access status and issued API tokens."""
    api_enabled = current_app.config['API_ENABLED']
    api_tokens = api_service.get_all_api_tokens()

    user_ids = {api_token.creator_id for api_token in api_tokens}
    users = user_service.get_users(user_ids, include_avatars=True)
    users_by_id = user_service.index_users_by_id(users)

    return {
        'api_enabled': api_enabled,
        'api_tokens': api_tokens,
        'users_by_id': users_by_id,
    }


@blueprint.delete('/api_tokens/<uuid:api_token_id>')
@permission_required('api.administrate')
@respond_no_content
def delete_api_token(api_token_id):
    """Delete an API token."""
    api_service.delete_api_token(api_token_id)

    flash_success(gettext('API token has been deleted.'))
