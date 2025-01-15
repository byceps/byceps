"""
byceps.blueprints.admin.authn.identity_tag.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request
from flask_babel import gettext

from byceps.services.authn.identity_tag import authn_identity_tag_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import (
    permission_required,
    redirect_to,
    respond_no_content,
)

from .forms import CreateForm


blueprint = create_blueprint('authn_identity_tag_admin', __name__)


@blueprint.get('')
@permission_required('authn_identity_tag.view')
@templated
def index():
    """List tags."""
    search_term = request.args.get('search_term', default='').strip()

    tags = authn_identity_tag_service.get_all_tags()

    if search_term:
        tags = [tag for tag in tags if tag.identifier == search_term]

    return {
        'tags': tags,
        'search_term': search_term,
    }


@blueprint.get('/tags/create')
@permission_required('authn_identity_tag.administrate')
@templated
def create_form(erroneous_form=None):
    """Show form to add an identity tag."""
    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'form': form,
    }


@blueprint.post('/tags')
@permission_required('authn_identity_tag.administrate')
def create():
    """Add an identity tag."""
    form = CreateForm(request.form)
    if not form.validate():
        return create_form(form)

    creator = g.user
    identifier = form.identifier.data.strip()
    user = form.user.data
    note = form.note.data.strip() or None
    suspended = form.suspended.data

    authn_identity_tag_service.create_tag(
        creator, identifier, user, note=note, suspended=suspended
    )

    flash_success(gettext('The object has been created.'))

    return redirect_to('.index')


@blueprint.delete('/tags/<uuid:tag_id>')
@permission_required('authn_identity_tag.administrate')
@respond_no_content
def delete(tag_id):
    """Delete an identity tag."""
    tag = _get_tag_or_404(tag_id)
    initiator = g.user

    authn_identity_tag_service.delete_tag(tag, initiator)

    flash_success(gettext('The object has been deleted.'))


def _get_tag_or_404(tag_id):
    tag = authn_identity_tag_service.find_tag(tag_id)

    if tag is None:
        abort(404)

    return tag
