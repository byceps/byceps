# -*- coding: utf-8 -*-

from datetime import date

from byceps.blueprints.authorization.models import Permission, Role
from byceps.blueprints.shop_admin.authorization import ShopPermission
from byceps.blueprints.shop.models import Order, PaymentState
from byceps.blueprints.user.models import User

from testfixtures.user import create_user

from tests import AbstractAppTestCase


class ShopAdminTestCase(AbstractAppTestCase):

    def setUp(self):
        super(ShopAdminTestCase, self).setUp(env='test_admin')

        self.setUp_current_user()

    def setUp_current_user(self):
        update_orders_permission = Permission.from_enum_member(
            ShopPermission.update_orders)
        self.db.session.add(update_orders_permission)

        shop_admin_role = Role(id='shop_admin')
        self.db.session.add(shop_admin_role)

        shop_admin_role.permissions.append(update_orders_permission)

        self.current_user = self.create_user(99, enabled=True)
        self.current_user.roles.add(shop_admin_role)

        self.db.session.commit()

    def test_mark_order_as_canceled(self):
        user = self.create_user(1, enabled=True)
        order_before = self.create_order(user)
        self.db.session.commit()

        self.assertEqual(order_before.payment_state, PaymentState.open)
        self.assertIsNone(order_before.payment_state_updated_at)
        self.assertIsNone(order_before.payment_state_updated_by)

        url = '/admin/shop/orders/{}/mark_as_canceled'.format(order_before.id)
        with self.client.session_transaction() as session:
            session['user_id'] = str(self.current_user.id)
        response = self.client.post(url)

        order_afterwards = Order.query.get(order_before.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(order_afterwards.payment_state, PaymentState.canceled)
        self.assertIsNotNone(order_afterwards.payment_state_updated_at)
        self.assertEqual(order_afterwards.payment_state_updated_by, self.current_user)

    def test_mark_order_as_paid(self):
        user = self.create_user(1, enabled=True)
        order_before = self.create_order(user)
        self.db.session.commit()

        self.assertEqual(order_before.payment_state, PaymentState.open)
        self.assertIsNone(order_before.payment_state_updated_at)
        self.assertIsNone(order_before.payment_state_updated_by)

        url = '/admin/shop/orders/{}/mark_as_paid'.format(order_before.id)
        with self.client.session_transaction() as session:
            session['user_id'] = str(self.current_user.id)
        response = self.client.post(url)

        order_afterwards = Order.query.get(order_before.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(order_afterwards.payment_state, PaymentState.paid)
        self.assertIsNotNone(order_afterwards.payment_state_updated_at)
        self.assertEqual(order_afterwards.payment_state_updated_by, self.current_user)

    def create_user(self, number, *, enabled=True):
        user = create_user(number, enabled=enabled)
        self.db.session.add(user)
        return user

    def create_order(self, placed_by):
        order = Order(
            party=self.party,
            placed_by=placed_by,
            first_names='Hiro',
            last_name='Protagonist',
            date_of_birth=date(1970, 1, 1),
            zip_code='31337',
            city='Atrocity',
            street='L33t Street 101',
        )
        self.db.session.add(order)
        return order
