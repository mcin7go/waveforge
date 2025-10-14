import stripe
from flask import render_template, request, jsonify, current_app, abort, Response, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_babel import gettext as _
from . import bp
from app.services import payment_service
from app.models import Plan, User, db

@bp.route('/portal')
@login_required
def customer_portal():
    if not current_user.stripe_customer_id:
        flash(_('Nie znaleziono aktywnej subskrypcji.'), 'warning')
        return redirect(url_for('main.pricing'))
    
    payment_service.init_stripe()
    return_url = url_for('audio_processing.get_processing_history', _external=True)
    
    portal_session = stripe.billing_portal.Session.create(
        customer=current_user.stripe_customer_id,
        return_url=return_url,
    )
    return redirect(portal_session.url, code=303)

@bp.route('/subscribe')
@login_required
def subscribe_page():
    price_id = request.args.get('price_id')
    if not price_id:
        abort(404)
    plan = Plan.query.filter_by(stripe_price_id=price_id).first_or_404()
    publishable_key = current_app.config.get('STRIPE_PUBLISHABLE_KEY')
    return render_template('subscribe.html', stripe_publishable_key=publishable_key, plan=plan)

@bp.route('/create-subscription', methods=['POST'])
@login_required
def create_subscription_endpoint():
    data = request.get_json()
    try:
        customer = payment_service.get_or_create_customer(current_user)
        subscription = payment_service.create_subscription(
            customer_id=customer.id, 
            payment_method_id=data.get('paymentMethodId'), 
            price_id=data.get('priceId')
        )
        return jsonify({'subscriptionId': subscription.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    event = None

    if not sig_header or not endpoint_secret:
        return 'Webhook secret not configured.', 400

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400

    event_map = {
        'invoice.payment_succeeded': 'active',
        'customer.subscription.updated': 'active',
        'invoice.payment_failed': 'past_due',
        'customer.subscription.deleted': 'canceled'
    }
    event_type = event['type']
    if event_type in event_map:
        customer_id = event['data']['object']['customer']
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            user.subscription_status = event_map[event_type]
            db.session.commit()
    
    return Response(status=200)
