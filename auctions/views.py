from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
# from .models import User, Listing, Category, Bid, Comment
from .models import *
from .forms import ProductForm, BidForm
import decimal


def index(request):
    """
    :param request: HTTP request
    :return: homepage
    """
    return render(request, "auctions/index.html", {"listings": Listing.objects.filter(status=Listing.Status.Active)})


def login_view(request):
    """
    :param request: HTTP request
    :return: login page
    """
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    """
    :param request: HTTP request
    :return: logout page
    """
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """
    :param request: HTTP request
    :return: registration page
    """
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def listing(request, listing_id):
    """
    If listing is still active users should be able to view all details about the listing including title,
    description, photo (if exists), category, current price of the listing, comments on the listing
    If listing is closed by the creator and the user has won, it is shown on the page

    :param request: HTTP request
    :param listing_id: listing id (pk)
    :return: corresponding listing page
    """
    if request.method == 'POST':
        listing = Listing.objects.get(pk=listing_id)
        listing.status = Listing.Status.Closed
        listing.save()
        print(request)
        print(request.POST)
        return HttpResponseRedirect("/")

    # select listing from db
    try:
        listing = Listing.objects.get(id=listing_id)
    # if listing could not be found
    except Listing.DoesNotExist:
        return HttpResponseBadRequest("Bad Request: listing does not exist")

    winner = False
    on_watchlist = False
    try:
        if listing.number_of_bids != 0 and listing.bids.get(price=listing.price).user == request.user:
            winner = True
        if request.user.is_authenticated:
            watchlist_item = request.user.watchlist.get(listing=listing)
            on_watchlist = True
    except Bid.DoesNotExist:
        return HttpResponseBadRequest("Bad Request: bid does not exist")
    except Watchlist.DoesNotExist:
        return HttpResponseBadRequest("Bad Request: watchlist does not exist")

    return render(request, "auctions/listing.html", {"listing": listing, "winner": winner, "on_watchlist": on_watchlist})


@login_required(login_url='login', redirect_field_name='watchlist')
def watchlist(request):
    return render(request, "auctions/watchlist.html", {"watchlist": request.user.watchlist.all()})


@login_required(login_url='login', redirect_field_name='create_listing')
def create_listing(request):
    """
    :param request: HTTP request
    :return: page with a form that allows user to create a listing
    """
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            price = form.cleaned_data["price"]
            url = form.cleaned_data["url"]
            category_id = form.cleaned_data["category"]
            creator = User.objects.get(pk=request.user.id)
            try:
                category = Category.objects.get(pk=int(category_id))
            except Category.DoesNotExist:
                product = Product(title=title, description=description, price=price, url=url)
                product.save()
                listing = Listing(product=product, creator=creator, number_of_bids=0, price=price)
                listing.save()
                return HttpResponseRedirect(reverse("index"))

            product = Product(title=title, description=description, price=price, url=url, category=category)
            product.save()
            listing = Listing(product=product, creator=creator, number_of_bids=0, price=price)
            listing.save()
            return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "auctions/add.html", {
            "form": ProductForm()
        })


@login_required(login_url='login', redirect_field_name='listing')
def watchlist_add(request, listing_id):
    """
    allows users to add the listing on their watchlist
    :param request: HTTP request
    :param listing_id: listing id (pk)
    :return:
    """

    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        return HttpResponseBadRequest("Bad Request: listing does not exist")
    watchlist_item = Watchlist(user=request.user, listing=listing)
    watchlist_item.save()
    return HttpResponseRedirect(reverse("index"))


@login_required(login_url='login', redirect_field_name='listing')
def watchlist_remove(request, listing_id):

    """
    allows users to remove the listing from their watchlist
    :param request: HTTP request
    :param listing_id: listing id (pk)
    :return:
    """

    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        return HttpResponseBadRequest("Bad Request: listing does not exist")
    watchlist_item = request.user.watchlist.get(listing=listing)
    watchlist_item.delete()
    return HttpResponseRedirect(reverse("index"))


@login_required(login_url='login', redirect_field_name='listing')
def bid(request, listing_id):
    """
    allows users to bid on a listing
    :param request: HTTP request
    :param listing_id: listing id (pk)
    :return:
    """
    bid = decimal.Decimal(request.POST['bid'])
    listing = Listing.objects.get(pk=listing_id)

    if bid <= listing.price:
        print(bid)
        print(type(bid))
        return HttpResponseBadRequest("Bad Request: Your bid cannot be less than or equal to the current bid.")

    if bid >= decimal.Decimal(9999999.99):
        return HttpResponseBadRequest("Bad Request: Your bid cannot be greater than 9999999.99")

    try:
        user = User.objects.get(username=request.user)
    except User.DoesNotExist:
        return HttpResponseBadRequest("Bad Request: user does not exist")

    new_bid = Bid.objects.create(user=user, listing=listing, price=bid)
    listing.bids.add(new_bid)
    listing.price = bid
    listing.number_of_bids += 1
    listing.save()
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

