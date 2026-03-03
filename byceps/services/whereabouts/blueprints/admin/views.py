"""
byceps.services.whereabouts.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from datetime import datetime, timedelta

from flask import abort, g, request
from flask_babel import gettext

from byceps.services.party import party_service
from byceps.services.party.models import Party
from byceps.services.whereabouts import (
    signals as whereabouts_signals,
    whereabouts_client_service,
    whereabouts_service,
    whereabouts_sound_service,
)
from byceps.services.whereabouts.models import (
    WhereaboutsClient,
    WhereaboutsClientCandidate,
    WhereaboutsStatus,
)
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
from byceps.util.iterables import partition
from byceps.util.views import (
    permission_required,
    redirect_to,
    respond_no_content,
)

from .forms import ClientUpdateForm, UserSoundCreateForm, WhereaboutsCreateForm


blueprint = create_blueprint('whereabouts_admin', __name__)


STALE_THRESHOLD = timedelta(hours=12)


@blueprint.get('/for_party/<party_id>')
@permission_required('whereabouts.view')
@templated
def index(party_id):
    """Show orga whereabouts for party."""
    party = _get_party_or_404(party_id)

    whereabouts_list = whereabouts_service.get_whereabouts_list(party)

    statuses = whereabouts_service.get_statuses(party)

    now = datetime.utcnow()

    def _is_status_stale(status: WhereaboutsStatus) -> bool:
        return (now - STALE_THRESHOLD) > status.set_at

    stale_statuses, recent_statuses = partition(statuses, _is_status_stale)

    recent_statuses_by_whereabouts = defaultdict(list)
    for status in recent_statuses:
        recent_statuses_by_whereabouts[status.whereabouts_id].append(status)

    return {
        'party': party,
        'whereabouts_list': whereabouts_list,
        'recent_statuses_by_whereabouts': recent_statuses_by_whereabouts,
        'stale_statuses': stale_statuses,
    }


# -------------------------------------------------------------------- #
# whereabouts


@blueprint.get('/for_party/<party_id>/whereabouts')
@permission_required('whereabouts.view')
@templated
def whereabouts_index(party_id):
    """List whereabouts for party."""
    party = _get_party_or_404(party_id)

    whereabouts_list = whereabouts_service.get_whereabouts_list(party)

    return {
        'party': party,
        'whereabouts_list': whereabouts_list,
    }


@blueprint.get('/for_party/<party_id>/whereabouts/create')
@permission_required('whereabouts.administrate')
@templated
def whereabouts_create_form(party_id, erroneous_form=None):
    """Show form to add whereabouts."""
    party = _get_party_or_404(party_id)

    form = erroneous_form if erroneous_form else WhereaboutsCreateForm()

    return {
        'party': party,
        'form': form,
    }


@blueprint.post('/for_party/<party_id>/whereabouts')
@permission_required('whereabouts.administrate')
def whereabouts_create(party_id):
    """Add whereabouts."""
    party = _get_party_or_404(party_id)

    form = WhereaboutsCreateForm(request.form)
    if not form.validate():
        return whereabouts_create_form(form)

    name = form.name.data.strip()
    description = form.description.data.strip()
    hidden_if_empty = form.hidden_if_empty.data
    secret = form.secret.data

    whereabouts_service.create_whereabouts(
        party, name, description, hidden_if_empty=hidden_if_empty, secret=secret
    )

    flash_success(gettext('The object has been created.'))

    return redirect_to('.whereabouts_index', party_id=party.id)


# -------------------------------------------------------------------- #
# clients


@blueprint.get('/clients')
@permission_required('whereabouts.administrate')
@templated
def client_index():
    """List clients."""
    registration_open = whereabouts_client_service.is_registration_open()

    client_candidates = whereabouts_client_service.get_client_candidates()

    clients = whereabouts_client_service.get_clients()

    approved_clients, deleted_clients = partition(clients, lambda c: c.approved)

    return {
        'registration_open': registration_open,
        'client_candidates': client_candidates,
        'approved_clients': approved_clients,
        'deleted_clients': deleted_clients,
    }


@blueprint.get('/clients/<uuid:client_id>')
@permission_required('whereabouts.administrate')
@templated
def client_view(client_id):
    """Show single client."""
    client = _get_client_or_404(client_id)

    return {
        'client': client,
    }


@blueprint.post('/client_registration/open')
@permission_required('whereabouts.administrate')
@respond_no_content
def open_client_registration():
    """Open client registration."""
    whereabouts_client_service.open_registration()


@blueprint.post('/client_registration/close')
@permission_required('whereabouts.administrate')
@respond_no_content
def close_client_registration():
    """Close client registration."""
    whereabouts_client_service.close_registration()


@blueprint.post('/client_candidates/<uuid:candidate_id>/approve')
@permission_required('whereabouts.administrate')
@respond_no_content
def client_candidate_approve(candidate_id):
    """Approve a client candidate."""
    candidate = _get_client_candidate_or_404(candidate_id)
    initiator = g.user.as_user()

    _, event = whereabouts_client_service.approve_client(candidate, initiator)

    flash_success(gettext('Client candidate has been approved.'))

    whereabouts_signals.whereabouts_client_approved.send(None, event=event)


@blueprint.delete('/client_candidates/<uuid:candidate_id>')
@permission_required('whereabouts.administrate')
@respond_no_content
def client_candidate_delete(candidate_id):
    """Delete a client candidate."""
    candidate = _get_client_candidate_or_404(candidate_id)
    initiator = g.user.as_user()

    whereabouts_client_service.delete_client_candidate(candidate, initiator)

    flash_success(gettext('Client candidate has been deleted.'))


@blueprint.get('/client/<uuid:client_id>/update')
@permission_required('whereabouts.administrate')
@templated
def client_update_form(client_id, erroneous_form=None):
    """Show form to update a client."""
    client = _get_client_or_404(client_id)

    form = erroneous_form if erroneous_form else ClientUpdateForm(obj=client)

    return {
        'client': client,
        'form': form,
    }


@blueprint.post('/webhooks/<uuid:client_id>')
@permission_required('whereabouts.administrate')
def client_update(client_id):
    """Update the webhook."""
    client = _get_client_or_404(client_id)

    form = ClientUpdateForm(request.form)
    if not form.validate():
        return client_update_form(client.id, form)

    name = form.name.data.strip() or None
    location = form.location.data.strip() or None
    description = form.description.data.strip() or None

    whereabouts_client_service.update_client(
        client, name, location, description
    )

    flash_success(gettext('The object has been updated.'))

    return redirect_to('.client_index')


@blueprint.delete('/clients/<uuid:client_id>')
@permission_required('whereabouts.administrate')
@respond_no_content
def client_delete(client_id):
    """Delete a client."""
    client = _get_client_or_404(client_id)
    initiator = g.user.as_user()

    _, event = whereabouts_client_service.delete_client(client, initiator)

    flash_success(gettext('Client has been deleted.'))

    whereabouts_signals.whereabouts_client_deleted.send(None, event=event)


# -------------------------------------------------------------------- #
# user sounds


@blueprint.get('/user_sounds')
@permission_required('whereabouts.administrate')
@templated
def user_sound_index():
    """List user sounds."""
    user_sounds = whereabouts_sound_service.get_all_user_sounds()

    return {
        'user_sounds': user_sounds,
    }


@blueprint.get('/user_sounds/create')
@permission_required('whereabouts.administrate')
@templated
def user_sound_create_form(erroneous_form=None):
    """Show form to specify a sound for a user."""
    form = erroneous_form if erroneous_form else UserSoundCreateForm()

    return {
        'form': form,
    }


@blueprint.post('/user_sounds')
@permission_required('whereabouts.administrate')
def user_sound_create():
    """Specify a sound for a user."""
    form = UserSoundCreateForm(request.form)
    if not form.validate():
        return user_sound_create_form(form)

    user = form.user.data
    name = form.name.data.strip()

    whereabouts_sound_service.create_user_sound(user, name)

    flash_success(gettext('The object has been created.'))

    return redirect_to('.user_sound_index')


# -------------------------------------------------------------------- #
# helpers


def _get_party_or_404(party_id) -> Party:
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party


def _get_client_candidate_or_404(client_id) -> WhereaboutsClientCandidate:
    client_candidate = whereabouts_client_service.find_client_candidate(
        client_id
    )

    if client_candidate is None:
        abort(404)

    return client_candidate


def _get_client_or_404(client_id) -> WhereaboutsClient:
    client = whereabouts_client_service.find_client(client_id)

    if (client is None) or client.pending:
        abort(404)

    return client
