import json
import logging
import requests
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from .models import LarkProfile


logger = logging.getLogger(__name__)


# Home Page


def index(request):
    return render(request, 'lark_integration/index.html')


# Step 1 — Redirect User to Lark OAuth


def lark_login(request):
    return redirect(
    f"https://open.larksuite.com/open-apis/authen/v1/index?app_id={settings.LARK_APP_ID_1}&redirect_uri={settings.LARK_CALLBACK_URL_1}"
    )


# Step 2 — Callback from Lark OAuth


def lark_callback(request):
    code = request.GET.get('code')
    token_url = "https://open.larksuite.com/open-apis/authen/v1/access_token"
    resp = requests.post(token_url, json={"code": code})
    data = resp.json().get("data", {})


    open_id = data.get("user_id")
    name = data.get("name")
    email = data.get("email")


    user, created = User.objects.get_or_create(username=f"lark_{open_id}")
    if created:
        user.first_name = name
        user.email = email or ''
        user.save()


    LarkProfile.objects.update_or_create(
    user=user,
    defaults={"open_id": open_id, "name": name, "avatar": data.get("avatar"), "extra": data}
    )


    login(request, user)
    return redirect('/')


# Webhook endpoint


@csrf_exempt
def lark_webhook(request):
    body = json.loads(request.body.decode('utf-8'))


    if "challenge" in body:
        return JsonResponse({"challenge": body["challenge"]})


    logger.info("Lark Event Received: %s", body)


    return HttpResponse(status=200)