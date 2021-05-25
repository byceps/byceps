"""
byceps.util.framework.blueprint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Blueprint utilities

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from importlib import import_module
from types import ModuleType
from typing import Union

from flask import Blueprint, Flask


def create_blueprint(name: str, import_name: str) -> Blueprint:
    """Create a blueprint with default folder names."""
    return Blueprint(
        name, import_name, static_folder='static', template_folder='templates'
    )


def register_blueprint(
    parent: Union[Blueprint, Flask], name: str, url_prefix: str
) -> None:
    """Register a blueprint with the application/blueprint as a parent.

    The module with the given name is expected to be located inside the
    'blueprints' sub-package and to contain a blueprint instance named
    'blueprint'.
    """
    module = _get_blueprint_views_module(name)
    blueprint = getattr(module, 'blueprint')
    parent.register_blueprint(blueprint, url_prefix=url_prefix)


def _get_blueprint_views_module(name: str) -> ModuleType:
    """Import and return the 'views' module located in the specified
    blueprint package.
    """
    return import_module(f'byceps.blueprints.{name}.views')
