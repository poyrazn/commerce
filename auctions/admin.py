from django.contrib import admin

from .models import Category, Listing, Comment, User, Bid, SubCategory
# Register your models here.

admin.site.register(Category)
admin.site.register(Listing)
admin.site.register(Comment)
admin.site.register(User)
admin.site.register(Bid)
admin.site.register(SubCategory)
