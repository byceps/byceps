"""
byceps.util.framework.blueprint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Blueprint utilities

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from importlib import import_module
from types import ModuleType

from flask import Blueprint


def create_blueprint(name: str, import_name: str) -> Blueprint:
    """Create a blueprint with default folder names."""
    return Blueprint(
        name, import_name, static_folder='static', template_folder='templates'
    )


def get_blueprint(name: str) -> Blueprint:
    """Load the blueprint from the named module.

    The module is expected to be located inside the ``blueprints``
    sub-package and to contain a blueprint instance named ``blueprint``.
    """
    module = _get_blueprint_views_module(name)
    return getattr(module, 'blueprint')


def _get_blueprint_views_module(name: str) -> ModuleType:
    """Import and return the 'views' module located in the specified
    blueprint package.
    """
    return import_module(f'byceps.blueprints.{name}.views')
