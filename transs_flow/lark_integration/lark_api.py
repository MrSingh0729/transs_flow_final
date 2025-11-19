import json
import requests
from django.conf import settings


TOKEN_URL = "https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal/"
SEND_MSG_URL = "https://open.larksuite.com/open-apis/im/v1/messages?receive_id_type=chat_id"


def get_tenant_access_token():
    r = requests.post(TOKEN_URL, json={
    "app_id": settings.LARK_APP_ID_1,
    "app_secret": settings.LARK_APP_SECRET_1,
    })
    return r.json().get("tenant_access_token")


def send_text_message(chat_id, text):
    token = get_tenant_access_token()
    payload = {
    "receive_id": chat_id,
    "msg_type": "text",
    "content": json.dumps({"text": text}),
    }
    return requests.post(SEND_MSG_URL, json=payload, headers={"Authorization": f"Bearer {token}"}).json()