"""
byceps.application.blueprints.api.blueprints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.util.framework.blueprint import get_blueprint


def register_api_blueprints(app: Flask) -> None:
    api_v1 = get_blueprint('api.v1')

    for name, url_prefix in [
        ('attendance', '/attendances'),
        ('snippet', '/snippets'),
        ('tourney.avatar', '/tourney/avatars'),
        ('tourney.match.comments', '/tourney'),
        ('ticketing', '/ticketing'),
        ('user', '/users'),
        ('user_avatar', '/user_avatars'),
        ('user_badge', '/user_badges'),
    ]:
        package = f'api.v1.{name}'
        blueprint = get_blueprint(package)
        api_v1.register_blueprint(blueprint, url_prefix=url_prefix)

    app.register_blueprint(api_v1, url_prefix='/v1')
