from django.db import models
from django.contrib.auth.models import User
from branches.models import Branch
import random
from django.db.models.signals import post_save
from django.dispatch import receiver

# Generate account number
def generate_account_number():
    return "BANK" + str(random.randint(1000000000, 9999999999))

# ----------------------------
# Account Model
# ----------------------------
class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = generate_account_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.account_number}"

# ----------------------------
# Profile Model
# ----------------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=(
        ('admin','Admin'),
        ('manager','Manager'),
        ('customer','Customer'),
    ),
    default='customer')
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    message = models.TextField(blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reply = models.TextField(blank=True, null=True)
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='profile_pics/', default='default_profile.png', blank=True)
    def __str__(self):
        return f"{self.user.username} Profile"

# ----------------------------
# Signal: Automatically create Profile & Account
# ----------------------------
@receiver(post_save, sender=User)
def create_profile_and_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)
        Profile.objects.create(
            user=instance,
            role='customer'  # branch will be set by form later
        )
