
import json, os, requests, smtplib
from email.mime.text import MIMEText
HEADERS={"User-Agent":"Mozilla/5.0"}
KEYWORDS=["pre-order","preorder","add to cart","buy now","in stock"]
products=json.load(open("products.json"))
state_file="data/stock_state.json"
old=json.load(open(state_file)) if os.path.exists(state_file) else {}
new={}; alerts=[]
for p in products:
    try:
        html=requests.get(p["url"],headers=HEADERS,timeout=20).text.lower()
    except Exception:
        html=""
    available=any(k in html for k in KEYWORDS)
    key=f'{p["retailer"]}-{p["product"]}'
    new[key]=available
    if available and not old.get(key,False):
        alerts.append(p)
os.makedirs("data",exist_ok=True)
json.dump(new,open(state_file,"w"),indent=2)
if alerts and os.getenv("EMAIL") and os.getenv("APP_PASSWORD"):
    body="Pokemon Stock Alert\n\n"
    for a in alerts:
        body+=f'{a["retailer"]}\n{a["product"]}\n{a["url"]}\n\n'
    msg=MIMEText(body); msg["Subject"]="Pokemon Stock Alert"; msg["From"]=os.environ["EMAIL"]; msg["To"]=os.environ["EMAIL"]
    s=smtplib.SMTP_SSL("smtp.gmail.com",465); s.login(os.environ["EMAIL"],os.environ["APP_PASSWORD"]); s.send_message(msg); s.quit()
print("Done")
