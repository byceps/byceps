# -*- coding: utf-8 -*-

"""
byceps.blueprints.user_avatar.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g, request, url_for

from ...util.framework import create_blueprint, flash_success
from ...util.image import ImageType
from ...util.templating import templated
from ...util.views import redirect_to, respond_no_content_with_location

from .forms import UpdateForm
from . import service
from . import signals


blueprint = create_blueprint('user_avatar', __name__)


ALLOWED_IMAGE_TYPES = frozenset([
    ImageType.gif,
    ImageType.jpeg,
    ImageType.png,
])


@blueprint.route('/me/avatar/update')
@templated
def update_form(erroneous_form=None):
    """Show a form to update the current user's avatar image."""
    get_current_user_or_404()

    form = erroneous_form if erroneous_form else UpdateForm()

    image_type_names = service.get_image_type_names(ALLOWED_IMAGE_TYPES)

    return {
        'form': form,
        'allowed_types': image_type_names,
        'maximum_dimensions': service.MAXIMUM_DIMENSIONS,
    }


@blueprint.route('/me/avatar', methods=['POST'])
def update():
    """Update the current user's avatar image."""
    user = get_current_user_or_404()

    # Make `InputRequired` work on `FileField`.
    form_fields = request.form.copy()
    if request.files:
        form_fields.update(request.files)

    form = UpdateForm(form_fields)

    if not form.validate():
        return update_form(form)

    image = request.files.get('image')
    if not image or not image.filename:
        abort(400, 'No file to upload has been specified.')

    try:
        service.update_avatar_image(user, image.stream,
                                    allowed_types=ALLOWED_IMAGE_TYPES)
    except FileExistsError:
        abort(409, 'File already exists, not overwriting.')

    flash_success('Das Avatarbild wurde aktualisiert.', icon='upload')
    signals.avatar_updated.send(None, user=user)

    return redirect_to('user.view_current')


@blueprint.route('/me/avatar', methods=['DELETE'])
@respond_no_content_with_location
def delete():
    """Remove the current user's avatar image."""
    user = get_current_user_or_404()

    service.remove_avatar_image(user)

    flash_success('Das Avatarbild wurde entfernt.')
    return url_for('user.view_current')


def get_current_user_or_404():
    user = g.current_user
    if not user.is_active:
        abort(404)

    return user
