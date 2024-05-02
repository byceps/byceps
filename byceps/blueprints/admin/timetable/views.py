"""
byceps.blueprints.admin.timetable.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict

from flask import abort, g, request
from flask_babel import gettext

from byceps.services.party import party_service
from byceps.services.timetable import timetable_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import (
    permission_required,
    redirect_to,
    respond_no_content,
)

from .forms import CreateForm, UpdateForm


blueprint = create_blueprint('timetable_admin', __name__)


@blueprint.get('/for_party/<party_id>')
@permission_required('timetable.update')
@templated
def view(party_id):
    """Show timetable for party."""
    party = _get_party_or_404(party_id)

    timetable = timetable_service.find_timetable_for_party(party.id)

    if timetable:
        items_grouped_by_day = _group_items_by_day(timetable)
    else:
        items_grouped_by_day = []

    return {
        'party': party,
        'timetable': timetable,
        'items_grouped_by_day': items_grouped_by_day,
    }


def _group_items_by_day(timetable):
    items_grouped_by_day = defaultdict(list)

    for item in timetable.items:
        items_grouped_by_day[item.scheduled_at.date()].append(item)

    return dict(items_grouped_by_day)


@blueprint.post('/for_party/<party_id>')
@permission_required('timetable.administrate')
def create(party_id):
    """Create a timetable."""
    party = _get_party_or_404(party_id)

    timetable_service.create_timetable(party, hidden=True)

    flash_success(gettext('The object has been created.'))

    return redirect_to('.view', party_id=party_id)


@blueprint.get('/timetables/<uuid:timetable_id>/create')
@permission_required('timetable.update')
@templated
def item_create_form(timetable_id, erroneous_form=None):
    """Show form to create a timetable item."""
    timetable = _get_timetable_or_404(timetable_id)

    party = party_service.get_party(timetable.party_id)

    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'party': party,
        'timetable': timetable,
        'form': form,
    }


@blueprint.post('/timetables/<uuid:timetable_id>')
@permission_required('timetable.update')
def item_create(timetable_id):
    """Create a timetable item."""
    timetable = _get_timetable_or_404(timetable_id)

    form = CreateForm(request.form)
    if not form.validate():
        return item_create_form(form)

    scheduled_at = form.scheduled_at.data  # TODO: timezone conversion!!
    description = form.description.data.strip()
    location = form.location.data
    link_target = form.link_target.data
    link_label = form.link_label.data
    hidden = form.hidden.data

    timetable_service.create_item(
        timetable.id,
        scheduled_at,
        description,
        location,
        link_target,
        link_label,
        hidden,
    )

    flash_success(gettext('The object has been created.'))

    return redirect_to('.view', party_id=timetable.party_id)


@blueprint.get('/timetable_items/<uuid:item_id>/update')
@permission_required('timetable.update')
@templated
def item_update_form(item_id, erroneous_form=None):
    """Show form to update a timetable item."""
    item = _get_timetable_item_or_404(item_id)

    timetable = _get_timetable_or_404(item.timetable_id)

    party = party_service.get_party(timetable.party_id)

    form = erroneous_form if erroneous_form else UpdateForm(obj=item)

    return {
        'party': party,
        'item': item,
        'form': form,
    }


@blueprint.post('/timetable_items/<uuid:item_id>')
@permission_required('timetable.update')
def item_update(item_id):
    """Update a timetable item."""
    item = _get_timetable_item_or_404(item_id)

    timetable = _get_timetable_or_404(item.timetable_id)

    form = UpdateForm(request.form)
    if not form.validate():
        return item_update_form(item.id, form)

    scheduled_at = form.scheduled_at.data
    description = form.description.data.strip()
    location = form.location.data.strip()
    link_target = form.link_target.data.strip()
    link_label = form.link_label.data.strip()
    hidden = form.hidden.data

    timetable_service.update_item(
        item.id,
        scheduled_at,
        description,
        location,
        link_target,
        link_label,
        hidden,
    )

    flash_success(gettext('The object has been updated.'))

    return redirect_to('.view', party_id=timetable.party_id)


@blueprint.delete('/timetable_items/<uuid:item_id>')
@permission_required('timetable.update')
@respond_no_content
def item_delete(item_id):
    """Delete a timetable item."""
    item = _get_timetable_item_or_404(item_id)

    initiator = g.user

    timetable_service.delete_item(item.id, initiator)

    flash_success(gettext('The object has been deleted.'))


# -------------------------------------------------------------------- #


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party


def _get_timetable_or_404(timetable_id):
    timetable = timetable_service.find_timetable(timetable_id)

    if timetable is None:
        abort(404)

    return timetable


def _get_timetable_item_or_404(item_id):
    item = timetable_service.find_item(item_id)

    if item is None:
        abort(404)

    return item
