"""
byceps.blueprints.site.guest_server.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable

from flask import abort, g, redirect, request
from flask_babel import gettext

from byceps.services.global_setting import global_setting_service
from byceps.services.guest_server import guest_server_service
from byceps.services.guest_server.errors import (
    QuantityLimitReachedError,
    UserUsesNoTicketError,
)
from byceps.services.guest_server.models import Address
from byceps.services.party.models import Party
from byceps.services.user.models.user import User
from byceps.signals import guest_server as guest_server_signals
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_notice, flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import login_required, permission_required, redirect_to

from .forms import RegisterForm


blueprint = create_blueprint('guest_server', __name__)


@blueprint.get('')
@login_required
@templated
def index():
    """List current user's registered guest servers."""
    party = _get_current_party_or_404()

    servers = guest_server_service.get_servers_for_owner_and_party(
        g.user.id, party.id
    )

    setting = guest_server_service.get_setting_for_party(party.id)

    return {
        'servers': servers,
        'setting': setting,
        'sort_addresses': _sort_addresses,
    }


@blueprint.get('/create')
@login_required
@templated
def create_form(erroneous_form=None):
    """Show a form to register a guest server."""
    party = _get_current_party_or_404()

    if not may_user_register_server(party, g.user):
        return redirect_to('.index')

    setting = guest_server_service.get_setting_for_party(party.id)

    form = erroneous_form if erroneous_form else RegisterForm()

    return {
        'form': form,
        'domain': setting.domain,
    }


@blueprint.post('/create')
@login_required
def create():
    """Register a guest server."""
    party = _get_current_party_or_404()

    if not may_user_register_server(party, g.user):
        return redirect_to('.index')

    form = RegisterForm(request.form)
    if not form.validate():
        return create_form(form)

    hostname = form.hostname.data.strip().lower()
    description = form.description.data.strip()
    notes = form.notes.data.strip()

    server, event = guest_server_service.register_server(
        party,
        g.user,
        g.user,
        description=description,
        notes_owner=notes,
        hostname=hostname,
    )

    flash_success(gettext('The server has been registered.'))

    guest_server_signals.guest_server_registered.send(None, event=event)

    return redirect_to('.index')


@blueprint.get('/servers/<server_id>/admin')
@permission_required('guest_server.administrate')
def server_view(server_id):
    """Show guest server."""
    server = guest_server_service.find_server(server_id)
    if server is None:
        abort(404)

    admin_url_root = global_setting_service.find_setting_value('admin_url_root')
    if not admin_url_root:
        abort(500, 'Admin URL root not configured.')

    url = f'https://{admin_url_root}/admin/guest_servers/servers/{server.id}'
    return redirect(url)


def _get_current_party_or_404() -> Party:
    party = g.party

    if party is None:
        abort(404)

    return party


def may_user_register_server(party: Party, user: User) -> None:
    result = guest_server_service.ensure_user_may_register_server(party, user)

    if result.is_err():
        err = result.unwrap_err()
        if isinstance(err, UserUsesNoTicketError):
            flash_notice(
                gettext(
                    'Using a ticket for this party is required to register servers.'
                )
            )
            return False
        elif isinstance(err, QuantityLimitReachedError):
            flash_notice(
                gettext(
                    'You have already registered the maximum number of servers allowed.'
                )
            )
            return False
        else:
            flash_error(gettext('An unknown error has occurred.'))
            return False

    return True


def _sort_addresses(addresses: Iterable[Address]) -> list[Address]:
    """Sort addresses.

    By IP address first, hostname second. `None` at the end.
    """
    return list(
        sorted(
            addresses,
            key=lambda addr: (
                addr.ip_address is None,
                addr.ip_address,
                addr.hostname is None,
                addr.hostname,
            ),
        )
    )
