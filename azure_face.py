import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

# set to your own subscription key value

subscription_key = os.getenv("AZURE_FACE_API_KEY")
assert subscription_key

# replace <My Endpoint String> with the string from your endpoint URL
face_api_url = os.getenv("AZURE_FACE_DETECTION_API_ENDPOINT")

def face_insights(image_path):
    print(image_path)
    data = open(image_path, "rb").read()
    headers = {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': subscription_key
    }

    params = {
        'returnFaceId': 'false',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': 'gender',
    }

    response = requests.post(face_api_url, params=params,
                            headers=headers, data=data)
    # print(json.dumps(response.json()))
    data_payload = response.json()

    return data_payload