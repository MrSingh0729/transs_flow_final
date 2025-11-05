# mes_forwarder.py
# Run: python mes_forwarder.py
from flask import Flask, request, Response
import requests
import base64

UPSTREAM = "http://10.61.248.12:6803"   # real MES server (no path)
# If your original proxy required auth to reach internet, set upstream_proxy below:
UPSTREAM_PROXY = None
# UPSTREAM_PROXY = {
#   "http": "http://Systemuser:Systemuser@12.99.9.1:80",
#   "https": "http://Systemuser:Systemuser@12.99.9.1:80"
# }

app = Flask(__name__)

@app.route('/PLDB_SZ/FramworkServlet', methods=['POST'])
def proxy_servlet():
    data = request.get_data()
    print("=== Incoming MES Request ===")
    try:
        print(data.decode('utf-8'))
    except:
        print(data)
    # forward to real server
    url = UPSTREAM + '/PLDB_SZ/FramworkServlet'
    headers = {k: v for k, v in request.headers.items() if k.lower() != 'host'}
    try:
        resp = requests.post(url, headers=headers, data=data, proxies=UPSTREAM_PROXY, timeout=15)
        return Response(resp.content, status=resp.status_code, headers=dict(resp.headers))
    except Exception as e:
        return ("Error forwarding: " + str(e), 502)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
