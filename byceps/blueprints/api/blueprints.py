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
        ('authn', '/authentication'),
        ('attendance', '/attendances'),
        ('snippet', '/snippets'),
        ('tourney.avatar', '/tourney/avatars'),
        ('tourney.match.comments', '/tourney'),
        ('ticketing', '/ticketing'),
        ('user', '/users'),
        ('user_avatar', '/user_avatars'),
        ('user_badge', '/user_badges'),
    ]
    blueprints = [
        (f'blueprints.api.v1.{name}', url_prefix)
        for name, url_prefix in blueprints
    ]

    register_blueprints(api_v1, blueprints)

    app.register_blueprint(api_v1, url_prefix='/v1')
