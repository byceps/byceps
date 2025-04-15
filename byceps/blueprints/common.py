"""
byceps.application.blueprints.common
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
        ('services.locale.blueprints.common', '/locale'),
        ('services.healthcheck.blueprints.common', '/health'),
    ]

    if style_guide_enabled:
        blueprints.append(('services.style_guide.blueprints.common', '/style_guide'))

    return blueprints
