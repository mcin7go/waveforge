import click
from faker import Faker
from flask.cli import with_appcontext
from . import db
from .models import User, AudioFile, ProcessingTask, Plan
from flask import current_app
import random
from datetime import datetime, timedelta, UTC

@click.command('seed-admin')
@with_appcontext
def seed_admin_command():
    admin_email = current_app.config.get('ADMIN_EMAIL')
    admin_password = current_app.config.get('ADMIN_PASSWORD')
    if not admin_email or not admin_password:
        click.echo('Admin credentials not set in .env. Skipping.')
        return
    user = User.query.filter_by(email=admin_email).first()
    if user:
        if not user.is_admin:
            user.is_admin = True
            db.session.commit()
            click.echo(f'Granted admin privileges to {admin_email}.')
        else:
            click.echo(f'Admin {admin_email} already exists.')
    else:
        new_admin = User(email=admin_email, is_admin=True)
        new_admin.set_password(admin_password)
        db.session.add(new_admin)
        db.session.commit()
        click.echo(f'Admin account for {admin_email} created.')

@click.command('seed-users')
@with_appcontext
def seed_users_command():
    """Seed database with 10 test users (password: Marcin123!)"""
    
    users_data = [
        {'email': 'admin@wavebulk.com', 'is_admin': True, 'subscription': None, 'files': 8},
        {'email': 'pro1@test.com', 'is_admin': False, 'subscription': 'active', 'files': 15},
        {'email': 'pro2@test.com', 'is_admin': False, 'subscription': 'active', 'files': 12},
        {'email': 'free1@test.com', 'is_admin': False, 'subscription': None, 'files': 3},
        {'email': 'free2@test.com', 'is_admin': False, 'subscription': None, 'files': 5},
        {'email': 'trial@test.com', 'is_admin': False, 'subscription': 'trialing', 'files': 7},
        {'email': 'canceled@test.com', 'is_admin': False, 'subscription': 'canceled', 'files': 2},
        {'email': 'producer@wavebulk.com', 'is_admin': False, 'subscription': 'active', 'files': 25},
        {'email': 'podcaster@test.com', 'is_admin': False, 'subscription': 'active', 'files': 18},
        {'email': 'dj@test.com', 'is_admin': False, 'subscription': 'active', 'files': 20},
    ]
    
    password = 'Marcin123!'
    
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    click.echo("🌱 SEEDING DATABASE WITH TEST USERS")
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    click.echo("")
    
    created_count = 0
    skipped_count = 0
    
    for user_data in users_data:
        existing_user = User.query.filter_by(email=user_data['email']).first()
        
        if existing_user:
            click.echo(f"⚠️  Skipping {user_data['email']:<30} (already exists)")
            skipped_count += 1
            continue
        
        # Create user
        new_user = User(
            email=user_data['email'],
            is_admin=user_data['is_admin'],
            subscription_status=user_data['subscription']
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()  # Get user.id
        
        # Create dummy audio files
        num_files = user_data['files']
        for i in range(num_files):
            # Random date in last 30 days
            days_ago = random.randint(0, 30)
            upload_date = datetime.now(UTC) - timedelta(days=days_ago)
            
            # Random LUFS between -20 and -8
            lufs = round(random.uniform(-20, -8), 1)
            
            # Random duration 30s - 5min
            duration = round(random.uniform(30, 300), 1)
            
            # Random file size 5-50MB
            file_size = random.randint(5, 50) * 1024 * 1024
            
            audio_file = AudioFile(
                user_id=new_user.id,
                original_filename=f"track_{i+1:02d}.wav",
                processed_filename=f"track_{i+1:02d}.mp3",
                file_size_bytes=file_size,
                loudness_lufs=lufs,
                true_peak_db=round(random.uniform(-3, -0.1), 2),
                duration_seconds=duration,
                upload_date=upload_date,
                original_file_path=f"/uploads/track_{i+1:02d}.wav",
                processed_file_path=f"/uploads/track_{i+1:02d}.mp3"
            )
            db.session.add(audio_file)
            db.session.flush()
            
            # Create processing task (completed)
            task = ProcessingTask(
                user_id=new_user.id,
                audio_file_id=audio_file.id,
                celery_task_id=f"seed_{new_user.id}_{i}",
                status='COMPLETED',
                result_json={'loudness_lufs': lufs, 'duration_seconds': duration},
                created_at=upload_date,
                completed_at=upload_date + timedelta(seconds=random.randint(10, 60))
            )
            db.session.add(task)
        
        db.session.commit()
        
        role = "👑 ADMIN" if user_data['is_admin'] else f"📊 {user_data['subscription'] or 'FREE'}"
        click.echo(f"✅ Created: {user_data['email']:<30} {role:<15} ({num_files} files)")
        created_count += 1
    
    click.echo("")
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    click.echo(f"✅ Seed complete!")
    click.echo(f"   Created: {created_count} users")
    click.echo(f"   Skipped: {skipped_count} users (already exist)")
    click.echo(f"   Password: {password}")
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    click.echo("")
    click.echo("📋 TEST USERS:")
    click.echo("   • admin@wavebulk.com     - Admin (8 files)")
    click.echo("   • pro1@test.com          - Pro Active (15 files)")
    click.echo("   • pro2@test.com          - Pro Active (12 files)")
    click.echo("   • free1@test.com         - Free (3 files)")
    click.echo("   • free2@test.com         - Free (5 files)")
    click.echo("   • trial@test.com         - Trial (7 files)")
    click.echo("   • canceled@test.com      - Canceled (2 files)")
    click.echo("   • producer@wavebulk.com  - Pro Active (25 files)")
    click.echo("   • podcaster@test.com     - Pro Active (18 files)")
    click.echo("   • dj@test.com            - Pro Active (20 files)")
    click.echo("")
    click.echo(f"🔑 Password for all: {password}")
    click.echo("")

@click.command('seed-plans')
@with_appcontext
def seed_plans_command():
    """Seed database with subscription plans"""
    
    plans_data = [
        {
            'name': 'Free',
            'stripe_product_id': 'prod_free_plan',
            'stripe_price_id': 'price_free',
            'price': 0,
            'interval': 'month',
            'is_active': True
        },
        {
            'name': 'Starter',
            'stripe_product_id': 'prod_starter_plan',
            'stripe_price_id': 'price_starter_monthly',
            'price': 990,  # $9.90/month
            'interval': 'month',
            'is_active': True
        },
        {
            'name': 'Pro',
            'stripe_product_id': 'prod_pro_plan',
            'stripe_price_id': 'price_pro_monthly',
            'price': 1990,  # $19.90/month
            'interval': 'month',
            'is_active': True
        },
        {
            'name': 'Pro Annual',
            'stripe_product_id': 'prod_pro_annual_plan',
            'stripe_price_id': 'price_pro_yearly',
            'price': 19900,  # $199/year (save 16%)
            'interval': 'year',
            'is_active': True
        },
        {
            'name': 'Enterprise',
            'stripe_product_id': 'prod_enterprise_plan',
            'stripe_price_id': 'price_enterprise_monthly',
            'price': 4990,  # $49.90/month
            'interval': 'month',
            'is_active': True
        },
    ]
    
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    click.echo("💳 SEEDING SUBSCRIPTION PLANS")
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    click.echo("")
    
    created_count = 0
    skipped_count = 0
    
    for plan_data in plans_data:
        existing_plan = Plan.query.filter_by(stripe_price_id=plan_data['stripe_price_id']).first()
        
        if existing_plan:
            click.echo(f"⚠️  Skipping {plan_data['name']:<20} (already exists)")
            skipped_count += 1
            continue
        
        new_plan = Plan(
            name=plan_data['name'],
            stripe_product_id=plan_data['stripe_product_id'],
            stripe_price_id=plan_data['stripe_price_id'],
            price=plan_data['price'],
            interval=plan_data['interval'],
            is_active=plan_data['is_active']
        )
        db.session.add(new_plan)
        
        price_display = f"${plan_data['price']/100:.2f}"
        interval_display = plan_data['interval']
        click.echo(f"✅ Created: {plan_data['name']:<20} {price_display:>10}/{interval_display}")
        created_count += 1
    
    db.session.commit()
    
    click.echo("")
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    click.echo(f"✅ Seed complete!")
    click.echo(f"   Created: {created_count} plans")
    click.echo(f"   Skipped: {skipped_count} plans")
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    click.echo("")
    click.echo("💳 AVAILABLE PLANS:")
    click.echo("   1. Free          -    $0.00/month   (10 files, basic)")
    click.echo("   2. Starter       -    $9.90/month   (50 files, all features)")
    click.echo("   3. Pro           -   $19.90/month   (100 files, priority)")
    click.echo("   4. Pro Annual    -  $199.00/year    (save 16%!)")
    click.echo("   5. Enterprise    -   $49.90/month   (unlimited, support)")
    click.echo("")
    click.echo("📍 View at: http://localhost:5000/pricing")
    click.echo("")

def register_commands(app):
    app.cli.add_command(seed_admin_command)
    app.cli.add_command(seed_users_command)
    app.cli.add_command(seed_plans_command)
