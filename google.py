from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

def fetch_image_url(query):
    api_key = "AIzaSyDV5mE_hOKBN4Cm6GEEJ4TmaNI9niUrBqU"
    cse_id = "970835fe6194d4ed0"

    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=cse_id, searchType='image', num=1).execute()

    if 'items' in res:
        return res['items'][0]['link']
    else:
        return None
def get_images(recipe_name):
    image = fetch_image_url(recipe_name)
    return image

print(fetch_image_url("dog"))