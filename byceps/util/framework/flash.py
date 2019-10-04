"""
byceps.util.framework.flash
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Flash message utilities

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple

from flask import flash


FlashMessage = namedtuple('FlashMessage',
                          ['text', 'text_is_safe', 'category', 'icon'])


def flash_error(message, *args, icon=None, text_is_safe=False):
    """Flash a message indicating an error."""
    return _flash(
        message, *args, category='danger', icon=icon, text_is_safe=text_is_safe
    )


def flash_notice(message, *args, icon=None, text_is_safe=False):
    """Flash a generally informational message."""
    return _flash(
        message, *args, category='info', icon=icon, text_is_safe=text_is_safe
    )


def flash_success(message, *args, icon=None, text_is_safe=False):
    """Flash a message describing a successful action."""
    return _flash(
        message, *args, category='success', icon=icon, text_is_safe=text_is_safe
    )


def _flash(message, *args, category=None, icon=None, text_is_safe=False):
    text = message.format(*args)

    flash_message = FlashMessage(text, text_is_safe, category, icon)

    return flash(flash_message)
