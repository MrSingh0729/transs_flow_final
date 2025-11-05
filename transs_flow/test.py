import requests

# ---------------- CONFIG ----------------
LARK_APP_ID = "cli_a802ed86e438d028"
LARK_APP_SECRET = "mfbtudMamxM9nKq5tUoh43AJNJT7iJWu"
BITABLE_APP_TOKEN = "UbZRbYrtqaDGwMsY9WmlqhAmgGf"
TABLE_ID = "tblq3hkrNHWvvVJz"
# ----------------------------------------

def get_lark_access_token():
    """Get Lark tenant access token"""
    url = "https://open.larkoffice.com/open-apis/auth/v3/tenant_access_token/internal/"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": LARK_APP_ID, "app_secret": LARK_APP_SECRET}

    try:
        resp = requests.post(url, headers=headers, json=data)
        resp.raise_for_status()
        token = resp.json().get("tenant_access_token")
        print("✅ Tenant Access Token:", token)
        return token
    except Exception as e:
        print("❌ Failed to get access token:", e)
        return None

def fetch_table_schema():
    """Fetch Bitable table fields with their types"""
    token = get_lark_access_token()
    if not token:
        return

    url = f"https://open.larkoffice.com/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{TABLE_ID}/fields"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.get(url, headers=headers)
        print("Status code:", resp.status_code)
        data = resp.json()

        if resp.status_code != 200:
            print("❌ Response:", data)
            return

        fields = data.get("data", {}).get("items", [])
        if not fields:
            print("⚠️ No fields found in this table.")
            return

        print("📋 Fields in table with types:")
        for field in fields:
            name = field.get("name")
            field_type = field.get("type")
            print(f"- {name}: {field_type}")

    except Exception as e:
        print("❌ Failed to fetch table schema:", e)

if __name__ == "__main__":
    fetch_table_schema()
