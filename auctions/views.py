from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
# from .models import User, Listing, Category, Bid, Comment
from .models import *
from .forms import ListingForm, BidForm
import decimal


def index(request):
    """
    :param request: HTTP request
    :return: homepage
    """

    return render(request, "auctions/index.html", {"listings": Listing.objects.all()})


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
    :param request: HTTP request
    :param listing_id: listing id (pk)
    :return: corresponding listing page
    """
    # if request.method == 'POST':
    #     print(request)
    #     print(request.POST)
    #     return HttpResponseRedirect("/")

    # select listing from db
    try:
        listing = Listing.objects.get(id=listing_id)
    # if listing could not be found
    except Listing.DoesNotExist:
        raise Http404("Listing not found.")

    # if listing is still active users should be able to view all details about the listing
    # Title, description, photo (if exists), category, current price of the listing, comments on the listing
    if listing.status == 'Active':
        winner = False
        try:
            bids_count = listing.bids.count()
            comments = listing.comments.all()
            if bids_count != 0 and listing.bids.get(price=listing.currentPrice).user == request.user:
                winner = True
            print("Comments:")
            print(comments)
            print("Number of bids:")
            print(bids_count)
            # winner = Bid.objects.get(price=listing.currentPrice, listing=listing_id).user
        except Bid.DoesNotExist:
            print("Does not exist")
        return render(request, "auctions/listing.html", {"listing": listing, "comments": comments, "bids": bids_count, "winner": winner, "form": BidForm()})

    # if listing is closed by the creator and the user(visitor) has won, it is shown on the page
    else:
        try:
            winner = listing.bids.get(price=listing.currentPrice).user
            # print(winner)
            # winner = Bid.objects.get(price=listing.currentPrice, listing=listing_id).user
        except Bid.DoesNotExist:
            winner = False
            print("Does not exist")
        if winner == request.user:
            winner = True
        return render(request, "auctions/closed.html", {"listing": listing, "winner": winner, "form": BidForm()})


@login_required(login_url='login', redirect_field_name='watchlist')
def watchlist(request):
    return render(request, "auctions/watchlist.html")


@login_required(login_url='login', redirect_field_name='create_listing')
def create_listing(request):
    """
    :param request: HTTP request
    :return: page with a form that allows user to create a listing
    """
    if request.method == "POST":
        form = ListingForm(request.POST)
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
                new_listing = Listing(title=title, description=description, price=price, currentPrice=price, url=url,
                                      creator=creator)
                new_listing.save()
                return HttpResponseRedirect(reverse("index"))

            new_listing = Listing(title=title, description=description, price=price, currentPrice=price, url=url, category=category, creator=creator)
            new_listing.save()
            return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "auctions/add.html", {
            "form": ListingForm()
        })


def watchlist_add(request):
    pass


def watchlist(request):
    pass


@login_required(login_url='login', redirect_field_name='listing')
def bid(request, listing_id):
    # form = BidForm(request.POST)
    # form.validate()
    # print(form.cleaned_data['bid'])
    # if form.is_valid():
    #     print(form.cleaned_data['bid'])
    # else:
    #     print("Not Valid")
    #     print(form.errors)
    # decimal.getcontext().prec = 2
    bid = decimal.Decimal(request.POST['bid'])
    listing = Listing.objects.get(pk=listing_id)

    if bid <= listing.currentPrice:
        print(bid)
        print(type(bid))
        return HttpResponseBadRequest("Bad Request: Your bid cannot be less than or equal to the current bid.")

    if bid >= decimal.Decimal(9999999.99):
        return HttpResponseBadRequest("Bad Request: Your bid cannot be greater than 9999999.99")

    try:
        user = User.objects.get(username=request.user)
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse("index"))

    # new_bid = Bid(user=user, listing=listing, price=bid)
    # new_bid.save()
    new_bid = Bid.objects.create(user=user, listing=listing, price=bid)
    listing.bids.add(new_bid)
    listing.currentPrice = bid
    listing.save()
    return HttpResponseRedirect("/")
