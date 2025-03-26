"""
byceps.services.api.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import g, request
from flask_babel import gettext

from byceps.services.authn.api import authn_api_service
from byceps.services.user import user_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import (
    permission_required,
    redirect_to,
    respond_no_content,
)

from .forms import CreateForm


blueprint = create_blueprint('api_admin', __name__)


@blueprint.get('')
@permission_required('api.administrate')
@templated
def index():
    """Show API access status and issued API tokens."""
    api_tokens = authn_api_service.get_all_api_tokens()

    user_ids = {api_token.creator_id for api_token in api_tokens}
    users_by_id = user_service.get_users_indexed_by_id(
        user_ids, include_avatars=True
    )

    return {
        'api_tokens': api_tokens,
        'users_by_id': users_by_id,
    }


@blueprint.get('/api_tokens/create')
@permission_required('api.administrate')
@templated
def create_api_token_form(erroneous_form=None):
    """Show form to create an API token."""
    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'form': form,
    }


@blueprint.post('/api_tokens')
@permission_required('api.administrate')
def create_api_token():
    """Create an API token."""
    form = CreateForm(request.form)

    if not form.validate():
        return create_api_token_form(form)

    creator_id = g.user.id
    permissions = set(form.permissions.data)
    description = form.description.data.strip()

    authn_api_service.create_api_token(
        creator_id, permissions, description=description
    )

    flash_success(gettext('API token has been created.'))

    return redirect_to('.index')


@blueprint.post('/api_tokens/<uuid:api_token_id>/suspend')
@permission_required('api.administrate')
@respond_no_content
def suspend_api_token(api_token_id):
    """Suspend the API token."""
    authn_api_service.suspend_api_token(api_token_id)

    flash_success(gettext('API token has been suspended.'))


@blueprint.post('/api_tokens/<uuid:api_token_id>/unsuspend')
@permission_required('api.administrate')
@respond_no_content
def unsuspend_api_token(api_token_id):
    """Unsuspend the API token."""
    authn_api_service.unsuspend_api_token(api_token_id)

    flash_success(gettext('API token has been unsuspended.'))


@blueprint.delete('/api_tokens/<uuid:api_token_id>')
@permission_required('api.administrate')
@respond_no_content
def delete_api_token(api_token_id):
    """Delete the API token."""
    authn_api_service.delete_api_token(api_token_id)

    flash_success(gettext('API token has been deleted.'))
