"""
byceps.application.blueprints.api.blueprints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.util.framework.blueprint import get_blueprint, register_blueprints


def register_api_blueprints(app: Flask) -> None:
    api_v1 = get_blueprint('blueprints.api.v1')

    blueprints = [
        ('blueprints.api.v1.authn', '/authentication'),
        ('blueprints.api.v1.attendance', '/attendances'),
        ('blueprints.api.v1.snippet', '/snippets'),
        ('blueprints.api.v1.tourney.avatar', '/tourney/avatars'),
        ('blueprints.api.v1.tourney.match.comments', '/tourney'),
        ('blueprints.api.v1.ticketing', '/ticketing'),
        ('blueprints.api.v1.user', '/users'),
        ('blueprints.api.v1.user_avatar', '/user_avatars'),
        ('blueprints.api.v1.user_badge', '/user_badges'),
    ]

    register_blueprints(api_v1, blueprints)

    app.register_blueprint(api_v1, url_prefix='/v1')
