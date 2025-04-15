"""
byceps.services.tourney.avatar.blueprints.api.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request

from byceps.services.party import party_service
from byceps.services.tourney.avatar import tourney_avatar_service
from byceps.services.user import user_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.image.image_type import ImageType
from byceps.util.views import (
    api_token_required,
    respond_created,
    respond_no_content,
)

from .forms import CreateForm


blueprint = create_blueprint('tourney_avatar_api', __name__)


ALLOWED_IMAGE_TYPES = frozenset(
    [
        ImageType.jpeg,
        ImageType.png,
        ImageType.webp,
    ]
)


@blueprint.post('')
@api_token_required
@respond_created
def create():
    """Create an avatar image."""
    # Make `InputRequired` work on `FileField`.
    form_fields = request.form.copy()
    if request.files:
        form_fields.update(request.files)

    form = CreateForm(form_fields)

    if not form.validate():
        abort(400, 'Form validation failed.')

    party_id = form.party_id.data
    creator_id = form.creator_id.data
    image = request.files.get('image')

    party = party_service.find_party(party_id)
    if not party:
        abort(400, 'Unknown party ID')

    avatar = _create(party.id, creator_id, image)

    return avatar.url_path


def _create(party_id, creator_id, image):
    creator = user_service.find_active_user(creator_id)
    if creator is None:
        abort(400, 'Invalid creator ID')

    if not image or not image.filename:
        abort(400, 'No file to upload has been specified.')

    try:
        creation_result = tourney_avatar_service.create_avatar_image(
            party_id, creator, image.stream, ALLOWED_IMAGE_TYPES
        )
        if creation_result.is_err():
            abort(400, creation_result.unwrap_err())

        return creation_result.unwrap()
    except FileExistsError:
        abort(409, 'File already exists, not overwriting.')


@blueprint.delete('/<uuid:avatar_id>')
@api_token_required
@respond_no_content
def delete(avatar_id):
    """Delete the avatar image."""
    result = tourney_avatar_service.delete_avatar_image(avatar_id)

    if result.is_err():
        abort(404, result.unwrap_err())
