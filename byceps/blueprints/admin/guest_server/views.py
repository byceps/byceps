"""
byceps.blueprints.admin.guest_server.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort
from flask_babel import gettext

from ....services.guest_server import service as guest_server_service
from ....services.party import service as party_service
from ....services.user import service as user_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.views import permission_required, respond_no_content


blueprint = create_blueprint('guest_server_admin', __name__)


@blueprint.get('/for_party/<party_id>')
@permission_required('guest_server.administrate')
@templated
def index(party_id):
    """Show guest servers for a party."""
    party = party_service.find_party(party_id)
    if party is None:
        abort(404)

    servers = guest_server_service.get_all_servers_for_party(party_id)

    creator_ids = {server.creator_id for server in servers}
    owner_ids = {server.owner_id for server in servers}
    user_ids = creator_ids.union(owner_ids)
    users = user_service.get_users(user_ids, include_avatars=True)
    users_by_id = user_service.index_users_by_id(users)

    return {
        'party': party,
        'servers': servers,
        'users_by_id': users_by_id,
    }


@blueprint.delete('/guest_servers/<uuid:server_id>')
@permission_required('guest_server.administrate')
@respond_no_content
def delete_server(server_id):
    """Delete a guest server."""
    guest_server_service.delete_server(server_id)

    flash_success(gettext('Server has been deleted.'))
