"""
byceps.blueprints.site.user_group.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request
from flask_babel import gettext

from byceps.services.user_group import user_group_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import redirect_to

from .forms import CreateForm


blueprint = create_blueprint('user_group', __name__)


@blueprint.get('/')
@templated
def index():
    """List groups."""
    groups = user_group_service.get_all_groups()

    return {
        'groups': groups,
    }


@blueprint.get('/create')
@templated
def create_form(erroneous_form=None):
    """Show a form to create a group."""
    if g.party_id is None:
        abort(404)

    if not g.user.authenticated:
        flash_error(gettext('You have to be logged in to create a user group.'))
        return redirect_to('.index')

    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'form': form,
    }


@blueprint.post('/')
def create():
    """Create a group."""
    if g.party_id is None:
        abort(404)

    if not g.user.authenticated:
        flash_error(gettext('You have to be logged in to create a user group.'))
        return redirect_to('.index')

    form = CreateForm(request.form)
    if not form.validate():
        return create_form(form)

    creator = g.user
    title = form.title.data.strip()
    description = form.description.data.strip()

    group = user_group_service.create_group(
        g.party_id, creator, title, description
    )

    flash_success(
        gettext(
            'Group "%(group_title)s" has been created.',
            group_title=group.title,
        )
    )
    return redirect_to('.index')
