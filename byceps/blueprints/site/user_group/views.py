"""
byceps.blueprints.site.user_group.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request
from flask_babel import gettext

from byceps.services.user_group import user_group_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import login_required, redirect_to

from .forms import CreateForm


blueprint = create_blueprint('user_group', __name__)


@blueprint.get('/')
@templated
def index():
    """List groups."""
    if g.party_id is None:
        abort(404)

    groups = user_group_service.get_groups_for_party(g.party_id)

    return {
        'groups': groups,
    }


@blueprint.get('/<uuid:group_id>')
@templated
def view(group_id):
    """Show group."""
    if g.party_id is None:
        abort(404)

    group = user_group_service.find_group(group_id)
    if (group is None) or (group.party_id != g.party_id):
        abort(404)

    return {
        'group': group,
    }


@blueprint.get('/create')
@login_required
@templated
def create_form(erroneous_form=None):
    """Show a form to create a group."""
    if g.party_id is None:
        abort(404)

    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'form': form,
    }


@blueprint.post('/')
@login_required
def create():
    """Create a group."""
    if g.party_id is None:
        abort(404)

    form = CreateForm(request.form)
    if not form.validate():
        return create_form(form)

    creator = g.user
    title = form.title.data.strip()
    description = form.description.data.strip()

    group = user_group_service.create_group(
        g.party, creator, title, description
    )

    flash_success(
        gettext(
            'Group "%(group_title)s" has been created.',
            group_title=group.title,
        )
    )
    return redirect_to('.view', group_id=group.id)
