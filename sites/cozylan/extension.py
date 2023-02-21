"""
Site-specific code extension
"""

from typing import Any

from flask_babel import get_locale

from byceps.util.l10n import get_locales


def template_context_processor() -> dict[str, Any]:
    """Extend template context."""
    return {
        'current_locale': get_locale(),
        'locales': get_locales(),
    }
