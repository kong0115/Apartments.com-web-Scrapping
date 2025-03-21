from google.maps import places_v1
from google.api_core import client_options
from dotenv import load_dotenv
import os
import pandas as pd
import traceback
import random 
import time

load_dotenv()
API_KEY = os.getenv("API_KEY")
client_options_instance = client_options.ClientOptions(api_key=API_KEY)
client = places_v1.PlacesClient(client_options=client_options_instance)

field_mask = "places.rating,places.userRatingCount,places.googleMapsUri"
try:
    input_file_name = "Apartment.csv"
    output_file_name = "Apartment_with_google_reviews.csv"
    apartment_list = []
    if os.path.exists(input_file_name):
        apartment_list = pd.read_csv(input_file_name).to_dict(orient="records")
    if os.path.exists(output_file_name):
        apartment_list_with_google_reviews = pd.read_csv(output_file_name).to_dict(orient="records")
    apartment_list_with_google_reviews_dict = {
        apartment["link"]: apartment for apartment in apartment_list_with_google_reviews
    }
    for apartment in apartment_list:
        link = apartment["link"]
        if apartment_list_with_google_reviews_dict.get(link) is None:
            time.sleep(random.randint(2, 5))
            request = places_v1.SearchTextRequest(
                text_query=f"{apartment['name']} Apartments {apartment['address']}"
            )
            response = client.search_text(request=request,  metadata=[("x-goog-fieldmask",field_mask)])
            print(response)
            apartment["googleReviewRating"] = response.places[0].rating
            apartment["googleReviewCount"] = response.places[0].user_rating_count
            apartment["googleReviewLink"] = response.places[0].google_maps_uri
            apartment_list_with_google_reviews.append(apartment)

except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()
pd.DataFrame(apartment_list_with_google_reviews).to_csv(output_file_name, index=False)