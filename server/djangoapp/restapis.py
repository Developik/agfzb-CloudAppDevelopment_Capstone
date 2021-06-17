import requests
import json
import traceback
# import related models here
from requests.auth import HTTPBasicAuth
from .models import CarDealer, CarMake, CarModel, DealerReview
from django.http import HttpResponseRedirect, HttpResponse

from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions, EntitiesOptions, KeywordsOptions

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))


def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))

    json_data = ""

    try:

        if 'api_key' in kwargs:

            authenticator = IAMAuthenticator(kwargs['api_key'])

            natural_language_understanding = NaturalLanguageUnderstandingV1(
                version=kwargs['version'],
                authenticator=authenticator)

            natural_language_understanding.set_service_url(url)

            response = natural_language_understanding.analyze(
                text=kwargs['text'],
                features=kwargs['features']).get_result()

            json_data = response
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)

            status_code = response.status_code
            print("With status {} ".format(status_code))
            json_data = json.loads(response.text)
        # Call get method of requests library with URL and parameters
    except Exception as e:
        # If any error occurs
        traceback.print_exc()
        print("Network exception occurred")

    #  NLU
    '''
    if (response2 is not None):
        status_code2 = response2.status_code
        print("With status {} ".format(status_code2))
        json_data2 = json.loads(response2.text)

        json_data = json_data['entries']['']
    '''
    # print(json_data)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["entries"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function


def get_dealer_reviews_from_cf(url, dealer_id, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealer_id)
    if json_result:
        # Get the row list in JSON as dealers
        reviews = json_result["entries"]
        # For each dealer object
        for review in reviews:
            # Get its content in `doc` object
            # dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            arr_params = ["purchase_date", "dealership", "name",
                          "car_model", "car_make", "car_year", "sentiment", "id", "review", "purchase"]

            for item in arr_params:
                if item not in review:
                    review[item] = ""

            new_sentiment = analyze_review_sentiments(
                review["review"])['keywords'][0]['sentiment']['label']

            print("----" + new_sentiment)

            review_obj = DealerReview(dealership=review["dealership"], name=review["name"], purchase=review["purchase"],
                                      review=review["review"], purchase_date=review["purchase_date"], car_make=review["car_make"],
                                      car_model=review["car_model"],
                                      car_year=review["car_year"], sentiment=new_sentiment, curr_id=review["id"])
            results.append(review_obj)

    return results

# check later


def get_dealer_by_id_from_cf(url, dealerId):
    return get_dealer_reviews_from_cf(url, dealerId)

# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealerreview):
    # params = dict()
    # params["text"] = dealerreview
    # params["version"] = kwargs["version"]
    # params["features"] = kwargs["features"]
    # params["return_analyzed_text"] = kwargs["return_analyzed_text"]

    api_key = 'ypjfbaVTDlmslmMNtrOYs2gyLLToW6Zxd7BlSplyZQfR'

    result = get_request(
        "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/c678fe58-ae0d-445c-be25-9cc5c2a7e8f0",
        api_key=api_key,
        version='2021-03-25',
        text=dealerreview,
        features=Features(
            entities=EntitiesOptions(
                emotion=True, sentiment=True, limit=2),
            keywords=KeywordsOptions(emotion=True, sentiment=True,
                                     limit=2))
    )

    print(result)

    return result


def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("Post to {} ".format(url))

    #json_data = ""

    response = requests.post(url, params=kwargs, json=json_payload)

    status_code = response.status_code
    print("Post With status {} ".format(status_code))
    #json_data = json.loads(response.text)
