"""
byceps.blueprints.site.user.avatar.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request
from flask_babel import gettext

from byceps.services.image import image_service
from byceps.services.user import user_avatar_service
from byceps.signals import user as user_signals
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_notice, flash_success
from byceps.util.framework.templating import templated
from byceps.util.image.models import ImageType
from byceps.util.views import redirect_to, respond_no_content

from .forms import UpdateForm


blueprint = create_blueprint('user_avatar', __name__)


ALLOWED_IMAGE_TYPES = frozenset(
    [
        ImageType.jpeg,
        ImageType.png,
        ImageType.webp,
    ]
)


@blueprint.get('/me/avatar/update')
@templated
def update_form(erroneous_form=None):
    """Show a form to update the current user's avatar image."""
    _get_current_user_or_404()

    form = erroneous_form if erroneous_form else UpdateForm()

    image_type_names = image_service.get_image_type_names(ALLOWED_IMAGE_TYPES)

    return {
        'form': form,
        'allowed_types': image_type_names,
        'maximum_dimensions': user_avatar_service.MAXIMUM_DIMENSIONS,
    }


@blueprint.post('/me/avatar')
def update():
    """Update the current user's avatar image."""
    user = _get_current_user_or_404()

    # Make `InputRequired` work on `FileField`.
    form_fields = request.form.copy()
    if request.files:
        form_fields.update(request.files)

    form = UpdateForm(form_fields)

    if not form.validate():
        return update_form(form)

    image = request.files.get('image')

    _update(user, image)

    flash_success(gettext('Avatar image has been updated.'), icon='upload')
    user_signals.avatar_updated.send(None, user_id=user.id)

    return redirect_to('user_settings.view')


def _update(user, image):
    if not image or not image.filename:
        abort(400, 'No file to upload has been specified.')

    try:
        update_result = user_avatar_service.update_avatar_image(
            user.id, image.stream, ALLOWED_IMAGE_TYPES, user
        )
        if update_result.is_err():
            abort(400, update_result.unwrap_err())
    except FileExistsError:
        abort(409, 'File already exists, not overwriting.')


@blueprint.delete('/me/avatar')
@respond_no_content
def delete():
    """Remove the current user's avatar image."""
    user = _get_current_user_or_404()

    try:
        user_avatar_service.remove_avatar_image(user.id, user)
    except ValueError:
        # No avatar selected.
        # But that's ok, deletions should be idempotent.
        flash_notice(gettext('No avatar image is set that could be removed.'))
    else:
        flash_success(gettext('Avatar image has been removed.'))


def _get_current_user_or_404():
    user = g.user

    if not user.authenticated:
        abort(404)

    return user
