import stripe
from flask import current_app
from app import db
from app.models import User, Plan

def init_stripe():
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')

def create_plan(name: str, price_cents: int, currency: str, interval: str) -> (stripe.Product, stripe.Price):
    init_stripe()
    product = stripe.Product.create(name=name)
    price = stripe.Price.create(product=product.id, unit_amount=price_cents, currency=currency, recurring={"interval": interval})
    return product, price

def archive_plan(plan: Plan):
    """Archiwizuje produkt w Stripe, co uniemożliwia nowe subskrypcje."""
    init_stripe()
    stripe.Product.modify(plan.stripe_product_id, active=False)

def get_or_create_customer(user: User) -> stripe.Customer:
    init_stripe()
    if user.stripe_customer_id:
        try:
            return stripe.Customer.retrieve(user.stripe_customer_id)
        except stripe.error.InvalidRequestError:
            pass
    customer = stripe.Customer.create(email=user.email, name=user.email)
    user.stripe_customer_id = customer.id
    db.session.commit()
    return customer

def create_subscription(customer_id: str, payment_method_id: str, price_id: str) -> stripe.Subscription:
    init_stripe()
    try:
        stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)
        stripe.Customer.modify(customer_id, invoice_settings={'default_payment_method': payment_method_id})
    except stripe.error.CardError as e:
        raise e
    subscription = stripe.Subscription.create(customer=customer_id, items=[{'price': price_id}], expand=['latest_invoice.payment_intent'])
    return subscription
