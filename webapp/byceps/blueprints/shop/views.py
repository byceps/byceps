# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from flask import abort, g, request

from ...database import db
from ...util.framework import create_blueprint, flash_success
from ...util.templating import templated
from ...util.views import redirect_to

from .forms import OrderForm


blueprint = create_blueprint('shop', __name__)


@blueprint.route('/order')
@templated
def order_form(errorneous_form=None):
    """Show a form to order articles."""
    user = get_current_user_or_403()
    form = errorneous_form if errorneous_form else OrderForm(obj=user.detail)
    return {'form': form}


@blueprint.route('/order', methods=['POST'])
def order():
    """Order articles."""
    user = get_current_user_or_403()
    form = OrderForm(request.form)

    if not form.validate():
        return order_form(form)

    #order.first_names = form.first_names.data.strip()
    #order.last_name = form.last_name.data.strip()
    #order.date_of_birth = form.date_of_birth.data
    #order.zip_code = form.zip_code.data.strip()
    #order.city = form.city.data.strip()
    #order.street = form.street.data.strip()
    #db.session.commit()

    flash_success('Deine Bestellung wurde entgegen genommen.')
    return redirect_to('.order_form')


def get_current_user_or_403():
    user = g.current_user
    if not user.is_active:
        abort(403)

    return user
