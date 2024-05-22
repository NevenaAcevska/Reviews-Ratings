from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import  AbstractUser
from django.utils import timezone

class Business(models.Model):
    store_name = models.CharField(max_length=100)
    managers = models.ManyToManyField('User', related_name='managed_businesses')

    def __str__(self):
        return self.store_name


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, null=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    first_login = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    store = models.ManyToManyField('Business', related_name='stores')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']

    @property
    def store_name(self):
        return self._store_name

    @store_name.setter
    def store_name(self, value):
        if self.is_superuser:
            try:
                business = Business.objects.get(store_name=value)
                self._store_name = value
                business.store_name = value  # Update the Business object
                business.save()
            except Business.DoesNotExist:
                print(f"The store name '{value}' does not exist.")

    def get_available_store_names(self):
        return Business.objects.values_list('store_name', flat=True)

    def __str__(self):
        return self.email





class Product(models.Model):
    business = models.ForeignKey(Business, related_name='products', on_delete=models.CASCADE, default=1)
    product_name = models.CharField(max_length=100)

    def __str__(self):
        return self.product_name


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    time_date = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        if self.user:
            return f"{self.user.first_name} {self.user.last_name} - {self.product.product_name}"
        else:
            return f"Anonymous - {self.product.product_name}"