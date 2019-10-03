"""
byceps.util.templating
~~~~~~~~~~~~~~~~~~~~~~

Templating utilities

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Any, Dict, Optional

from jinja2 import BaseLoader, Environment, FunctionLoader, Template
from jinja2.sandbox import ImmutableSandboxedEnvironment


def load_template(source: str, *, template_globals: Dict[str, Any] = None):
    """Load a template from source, using the sandboxed environment."""
    env = create_sandboxed_environment()

    if template_globals is not None:
        env.globals.update(template_globals)

    return env.from_string(source)


def create_sandboxed_environment(
    *, loader: Optional[BaseLoader] = None, autoescape: bool = True
) -> Environment:
    """Create a sandboxed environment."""
    if loader is None:
        # A loader that never finds a template.
        loader = FunctionLoader(lambda name: None)

    return ImmutableSandboxedEnvironment(
        loader=loader,
        autoescape=autoescape)


def get_variable_value(template: Template, name: str) -> Optional[Any]:
    """Return the named variable's value from the template, or `None` if
    the variable is not defined.
    """
    try:
        return getattr(template.module, name)
    except AttributeError:
        return None
