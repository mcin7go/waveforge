import pytest
import stripe
from flask import url_for
from app.models import Plan, User

# === Testy Serwisu Płatności ===

def test_get_or_create_customer_new(test_user, mocker):
    mock_create = mocker.patch('stripe.Customer.create', return_value=mocker.Mock(id='cus_new123'))
    from app.services import payment_service
    customer = payment_service.get_or_create_customer(test_user)
    assert customer.id == 'cus_new123'
    assert test_user.stripe_customer_id == 'cus_new123'

def test_get_or_create_customer_existing(user_with_stripe_id, mocker):
    mock_retrieve = mocker.patch('stripe.Customer.retrieve')
    mock_create = mocker.patch('stripe.Customer.create')
    from app.services import payment_service
    payment_service.get_or_create_customer(user_with_stripe_id)
    mock_retrieve.assert_called_once_with(user_with_stripe_id.stripe_customer_id)
    mock_create.assert_not_called()

def test_get_or_create_customer_stale_id(user_with_stripe_id, mocker):
    mocker.patch('stripe.Customer.retrieve', side_effect=stripe.error.InvalidRequestError('No such customer', 'id'))
    mock_create = mocker.patch('stripe.Customer.create', return_value=mocker.Mock(id='cus_new456'))
    from app.services import payment_service
    payment_service.get_or_create_customer(user_with_stripe_id)
    mock_create.assert_called_once()
    assert user_with_stripe_id.stripe_customer_id == 'cus_new456'

def test_create_subscription_success(user_with_stripe_id, mocker):
    mock_attach = mocker.patch('stripe.PaymentMethod.attach')
    mock_modify = mocker.patch('stripe.Customer.modify')
    mock_create = mocker.patch('stripe.Subscription.create')
    from app.services import payment_service
    payment_service.create_subscription('cus_test123', 'pm_123', 'price_123')
    mock_attach.assert_called_once_with('pm_123', customer='cus_test123')
    mock_modify.assert_called_once_with('cus_test123', invoice_settings={'default_payment_method': 'pm_123'})
    mock_create.assert_called_once()

def test_create_subscription_card_error(user_with_stripe_id, mocker):
    mocker.patch('stripe.PaymentMethod.attach', side_effect=stripe.error.CardError('msg', 'param', 'code'))
    from app.services import payment_service
    with pytest.raises(stripe.error.CardError):
        payment_service.create_subscription('cus_id', 'pm_id', 'price_id')

# === Testy Endpointów ===

def test_admin_panel_allows_admin(logged_in_admin_client):
    assert logged_in_admin_client.get(url_for('admin.manage_plans')).status_code == 200

def test_create_plan_success(logged_in_admin_client, db, mocker):
    mocker.patch('stripe.Product.create', return_value=mocker.Mock(id='prod_test'))
    mocker.patch('stripe.Price.create', return_value=mocker.Mock(id='price_test'))
    logged_in_admin_client.post(url_for('admin.manage_plans'), data={'name': 'Test Plan', 'price': '99.99', 'currency': 'pln', 'interval': 'month'})
    assert Plan.query.filter_by(stripe_product_id='prod_test').one_or_none() is not None

def test_webhook_updates_status(client, db, user_with_stripe_id, mocker):
    event_payload = {'type': 'invoice.payment_succeeded', 'data': {'object': {'customer': user_with_stripe_id.stripe_customer_id, 'status': 'active'}}}
    mocker.patch('stripe.Webhook.construct_event', return_value=event_payload)
    client.post(url_for('billing.stripe_webhook'), data='{}', headers={'Stripe-Signature': 'dummy'})
    db.session.refresh(user_with_stripe_id)
    assert user_with_stripe_id.subscription_status == 'active'

def test_customer_portal_redirects_subscribed_user(client, user_with_stripe_id, mocker):
    mocker.patch('stripe.billing_portal.Session.create', return_value=mocker.Mock(url='https://stripe.com/portal_session'))
    with client:
        client.post(url_for('auth.login'), data={'email': user_with_stripe_id.email, 'password': 'password123'})
        response = client.get(url_for('billing.customer_portal'))
    assert response.status_code in [302, 303]
    assert response.location == 'https://stripe.com/portal_session'
