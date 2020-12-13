from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    # listing (many to many)
    # listings = models.ManyToManyField(Listing, blank=True, related_name="passengers")
    # watchlist
    # def __str__(self):
    #     return f"{self.first} {self.last}"
    pass


class Category(models.Model):
    # category name
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"


class SubCategory(models.Model):
    name = models.CharField(max_length=64)
    parent = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategory")

    def __str__(self):
        return f"{self.parent.name}/{self.name}"


class Product(models.Model):
    # title
    title = models.CharField(max_length=64)
    # description
    description = models.TextField()
    # starting price
    price = models.DecimalField(max_digits=9, decimal_places=2)
    # photo url
    url = models.URLField(blank=True)
    # category
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.CASCADE, related_name='listings',
                                 default=None)


class Listing(models.Model):
    # product
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # created
    created_at = models.DateTimeField(auto_now_add=True)
    # creator
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    # number of bids
    number_of_bids = models.IntegerField()
    # current price
    price = models.DecimalField(max_digits=9, decimal_places=2)

    # status
    class Status(models.TextChoices):
        Active = 'Active'
        Closed = 'Closed'

    status = models.TextField(choices=Status.choices, default=Status.Active)

    def __str__(self):
        return f"{self.product.title} by {self.creator.username}"

    # comments

    # bidders

    # winner


class Bid(models.Model):
    # user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    # listing
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    # price
    price = models.DecimalField(max_digits=9, decimal_places=2)
    # bid time
    bid_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.price} on {self.listing_id.product_id.title} by {self.user_id.username}"


class Comment(models.Model):
    # user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    # listing
    listing = models.ForeignKey(Listing, blank=False, on_delete=models.CASCADE, related_name='comments')
    # comment
    comment = models.TextField()
    # time sent
    time_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.listing_id.product_id.title} by {self.user_id.username}"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='watchlist')
