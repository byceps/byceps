"""
byceps.blueprints.api.v1.zammad.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jan Korneffel, Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from flask import jsonify, request
from sqlalchemy import select

from byceps.blueprints.api.decorators import api_token_required
from byceps.database import db
from byceps.services.user.dbmodels.user import DbUser
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.views import create_empty_json_response


blueprint = create_blueprint('zammad', __name__)


@blueprint.get('/user_search')
@api_token_required
def search_user():
    """Return information about the user with the given email address."""
    email_address = request.args.get('email_address')
    if not email_address:
        return create_empty_json_response(400)

    user = _find_user(email_address)
    if user is None:
        return create_empty_json_response(404)

    avatar_url = _get_avatar_url(user)

    return jsonify(
        id=user.id,
        screen_name=user.screen_name,
        email_address=user.email_address,
        first_name=user.detail.first_name,
        last_name=user.detail.last_name,
        zip_code=user.detail.zip_code,
        city=user.detail.city,
        street=user.detail.street,
        country=user.detail.country,
        phone_number=user.detail.phone_number,
        internal_comment=user.detail.internal_comment,
        avatar_url=avatar_url,
    )


def _find_user(email_address: str) -> DbUser | None:
    return (
        db.session.scalars(
            select(DbUser)
            .options(
                db.joinedload(DbUser.detail),
                db.joinedload(DbUser.avatar),
            )
            .filter(
                db.func.lower(DbUser.email_address) == email_address.lower()
            )
        )
        .unique()
        .one_or_none()
    )


def _get_avatar_url(user: DbUser) -> str | None:
    if user.avatar is None:
        return None

    return request.host_url.rstrip('/') + user.avatar.url
