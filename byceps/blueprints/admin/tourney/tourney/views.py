"""
byceps.blueprints.admin.tourney.tourney.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses
from datetime import datetime

from flask import abort, request
from flask_babel import gettext

from .....permissions.tourney import TourneyPermission
from .....services.party import service as party_service
from .....services.tourney import tourney_service
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_success
from .....util.framework.templating import templated
from .....util.templatefilters import local_tz_to_utc, utc_to_local_tz
from .....util.views import permission_required, redirect_to

from .forms import CreateForm, UpdateForm


blueprint = create_blueprint('tourney_tourney_admin', __name__)


@blueprint.get('/for_party/<party_id>')
@permission_required(TourneyPermission.view)
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
@permission_required(TourneyPermission.administrate)
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
@permission_required(TourneyPermission.administrate)
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
    starts_at = local_tz_to_utc(
        datetime.combine(form.starts_on.data, form.starts_at.data)
    )

    tourney = tourney_service.create_tourney(
        party.id,
        title,
        category_id,
        max_participant_count,
        starts_at,
        subtitle=subtitle,
        logo_url=logo_url,
    )

    flash_success(
        gettext('Tourney "%(title)s" has been created.', title=tourney.title)
    )

    return redirect_to('.index', party_id=tourney.party_id)


@blueprint.get('/tourneys/<tourney_id>/update')
@permission_required(TourneyPermission.administrate)
@templated
def update_form(tourney_id, erroneous_form=None):
    """Show form to update the tourney."""
    tourney = _get_tourney_or_404(tourney_id)

    party = party_service.find_party(tourney.party_id)

    tourney = dataclasses.replace(
        tourney,
        starts_at=utc_to_local_tz(tourney.starts_at),
    )

    form = (
        erroneous_form
        if erroneous_form
        else UpdateForm(
            obj=tourney,
            starts_on=tourney.starts_at.date(),
            starts_at=tourney.starts_at.time(),
        )
    )
    form.set_category_choices(tourney.party_id)

    return {
        'party': party,
        'tourney': tourney,
        'form': form,
    }


@blueprint.post('/tourneys/<tourney_id>')
@permission_required(TourneyPermission.administrate)
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
    starts_at = local_tz_to_utc(
        datetime.combine(form.starts_on.data, form.starts_at.data)
    )

    tourney = tourney_service.update_tourney(
        tourney.id,
        title,
        subtitle,
        logo_url,
        category_id,
        max_participant_count,
        starts_at,
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
