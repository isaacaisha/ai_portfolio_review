import json
import os
import cloudinary
import cloudinary.uploader
import requests
from cloudinary.utils import cloudinary_url
from django.shortcuts import render
from selenium import webdriver
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .models import Review


# Configuration       
cloudinary.config( 
    cloud_name = "dobg0vu5e", 
    api_key = os.getenv('CLOUDINARY_API_KEY'), 
    api_secret = os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

# # Upload an image
# upload_result = cloudinary.uploader.upload("https://res.cloudinary.com/demo/image/upload/getting-started/shoes.jpg",
#                                            public_id="shoes")
# print(upload_result["secure_url"])
# 
# # Optimize delivery by resizing and applying auto-format and auto-quality
# optimize_url, _ = cloudinary_url("shoes", fetch_format="auto", quality="auto")
# print(optimize_url)
# 
# # Transform the image: auto-crop to square aspect_ratio
# auto_crop_url, _ = cloudinary_url("shoes", width=100, height=100, crop="auto", gravity="auto")
# print(auto_crop_url)


# Create your views here.
def take_screenshot(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    browser = webdriver.Chrome(options=options)

    browser.get(url)

    total_height = browser.execute_script("return document.body.parentNode.scrollHeight")

    browser.set_window_size(1200, total_height)

    screenshot = browser.get_screenshot_as_png()
    
    browser.quit()

    sanitized_url = url.replace('http//', '').replace('https//', '').replace('/', '_').replace(':', '_')

    upload_response = cloudinary.uploader.upload(
        screenshot,
        folder="screenshots",
        public_id=f"{sanitized_url}.png",
        resource_type='image'
    )

    # print(f'upload_response:\n{upload_response}')
    return upload_response['url']


def get_review(screenshot_url):
    url = "https://general-runtime.voiceflow.com/state/user/testuser/interact?logs=off"

    payload = {
        "action": {
            "type": "intent",
            "payload": {
                "query": screenshot_url,
                "intent": {"name": "review_intent"},
                "entities": []
            }
        },
        "config": {
            "tts": False,
            "stripSSML": True,
            "stopAll": True,
            "excludeTypes": ["block", "debug", "flow"]
        },
        "state": { "variables": { "x_var": 1 } }
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "VF.DM.668a1b221d8545d5b874c748.M2F4coDsRm2khrak"
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    review_text = ""

    for item in data:
        if item['type'] == 'speak' and 'payload' in item and 'message' in item['payload']:
            # The message is a list and we need the first 'speak' item
            review_text = item['payload']['message']
            break

    # print(f'review_text:\n{review_text}')
    return review_text


@require_http_methods(["POST"])
def submit_url(request):
    data = json.loads(request.body)
    domain = data.get('domain')

    website_screenshot = take_screenshot(domain)
    website_review = get_review(website_screenshot)

    new_review_object = Review.objects.create(
        site_url = domain,
        site_image_url = website_screenshot,
        feedback = website_review,
    )

    review_id = new_review_object.id

    response_data = {
        'website_screenshot': website_screenshot,
        'website_review': website_review,
        'review_id': review_id,
    }

    return JsonResponse(response_data)


@require_http_methods(["POST"])
def feedback(request):
    data = json.loads(request.body)
    review_id = data.get('id')
    type = data.get('type')

    try:
        review = Review.objects.get(id=review_id)
        review.user_rating = type
        review.save()

        return JsonResponse({'status': 'success', 'message': 'Feedback submitted 👌🏿'})
    except Review.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Review not found 😭'})


def index(request):
    # upload_response = take_screenshot("https://siisi-ai.online/conversation-test")
    # get_review("http://res.cloudinary.com/dobg0vu5e/image/upload/v1720325970/screenshots/https___siisi-ai.online_conversation-test.png.png")
    return render(request, 'index.html')
