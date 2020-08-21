"""
byceps.blueprints.site.user_group.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import g, request

from ....services.user_group import service as user_group_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_success
from ....util.framework.templating import templated
from ....util.views import redirect_to

from .forms import CreateForm


blueprint = create_blueprint('user_group', __name__)


@blueprint.route('/')
@templated
def index():
    """List groups."""
    groups = user_group_service.get_all_groups()

    return {
        'groups': groups,
    }


@blueprint.route('/create')
@templated
def create_form(erroneous_form=None):
    """Show a form to create a group."""
    if not g.current_user.is_active:
        flash_error(
            'Du musst angemeldet sein, um eine Benutzergruppe erstellen zu können.'
        )
        return redirect_to('.index')

    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'form': form,
    }


@blueprint.route('/', methods=['POST'])
def create():
    """Create a group."""
    if not g.current_user.is_active:
        flash_error(
            'Du musst angemeldet sein, um eine Benutzergruppe erstellen zu können.'
        )
        return redirect_to('.index')

    form = CreateForm(request.form)

    creator = g.current_user
    title = form.title.data.strip()
    description = form.description.data.strip()

    group = user_group_service.create_group(creator.id, title, description)

    flash_success(f'Die Gruppe "{group.title}" wurde erstellt.')
    return redirect_to('.index')
