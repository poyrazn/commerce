from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listings/<int:listing_id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("create", views.create_listing, name="create_listing"),
    path("watchlist/add", views.watchlist_add, name="watchlist_add"),
    path("bid/listing<int:listing_id>", views.bid, name="bid"),
]
