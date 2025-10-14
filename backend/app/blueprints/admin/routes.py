from flask import render_template, request, redirect, url_for, flash
from flask_babel import gettext as _
from . import bp
from app import db
from app.models import Plan, User
from app.utils.decorators import admin_required
from app.services import payment_service

@bp.route('/plans', methods=['GET', 'POST'])
@admin_required
def manage_plans():
    if request.method == 'POST':
        try:
            name = request.form['name']
            price = int(float(request.form['price']) * 100)
            currency = request.form['currency'].lower()
            interval = request.form['interval']
            product, price_obj = payment_service.create_plan(name, price, currency, interval)
            new_plan = Plan(name=name, stripe_product_id=product.id, stripe_price_id=price_obj.id, price=price, interval=interval)
            db.session.add(new_plan)
            db.session.commit()
            flash(_('Nowy plan został pomyślnie utworzony.'), 'success')
        except Exception as e:
            flash(_('Wystąpił błąd: %(error)s', error=str(e)), 'danger')
        return redirect(url_for('admin.manage_plans'))

    plans = Plan.query.order_by(Plan.id).all()
    return render_template('admin_plans.html', plans=plans)

@bp.route('/plans/<int:plan_id>/archive', methods=['POST'])
@admin_required
def archive_plan(plan_id):
    plan = db.session.get(Plan, plan_id)
    if plan and plan.is_active:
        try:
            payment_service.archive_plan(plan)
            plan.is_active = False
            db.session.commit()
            flash(_('Plan "%(plan_name)s" został zarchiwizowany.', plan_name=plan.name), 'success')
        except Exception as e:
            flash(_('Błąd podczas archiwizacji w Stripe: %(error)s', error=str(e)), 'danger')
    else:
        flash(_('Nie znaleziono aktywnego planu o podanym ID.'), 'warning')
    return redirect(url_for('admin.manage_plans'))

@bp.route('/users')
@admin_required
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users)
