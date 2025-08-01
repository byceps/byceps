"""
byceps.services.user.avatar.blueprints.api.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import redirect

from byceps.services.user import user_service
from byceps.services.user.models.user import USER_FALLBACK_AVATAR_URL_PATH
from byceps.util.framework.blueprint import create_blueprint


blueprint = create_blueprint('user_avatar_api', __name__)


@blueprint.get('/by_email_hash/<md5_hash>')
def get_avatar_url_by_email_address_hash(md5_hash):
    """Redirect to the avatar of the user with that hashed email address.

    This endpoint provides a Gravatar.com-like interface to obtain an
    avatar image for a email address. However, no parameters (size,
    etc.) are supported.
    """
    # No extra checks are done regarding user account states because:
    # - uninitialized accounts shouldn't have been able to upload
    #   avatars yet because they cannot log in.
    # - suspended accounts should still have their avatars (if there was
    #   an issue with an avatar, it should have been removed manually in
    #   the first place).
    # - deleted accounts should have their avatar removed by the
    #   deletion process.

    user = user_service.find_user_by_email_address_md5_hash(md5_hash)

    avatar_url = user.avatar_url if user else None

    if avatar_url is None:
        avatar_url = USER_FALLBACK_AVATAR_URL_PATH

    return redirect(avatar_url)
