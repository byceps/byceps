"""
byceps.application.blueprints.common.blueprints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.util.framework.blueprint import register_blueprints


def register_common_blueprints(
    app: Flask, *, style_guide_enabled: bool = False
) -> None:
    blueprints = [
        ('common.authn.password', '/authentication/password'),
        ('common.core', None),
        ('common.guest_server', None),
        ('common.locale', '/locale'),
        ('monitoring.healthcheck', '/health'),
    ]

    if style_guide_enabled:
        blueprints.append(('common.style_guide', '/style_guide'))

    register_blueprints(app, blueprints)
