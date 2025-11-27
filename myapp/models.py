import hashlib
import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# -----------------------
# Subscription Plan (Stripe Product)
# -----------------------


def md5_file_upload_path(instance, filename):
    """
    Generate an MD5-based filename while keeping the extension.
    """
    ext = filename.split('.')[-1]  # get file extension
    # Optional: include timestamp or user ID to avoid collisions
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S%f")
    hash_input = f"{filename}{timestamp}".encode('utf-8')
    md5_name = hashlib.md5(hash_input).hexdigest()
    # You can put it in a folder like 'uploads/images/'
    return os.path.join('uploads/images/', f"{md5_name}.{ext}")

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)  # Monthly price
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)  # Stripe Price ID
    daily_limit = models.IntegerField(default=0)

    def __str__(self):
        return self.name


# -----------------------
# Product
# -----------------------

class Product(models.Model):
    name = models.CharField(max_length=100)
    subscription_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE,
        default=1  # assuming a "Free" plan exists with ID=1
    )
    image = models.ImageField(upload_to=md5_file_upload_path, blank=True, null=True)
    file = models.FileField(upload_to=md5_file_upload_path, blank=True, null=True)

    def __str__(self):
        return self.name


# -----------------------
# User Subscription
# -----------------------
class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()

    def active(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

    def downloads_today(self):
        today = timezone.now().date()
        return DownloadLog.objects.filter(user=self.user, date=today).count()

    def __str__(self):
        plan_name = self.plan.name if self.plan else "No Plan"
        return f"{self.user.username} - {plan_name}"

    def paid_this_month(self):
        today = timezone.now().date()
        return self.start_date.year == today.year and self.start_date.month == today.month



# -----------------------
# Download Log
# -----------------------

class DownloadLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Download Log"
        verbose_name_plural = "Download Logs"

    def __str__(self):
        return f"{self.user.username} downloaded {self.product.name} on {self.date}"


