"""
byceps.application.blueprints.api
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Blueprint, Flask

from byceps.util.framework.blueprint import register_blueprints


def register_api_blueprints(app: Flask) -> None:
    api_v1 = Blueprint('v1', __name__)

    blueprints = [
        ('services.attendance.blueprints.api', '/attendances'),
        ('services.authn.api.blueprints.api', '/authentication'),
        ('services.snippet.blueprints.api', '/snippets'),
        ('services.ticketing.blueprints.api', '/ticketing'),
        ('services.tourney.avatar.blueprints.api', '/tourney/avatars'),
        ('services.tourney.match_comment.blueprints.api', '/tourney'),
        ('services.user.blueprints.api', '/users'),
        ('services.user.avatar.blueprints.api', '/user_avatars'),
        ('services.user_badge.blueprints.api', '/user_badges'),
    ]

    register_blueprints(api_v1, blueprints)

    app.register_blueprint(api_v1, url_prefix='/v1')
