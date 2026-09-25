import json, os, smtplib, requests
from email.mime.text import MIMEText

KEYWORDS=[
"pre-order","preorder","add to cart","buy now","in stock"
]

products=json.load(open("products.json"))

state_file="data/stock_state.json"

old=json.load(open(state_file)) if os.path.exists(state_file) else {}

new={}
alerts=[]

for p in products:

    page=requests.get(
        p["url"],
        headers={"User-Agent":"Mozilla/5.0"},
        timeout=20
    ).text.lower()

    stock=any(k in page for k in KEYWORDS)

    key=p["retailer"]+"-"+p["product"]

    new[key]=stock

    if stock and not old.get(key,False):
        alerts.append(p)

json.dump(new,open(state_file,"w"),indent=2)

if alerts:

    message="🚨 Pokemon 30th Stock Live\n\n"

    for a in alerts:
        message+=f'{a["retailer"]}\n'
        message+=f'{a["product"]}\n'
        message+=f'{a["url"]}\n\n'

    msg=MIMEText(message)
    msg["Subject"]="Pokemon Stock Alert"
    msg["From"]=os.environ["EMAIL"]
    msg["To"]=os.environ["EMAIL"]

    s=smtplib.SMTP_SSL("smtp.gmail.com",465)
    s.login(os.environ["EMAIL"],os.environ["APP_PASSWORD"])
    s.send_message(msg)
    s.quit()

    if os.environ.get("DISCORD_WEBHOOK"):
        requests.post(os.environ["DISCORD_WEBHOOK"],json={"content":message})

    if os.environ.get("TELEGRAM_TOKEN"):
        requests.get(
            f'https://api.telegram.org/bot{os.environ["TELEGRAM_TOKEN"]}/sendMessage',
            params={
                "chat_id":os.environ["TELEGRAM_CHAT"],
                "text":message
            }
        )
