import pytest
from flask import url_for

ENDPOINTS = [
    ('main.index', {}),
    ('main.pricing', {}),
    ('auth.login', {}),
    ('auth.register', {}),
    ('auth.logout', {}),
    ('auth.reset_password_request', {}),
    ('audio_processing.get_processing_history', {}),
    ('audio_processing.upload_and_process_audio', {}),
    ('billing.subscribe_page', {'price_id': 'price_pro'}),
    ('billing.customer_portal', {}),
    ('admin.manage_plans', {}),
    ('admin.manage_users', {}),
]

EXPECTED_STATUS_CODES = {
    'guest': {
        'main.index': 200, 'main.pricing': 200, 'auth.login': 200, 'auth.register': 200,
        'auth.reset_password_request': 200, 'auth.logout': 302,
        'audio_processing.get_processing_history': 302,
        'audio_processing.upload_and_process_audio': 302,
        'billing.subscribe_page': 302, 'billing.customer_portal': 302,
        'admin.manage_plans': 403, 'admin.manage_users': 403,
    },
    'user': {
        'main.index': 200, 'main.pricing': 200, 'auth.login': 302, 'auth.register': 302,
        'auth.logout': 302, 'auth.reset_password_request': 302,
        'audio_processing.get_processing_history': 200,
        'audio_processing.upload_and_process_audio': 302,
        'billing.subscribe_page': 200, 'billing.customer_portal': 302,
        'admin.manage_plans': 403, 'admin.manage_users': 403,
    },
    'subscriber': {
        'main.index': 200, 'main.pricing': 200, 'auth.login': 302, 'auth.register': 302,
        'auth.logout': 302, 'auth.reset_password_request': 302,
        'audio_processing.get_processing_history': 200,
        'audio_processing.upload_and_process_audio': 200,
        'billing.subscribe_page': 200, 'billing.customer_portal': 303,
        'admin.manage_plans': 403, 'admin.manage_users': 403,
    },
    'admin': {
        'main.index': 200, 'main.pricing': 200, 'auth.login': 302, 'auth.register': 302,
        'auth.logout': 302, 'auth.reset_password_request': 302,
        'audio_processing.get_processing_history': 200,
        'audio_processing.upload_and_process_audio': 200,
        'billing.subscribe_page': 200, 'billing.customer_portal': 303,
        'admin.manage_plans': 200, 'admin.manage_users': 200,
    }
}

@pytest.mark.parametrize("endpoint, kwargs", ENDPOINTS)
@pytest.mark.parametrize("user_type", ['guest', 'user', 'subscriber', 'admin'])
def test_url_reachability(
    client, test_user, admin_user, user_with_stripe_id, plan_in_db, db, mocker,
    endpoint, kwargs, user_type
):
    if endpoint == 'billing.customer_portal':
        mocker.patch(
            'stripe.billing_portal.Session.create',
            return_value=mocker.Mock(url='https://mocked.stripe.portal/url')
        )

    users_to_login = {
        'user': test_user,
        'subscriber': user_with_stripe_id,
        'admin': admin_user
    }

    if user_type in users_to_login:
        user = users_to_login[user_type]
        if user_type in ['subscriber', 'admin']:
            user.subscription_status = 'active'
            if user.stripe_customer_id is None:
                user.stripe_customer_id = 'cus_generic_for_test'
            db.session.commit()
        client.post(url_for('auth.login'), data={'email': user.email, 'password': 'password123'})

    expected_status = EXPECTED_STATUS_CODES[user_type][endpoint]
    response = client.get(url_for(endpoint, **kwargs))
    
    # Specjalna asercja dla przekierowania do portalu Stripe
    if endpoint == 'billing.customer_portal' and user_type in ['subscriber', 'admin']:
        assert response.status_code == expected_status
        assert 'mocked.stripe.portal' in response.location
    else:
        assert response.status_code == expected_status, \
            f"Endpoint '{endpoint}' for user '{user_type}' returned {response.status_code} but expected {expected_status}"
