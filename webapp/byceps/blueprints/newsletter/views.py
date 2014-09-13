# -*- coding: utf-8 -*-

"""
byceps.blueprints.newsletter.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from collections import namedtuple

from flask import g, request

from ...database import db
from ...util.framework import create_blueprint, flash_success
from ...util.templating import templated
from ...util.views import redirect_to

from .forms import SubscriptionForm
from .models import NewsletterSubscription, NewsletterSubscriptionState


blueprint = create_blueprint('newsletter', __name__)


@blueprint.route('/subscriptions/mine/update')
@templated
def subscription_update_form():
    """Show a form to update the current user's subscription."""
    user = get_current_user_or_404()
    state = NewsletterSubscription.get_state_for_user(user)

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

    state = NewsletterSubscriptionState[form.state.data]
    newsletter_subscription = NewsletterSubscription(user, state)
    db.session.add(newsletter_subscription)
    db.session.commit()

    flash_success('Dein Newsletter-Abonnement wurde aktualisiert.')
    return redirect_to('user.view_current')


def get_current_user_or_404():
    user = g.current_user
    if not user.is_active:
        abort(404)

    return user
