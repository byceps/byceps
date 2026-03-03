"""
byceps.util.templating
~~~~~~~~~~~~~~~~~~~~~~

Templating utilities

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pathlib import Path
from typing import Any

from jinja2 import (
    BaseLoader,
    Environment,
    FileSystemLoader,
    FunctionLoader,
    Template,
)
from jinja2.sandbox import ImmutableSandboxedEnvironment

from byceps.services.site.models import SiteID


SITES_PATH = Path('sites')


def load_template(
    source: str, *, template_globals: dict[str, Any] | None = None
) -> Template:
    """Load a template from source, using the sandboxed environment."""
    env = create_sandboxed_environment()

    if template_globals is not None:
        env.globals.update(template_globals)

    return env.from_string(source)


def create_sandboxed_environment(
    *, loader: BaseLoader | None = None, autoescape: bool = True
) -> Environment:
    """Create a sandboxed environment."""
    if loader is None:
        # A loader that never finds a template.
        loader = FunctionLoader(lambda name: None)

    return ImmutableSandboxedEnvironment(loader=loader, autoescape=autoescape)


def create_site_template_loader(site_id: SiteID) -> BaseLoader:
    search_path = SITES_PATH / site_id / 'template_overrides'
    return FileSystemLoader(search_path)
