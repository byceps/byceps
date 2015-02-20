# -*- coding: utf-8 -*-

"""
byceps.blueprints.user_group.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from flask import g, request

from ...database import db
from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.templating import templated
from ...util.views import redirect_to

from .forms import CreateForm
from .models import UserGroup


blueprint = create_blueprint('user_group', __name__)


@blueprint.route('/')
@templated
def index():
    """List groups."""
    groups = UserGroup.query.all()
    return {'groups': groups}


@blueprint.route('/create')
@templated
def create_form(erroneous_form=None):
    """Show a form to create a group."""
    if not g.current_user.is_active:
        flash_error(
            'Du musst angemeldet sein um eine Benutzergruppe erstellen zu können.')
        return redirect_to('.index')

    form = erroneous_form if erroneous_form else CreateForm()
    return {'form': form}


@blueprint.route('/', methods=['POST'])
def create():
    """Create a group."""
    if not g.current_user.is_active:
        flash_error(
            'Du musst angemeldet sein um eine Benutzergruppe erstellen zu können.')
        return redirect_to('.index')

    form = CreateForm(request.form)

    creator = g.current_user
    title = form.title.data.strip()
    description = form.description.data.strip()

    group = UserGroup(creator, title, description)
    db.session.add(group)
    db.session.commit()

    flash_success('Die Gruppe "{}" wurde erstellt.', group.title)
    return redirect_to('.index')
