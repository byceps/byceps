"""
byceps.application.blueprints.common.blueprints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.framework.blueprint import BlueprintReg


def get_common_blueprints(
    *, style_guide_enabled: bool = False
) -> list[BlueprintReg]:
    blueprints = [
        ('services.authn.password.blueprints.common', '/authentication/password'),
        ('services.core.blueprints.common', None),
        ('services.guest_server.blueprints.common', None),
        ('blueprints.common.locale', '/locale'),
        ('blueprints.monitoring.healthcheck', '/health'),
    ]

    if style_guide_enabled:
        blueprints.append(('blueprints.common.style_guide', '/style_guide'))

    return blueprints
