import json
import os
import smtplib
import requests
from email.mime.text import MIMEText

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

KEYWORDS = [
    "pre-order",
    "preorder",
    "add to cart",
    "buy now",
    "in stock"
]

with open("products.json") as f:
    products = json.load(f)

STATE_FILE = "data/stock_state.json"

if os.path.exists(STATE_FILE):
    with open(STATE_FILE") as f:
        previous = json.load(f)
else:
    previous = {}

current = {}
alerts = []

for item in products:

    try:
        response = requests.get(
            item["url"],
            headers=HEADERS,
            timeout=20
        )

        html = response.text.lower()

    except Exception:
        html = ""

    available = any(word in html for word in KEYWORDS)

    key = f'{item["retailer"]}-{item["product"]}'

    current[key] = available

    if available and not previous.get(key, False):
        alerts.append(item)

os.makedirs("data", exist_ok=True)

with open(STATE_FILE, "w") as f:
    json.dump(current, f, indent=2)

if alerts and os.getenv("EMAIL") and os.getenv("APP_PASSWORD"):

    body = "Pokemon 30th Celebration Stock Found\n\n"

    for a in alerts:
        body += f'{a["retailer"]}\n'
        body += f'{a["product"]}\n'
        body += f'{a["url"]}\n\n'

    msg = MIMEText(body)
    msg["Subject"] = "🚨 Pokemon Stock Alert"
    msg["From"] = os.environ["EMAIL"]
    msg["To"] = os.environ["EMAIL"]

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(os.environ["EMAIL"], os.environ["APP_PASSWORD"])
    server.send_message(msg)
    server.quit()

print("Stock check completed successfully.")
