headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/139 Safari/537.36"
}

try:
    response = requests.get(
        p["url"],
        headers=headers,
        timeout=20
    )
    page = response.text.lower()
except Exception:
    page = ""
