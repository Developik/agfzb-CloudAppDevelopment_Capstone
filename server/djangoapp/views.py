from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
from .restapis import get_dealers_from_cf, \
get_dealer_reviews_from_cf, get_dealer_by_id_from_cf, \
post_request
import logging
import json
from django.urls import reverse
from .models import CarDealer, CarMake, CarModel, DealerReview


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
# def contact(request):


def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            # return redirect('djangoapp')
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)
# ...

# Create a `logout_request` view to handle sign out request


def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')
# ...

# Create a `registration_request` view to handle sign up request


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships


def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://b993224f.us-south.apigw.appdomain.cloud/api/dealership/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context['dealerships'] = dealerships
        # Concat all dealer's short name
        #dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        print(dealerships)
        dealer_names = ''
        for dealer in dealerships:
            if (dealer is not None):
                dealer_names += dealer.short_name + " "

        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://b993224f.us-south.apigw.appdomain.cloud/api/review/api/review"
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        url = f"https://b993224f.us-south.apigw.appdomain.cloud/api/dealership/api/dealership"

        dealerships = get_dealers_from_cf(url)

        # Concat all dealer's short name
        #dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        print(reviews)
        dealer_reviews = ''

        oneTime_dealr = True

        curr_dealer = ""

        for dealer in dealerships:
            if str(dealer.id) == str(dealer_id):
                curr_dealer = dealer

        context['reviews'] = reviews
        context['dealer'] = curr_dealer

        print(reviews)
        # Return a list of dealer short name
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review_page(request, dealer_id):
#    context = {}
#    if request.method == "GET":
#        return render(request, 'djangoapp/add_review.html', context)

# Create a `add_review` view to submit a review


def add_review(request, dealer_id):
    context = {}

    if request.method == "GET":
        # query dealer id name
        url = f"https://b993224f.us-south.apigw.appdomain.cloud/api/dealership/api/dealership"

        dealerships = get_dealers_from_cf(url)

        curr_dealer = ""
        for dealer in dealerships:
            if str(dealer.id) == str(dealer_id):
                curr_dealer = dealer

        context['dealer'] = curr_dealer
        context['cars'] = CarModel.objects.filter(dealerId=dealer_id)

        return render(request, 'djangoapp/add_review.html', context)
        return HttpResponseRedirect(reverse(viewname='djangoapp:add_review', args=(dealer_id,)))

    if request.method == "POST" and \
            request.user.is_authenticated:
        url = "https://b993224f.us-south.apigw.appdomain.cloud/api/review/api/review"

        for key, value in request.POST.items():
            print(f'Key: {key}')
            print(f'Value: {value}')

        print("************" + str(request.POST.items()))

        review = dict()
        review["dealership"] = request.POST["dealership"]
        review["review"] = request.POST["review_content"]
        review["purchase"] = request.POST.get("purchasecheck", "off")

        car_details = request.POST["car_details"].split("-")
        review["car_make"] = car_details[0]
        review["car_model"] = car_details[1]
        review["year"] = car_details[2]

        if (request.POST["purchase_date"] == "on"):
            review["purchase_date"] = True
        else:
            review["purchase_date"] = False

        print(request)
        #json_payload = dict()
        #json_payload["review"] = review
        json_payload = review

        result_req = post_request(
            url, json_payload, dealerId=dealer_id)

        return HttpResponseRedirect(reverse(viewname='djangoapp:dealer_details', args=(str(dealer_id),)))
