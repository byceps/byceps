"""
byceps.services.tourney.tourney.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses

from flask import abort, g, request
from flask_babel import gettext, to_user_timezone, to_utc

from byceps.services.party import party_service
from byceps.services.tourney import tourney_category_service, tourney_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import permission_required, redirect_to

from .forms import CreateForm, UpdateForm


blueprint = create_blueprint('tourney_tourney_admin', __name__)


@blueprint.get('/for_party/<party_id>')
@permission_required('tourney.view')
@templated
def index(party_id):
    """List tourneys for that party."""
    party = _get_party_or_404(party_id)

    tourneys = tourney_service.get_tourneys_for_party(party.id)

    return {
        'party': party,
        'tourneys': tourneys,
    }


@blueprint.get('/for_party/<party_id>/create')
@permission_required('tourney.administrate')
@templated
def create_form(party_id, erroneous_form=None):
    """Show form to create a tourney."""
    party = _get_party_or_404(party_id)

    form = erroneous_form if erroneous_form else CreateForm()
    form.set_category_choices(party.id)

    return {
        'party': party,
        'form': form,
    }


@blueprint.post('/for_party/<party_id>')
@permission_required('tourney.administrate')
def create(party_id):
    """Create a tourney."""
    party = _get_party_or_404(party_id)

    form = CreateForm(request.form)
    form.set_category_choices(party.id)

    if not form.validate():
        return create_form(party.id, form)

    title = form.title.data.strip()
    subtitle = form.subtitle.data.strip()
    logo_url = form.logo_url.data.strip()
    category_id = form.category_id.data
    max_participant_count = form.max_participant_count.data
    starts_at_local = form.starts_at.data
    starts_at_utc = to_utc(starts_at_local)

    creator = g.user
    category = tourney_category_service.get_category(category_id)

    tourney, event = tourney_service.create_tourney(
        party,
        creator,
        title,
        category,
        max_participant_count,
        starts_at_utc,
        subtitle=subtitle,
        logo_url=logo_url,
    )

    flash_success(
        gettext('Tourney "%(title)s" has been created.', title=tourney.title)
    )

    return redirect_to('.index', party_id=tourney.party_id)


@blueprint.get('/tourneys/<tourney_id>/update')
@permission_required('tourney.administrate')
@templated
def update_form(tourney_id, erroneous_form=None):
    """Show form to update the tourney."""
    tourney = _get_tourney_or_404(tourney_id)

    party = party_service.find_party(tourney.party_id)

    data = dataclasses.asdict(tourney)
    starts_at_local = to_user_timezone(tourney.starts_at)
    data['starts_at'] = starts_at_local

    form = erroneous_form if erroneous_form else UpdateForm(data=data)
    form.set_category_choices(tourney.party_id)

    return {
        'party': party,
        'tourney': tourney,
        'form': form,
    }


@blueprint.post('/tourneys/<tourney_id>')
@permission_required('tourney.administrate')
def update(tourney_id):
    """Update the tourney."""
    tourney = _get_tourney_or_404(tourney_id)

    form = UpdateForm(request.form)
    form.set_category_choices(tourney.party_id)

    if not form.validate():
        return update_form(tourney.id, form)

    title = form.title.data.strip()
    subtitle = form.subtitle.data.strip()
    logo_url = form.logo_url.data.strip()
    category_id = form.category_id.data
    max_participant_count = form.max_participant_count.data
    starts_at_local = form.starts_at.data
    starts_at_utc = to_utc(starts_at_local)
    registration_open = form.registration_open.data

    tourney = tourney_service.update_tourney(
        tourney.id,
        title,
        subtitle,
        logo_url,
        category_id,
        max_participant_count,
        starts_at_utc,
        registration_open,
    )

    flash_success(
        gettext('Tourney "%(title)s" has been updated.', title=tourney.title)
    )

    return redirect_to('.index', party_id=tourney.party_id)


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party


def _get_tourney_or_404(tourney_id):
    tourney = tourney_service.find_tourney(tourney_id)

    if tourney is None:
        abort(404)

    return tourney
