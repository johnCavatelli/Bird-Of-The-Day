import requests
from PIL import Image
from io import BytesIO
from io import FileIO
from flask import Flask, render_template
import datetime
import urllib.request

useAPI = True
apiResponse = ""
birdCommonName = ""
birdScientificName = ""
birdOrder = ""
birdFamily = ""
webApp = Flask(__name__)


# Function extracts the link from the Google API Responce
def extract_link(json):
    return json["items"][0]["link"]


# Flask Implementation for the home page, takes information about the bird
@webApp.route("/")
def home():
    global birdCommonName  # pulls global variables of the bird data
    global birdScientificName  # I know they're a no-no, but I didn't really want to work around flask for this
    global birdOrder
    global birdFamily
    curr_date = datetime.datetime.now()
    if birdCommonName == "":
        birdCommonName = "Error Bird"
    return render_template("index.html", dateString=curr_date.strftime("%B %d, %Y"), birdName=birdCommonName,
                           scienceName=birdScientificName, order=birdOrder, family=birdFamily)


# Flask Implementation of the about page
@webApp.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    # Test using default data or use the API
    if not useAPI:
        # Fill all static data rather than pulling it from the API
        birdCommonName = "American Robin"
        birdScientificName = "Turdus migratorius"
        birdOrder = "Passeriformes"
        birdFamily = "Turdidae"
        img = Image.open(r"static\img\test.jpg")  # Open the test image, save it as the bird that the page pulls from
        img.save(r"static\img\bird.jpg")
    else:
        url = "https://ebird.org/species/surprise-me"  # Url for getting a random bird
        ebirdApiUrl = "https://api.ebird.org/v2/ref/taxonomy/ebird?species="
        googleApikey = "xxx"
        searchEngineID = "74ef369a6dbc51d2c"  # Specific Custom Search Engine ID (Only looks on bird sites and Wikipedia)
        ebird_headers = {
            'X-eBirdApiToken': 'XXXXXXX'
        }
        ebird_payload = {}

        # Getting Species from ebird website's built in feature. Goes to URL, sees redirect, and takes bird ID for reverse lookup
        response = requests.get(url, allow_redirects=True)
        birdId = response.url.split("/")  # Break up URL responce, take last section (the Ebird ID)
        birdId = birdId[-1]
        ebirdApiUrl += birdId  # Add birdId to URL to get more detailed info directly through the API

        apiResponse = requests.request("GET", ebirdApiUrl, headers=ebird_headers, data=ebird_payload)
        # print(apiResponse.text)  # Print's all bird json text from Ebird API
        birdInfo = apiResponse.text.split(',')  # split up the API Responce by the commas
        birdScientificName = birdInfo[14]  # pull out scientific name from array of values
        birdScientificName = birdScientificName[
                             12:]  # Because of a newline between headers and data, take out the first 12 characters
        birdCommonName = birdInfo[15]
        birdOrder = birdInfo[22]
        birdFamily = birdInfo[23]

        # Google API Section
        googleUrl = "https://www.googleapis.com/customsearch/v1"
        google_Payload = {
            'key': 'xxx',
            'cx': '74ef369a6dbc51d2c',
            'q': birdCommonName,  # Use the bird's common name as a search query
            'num': '1',
            'searchType': 'image'
        }
        response = requests.get(googleUrl, params=google_Payload)
        # print(response.url) # prints the url that came from  api
        # print(response.text)  # prints the google full responce
        birdImgLink = extract_link(response.json())
        # print(birdImgLink) # The url of the image the bird is at

        # Pull image of bird from internet using url from Google API
        headers = {
            'accept': 'image',
        }
        response = requests.get(birdImgLink, headers)
        try:  # sometimes pictures of the bird don't come up from the search, or are in the wrong format
            img = Image.open(BytesIO(response.content))  # save the image from the raw data
            img.save(r"static\img\bird.jpg")
        except Exception as e:
            print("An exception occurred trying to get an image of the bird! Not all birds want to be seen!")
            # Build the website (wether using the API or not)
    webApp.run()  # launch the flask app
