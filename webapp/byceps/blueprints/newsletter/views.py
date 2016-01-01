# -*- coding: utf-8 -*-

"""
byceps.blueprints.newsletter.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple

from flask import abort, g, request

from ...database import db
from ...util.framework import create_blueprint, flash_success
from ...util.templating import templated
from ...util.views import redirect_to

from .forms import SubscriptionForm
from .models import Subscription, SubscriptionState


blueprint = create_blueprint('newsletter', __name__)


@blueprint.route('/subscriptions/mine/update')
@templated
def subscription_update_form():
    """Show a form to update the current user's subscription."""
    user = get_current_user_or_404()
    state = Subscription.get_state_for_user(user)

    obj = namedtuple('Obj', 'state')(state.name)
    form = SubscriptionForm(obj=obj)

    return {
        'form': form,
    }


@blueprint.route('/subscriptions/mine', methods=['POST'])
def subscription_update():
    """Update the current user's subscription."""
    user = get_current_user_or_404()
    form = SubscriptionForm(request.form)

    state = SubscriptionState[form.state.data]
    subscription = Subscription(user, state)
    db.session.add(subscription)
    db.session.commit()

    flash_success('Dein Newsletter-Abonnement wurde aktualisiert.')
    return redirect_to('user.view_current')


def get_current_user_or_404():
    user = g.current_user
    if not user.is_active:
        abort(404)

    return user
