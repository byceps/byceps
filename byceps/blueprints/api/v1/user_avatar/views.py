"""
byceps.blueprints.api.v1.user_avatar.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import redirect

from .....services.user_avatar import service as user_avatar_service
from .....services.user_avatar.models import FALLBACK_AVATAR_URL_PATH
from .....util.framework.blueprint import create_blueprint


blueprint = create_blueprint('api_v1_user_avatar', __name__)


@blueprint.route('/by_email_hash/<md5_hash>')
def get_avatar_url_by_email_address_hash(md5_hash):
    """Redirect to the avatar of the user with that hashed email address.

    This endpoint provides a Gravatar.com-like interface to obtain an
    avatar image for a email address. However, no parameters (size,
    etc.) are supported.
    """
    # No extra checks are done regarding user account states because:
    # - uninitialized accounts shouldn't have been able to upload
    #   avatars yet because they cannot login.
    # - suspended accounts should still have their avatars (if there was
    #   an issue with an avatar, it should have been removed manually in
    #   the first place).
    # - deleted accounts should have their avatar removed by the
    #   deletion process.

    avatar_url = user_avatar_service.get_avatar_url_for_md5_email_address_hash(
        md5_hash
    )

    if avatar_url is None:
        avatar_url = FALLBACK_AVATAR_URL_PATH

    return redirect(avatar_url)
