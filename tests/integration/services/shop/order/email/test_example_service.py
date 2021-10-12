"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.shop.order.email import example_service

from tests.helpers import current_user_set

from .helpers import get_current_user_for_user


def test_example_placed_order_message_text(
    admin_app,
    order_admin,
    shop,
    email_payment_instructions_snippet_id,
    email_footer_snippet_id,
):
    app = admin_app
    current_user = get_current_user_for_user(order_admin)

    with current_user_set(app, current_user), app.app_context():
        actual = example_service.build_example_placed_order_message_text(
            shop.id, 'de'
        )

    assert (
        actual
        == '''\
From: NameAndAddress(name=None, address='noreply@acmecon.test')
To: ['besteller@example.com']
Subject: Deine Bestellung (AWSM-ORDR-9247) ist eingegangen.


Hallo Besteller,

vielen Dank für deine Bestellung mit der Nummer AWSM-ORDR-9247 am 12.10.2021 über unsere Website.

Folgende Artikel hast du bestellt:

  Gesamtbetrag: 42,95 €

Bitte überweise den Gesamtbetrag auf folgendes Konto:

  Zahlungsempfänger: <Name>
  IBAN: <IBAN>
  BIC: <BIC>
  Bank: <Kreditinstitut>
  Verwendungszweck: AWSM-ORDR-9247

Wir werden dich informieren, sobald wir deine Zahlung erhalten haben.

Hier kannst du deine Bestellungen einsehen: https://www.acmecon.test/shop/orders

Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: noreply@acmecon.test
'''
    )


def test_example_paid_order_message_text(
    admin_app,
    order_admin,
    shop,
    email_payment_instructions_snippet_id,
    email_footer_snippet_id,
):
    app = admin_app
    current_user = get_current_user_for_user(order_admin)

    with current_user_set(app, current_user), app.app_context():
        actual = example_service.build_example_paid_order_message_text(
            shop.id, 'de'
        )

    assert (
        actual
        == '''\
From: NameAndAddress(name=None, address='noreply@acmecon.test')
To: ['besteller@example.com']
Subject: ✅ Deine Bestellung (AWSM-ORDR-9247) ist bezahlt worden.


Hallo Besteller,

vielen Dank für deine Bestellung mit der Nummer AWSM-ORDR-9247 am 12.10.2021 über unsere Website.

Wir haben deine Zahlung erhalten und deine Bestellung als bezahlt markiert.

Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: noreply@acmecon.test
'''
    )


def test_example_canceled_order_message_text(
    admin_app,
    order_admin,
    shop,
    email_payment_instructions_snippet_id,
    email_footer_snippet_id,
):
    app = admin_app
    current_user = get_current_user_for_user(order_admin)

    with current_user_set(app, current_user), app.app_context():
        actual = example_service.build_example_canceled_order_message_text(
            shop.id, 'de'
        )

    assert (
        actual
        == '''\
From: NameAndAddress(name=None, address='noreply@acmecon.test')
To: ['besteller@example.com']
Subject: ❌ Deine Bestellung (AWSM-ORDR-9247) ist storniert worden.


Hallo Besteller,

deine Bestellung mit der Nummer AWSM-ORDR-9247 vom 12.10.2021 wurde von uns aus folgendem Grund storniert:

Kein fristgerechter Geldeingang feststellbar.

Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: noreply@acmecon.test
'''
    )
