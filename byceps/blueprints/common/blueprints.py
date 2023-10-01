"""
byceps.application.blueprints.common.blueprints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask
import structlog

from byceps.util.framework.blueprint import register_blueprints


log = structlog.get_logger()


def register_common_blueprints(app: Flask) -> None:
    blueprints = [
        ('common.authn.password', '/authentication/password'),
        ('common.core', None),
        ('common.guest_server', None),
        ('common.locale', '/locale'),
        ('monitoring.healthcheck', '/health'),
    ]

    if app.config.get('STYLE_GUIDE_ENABLED', False):
        blueprints.append(('common.style_guide', '/style_guide'))
        log.info('Style guide: enabled')
    else:
        log.info('Style guide: disabled')

    register_blueprints(app, blueprints)
