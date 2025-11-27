import os
import django
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from django.contrib.auth.models import User
from myapp.models import Product, Subscription, SubscriptionPlan

# -----------------------
# Helper function to get media path
# -----------------------
def media_path(path):
    full_path = os.path.join("media", path)
    return full_path if os.path.exists(full_path) else None


# -----------------------
# Create Subscription Plans
# -----------------------
subscription_plans = [
    {"name": "Free", "daily_limit": 3},
    {"name": "Basic", "daily_limit": 10},
    {"name": "Pro", "daily_limit": 100},
]

plan_objects = {}
for plan_data in subscription_plans:
    plan, created = SubscriptionPlan.objects.get_or_create(
        name=plan_data['name'],
        defaults={"daily_limit": plan_data['daily_limit']}
    )
    # Ensure daily_limit is up-to-date
    if not created and plan.daily_limit != plan_data['daily_limit']:
        plan.daily_limit = plan_data['daily_limit']
        plan.save()
    plan_objects[plan.name] = plan
print("✅ Subscription plans created/updated.")


# -----------------------
# Create Products
# -----------------------
products = [
    {"name": "Free Product 1", "plan": "Free", "image": "product_images/free1.png", "file": "product_files/free1.pdf"},
    {"name": "Basic Product 1", "plan": "Basic", "image": "product_images/basic1.png", "file": "product_files/basic1.pdf"},
    {"name": "Pro Product 1", "plan": "Pro", "image": "product_images/pro1.png", "file": "product_files/pro1.pdf"},
]

for p in products:
    plan = plan_objects[p['plan']]
    product, created = Product.objects.get_or_create(
        name=p['name'],
        subscription_plan=plan
    )
    # Assign image and file if provided and exist
    updated = False
    img_path = media_path(p['image'])
    file_path = media_path(p['file'])
    if img_path and product.image != p['image']:
        product.image = p['image']
        updated = True
    if file_path and product.file != p['file']:
        product.file = p['file']
        updated = True
    if updated:
        product.save()
print("✅ Products created/updated.")


# -----------------------
# Create Users and Subscriptions
# -----------------------
users = [
    {"username": "freeuser", "email": "free@example.com", "password": "free123", "plan": "Free"},
    {"username": "basicuser", "email": "basic@example.com", "password": "basic123", "plan": "Basic"},
    {"username": "prouser", "email": "pro@example.com", "password": "pro123", "plan": "Pro"},
]

for u in users:
    user, created = User.objects.get_or_create(username=u['username'], email=u['email'])
    if created:
        user.set_password(u['password'])
        user.save()

    # Link user to subscription
    plan = plan_objects[u['plan']]
    start_date = timezone.now().date()
    end_date = start_date + timedelta(days=365)

    subscription, sub_created = Subscription.objects.get_or_create(
        user=user,
        defaults={
            "plan": plan,
            "start_date": start_date,
            "end_date": end_date
        }
    )
    # Update existing subscription if needed
    if not sub_created:
        subscription.plan = plan
        subscription.start_date = start_date
        subscription.end_date = end_date
        subscription.save()
print("✅ Users and subscriptions created/updated.")


# -----------------------
# Create Superuser
# -----------------------
super_username = "admin"
super_email = "admin@example.com"
super_password = "admin123"

if not User.objects.filter(username=super_username).exists():
    User.objects.create_superuser(super_username, super_email, super_password)
    print("✅ Superuser created.")
else:
    print("ℹ️ Superuser already exists.")

print("🎉 Data load complete.")
