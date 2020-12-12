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


class Listing(models.Model):
    # title
    title = models.CharField(max_length=64)
    # description
    description = models.TextField()
    # starting price
    price = models.DecimalField(max_digits=9, decimal_places=2)
    # current price
    currentPrice = models.DecimalField(max_digits=9, decimal_places=2, default=price)
    # photo url
    url = models.URLField(blank=True)
    # category
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.CASCADE, related_name='listings', default=None)
    # created
    created = models.DateTimeField(auto_now_add=True)
    # creator
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')

    # status
    class Status(models.TextChoices):
        Active = 'Active'
        Closed = 'Closed'

    status = models.TextField(choices=Status.choices, default=Status.Active)

    def __str__(self):
        return f"{self.title} by {self.creator.username}"

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

    def __str__(self):
        return f"{self.price} on {self.listing.title} by {self.user.username}"


class Comment(models.Model):
    # user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    # listing
    listing = models.ForeignKey(Listing, blank=False, on_delete=models.CASCADE, related_name='comments')
    # comment
    comment = models.TextField()

    def __str__(self):
        return f"Comment on {self.listing.title} by {self.user.username}"
