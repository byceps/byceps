"""
byceps.util.framework.flash
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Flash message utilities

A custom wrapper, `FlashMessage`, is used to bundle additional properties
with a text message.

`FlashMessage` objects are then returned by `get_flashed_messages()` and
handled accordingly in the `_notifications` partial template.

Thus, use the `flash_*` functions provided by this module to flash
messages, but not `flask.flash` directly.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from flask import flash


@dataclass(frozen=True)
class FlashMessage:
    text: str
    text_is_safe: bool
    category: str | None
    icon: str | None


def flash_error(
    message: str, icon: str | None = None, text_is_safe: bool = False
) -> None:
    """Flash a message indicating an error."""
    _flash(message, category='danger', icon=icon, text_is_safe=text_is_safe)


def flash_notice(
    message: str, icon: str | None = None, text_is_safe: bool = False
) -> None:
    """Flash a generally informational message."""
    _flash(message, category='info', icon=icon, text_is_safe=text_is_safe)


def flash_success(
    message: str, icon: str | None = None, text_is_safe: bool = False
) -> None:
    """Flash a message describing a successful action."""
    _flash(message, category='success', icon=icon, text_is_safe=text_is_safe)


def _flash(
    message: str,
    category: str | None = None,
    icon: str | None = None,
    text_is_safe: bool = False,
) -> None:
    flash_message = FlashMessage(message, text_is_safe, category, icon)
    flash(flash_message)
