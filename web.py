import json
import re
import requests
from flask import Flask, render_template, request
from cachetools import TTLCache

app = Flask(__name__)


cache = TTLCache(maxsize=100, ttl=600)


def normalize(text):
    return re.sub(r'(spf)\d+', r'\1', text.lower().strip())


def get_txt_records(domain):
    domain = domain.strip().lower()
    if not domain:
        return []


    if domain in cache:
        return cache[domain]

    url = f"https://dns.google/resolve?name={domain}&type=TXT"
    try:
        response = requests.get(url, timeout=5, headers={'User-Agent': 'DNSServiceChecker/1.0'})
        response.raise_for_status()
        data = response.json()
        records = sorted([answer.get("data", "").strip('"') for answer in data.get("Answer", []) if answer.get("data")])


        if not records:
            cache[domain] = []
            return []


        cache[domain] = records
        return records
    except Exception as e:
        print(f"TXT kayıtları alınırken hata oluştu: {e}")
        cache[domain] = []
        return []


def search_services(txt_data, json_file="result_1000.json"):
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"JSON dosyası bulunamadı: {json_file}")
        return []


    norm_txt = normalize(txt_data)
    found_services = []

    # JSON'daki her anahtar ve servis için kontrol
    for keyword, services in sorted(data.items()):  # Anahtarları sıralı işlemek için
        norm_keyword = normalize(keyword)

        # Daha kesin bir eşleştirme: Anahtar kelime TXT içinde tam olarak geçiyorsa
        if norm_keyword in norm_txt:
            for service in services:
                found_services.append({
                    "Keyword": keyword,
                    "Service": service.get("Service", "Bilinmiyor"),
                    "Url": service.get("Url", ""),
                    "Icon": service.get("Icon", "")
                })

    # Sonuçları sıralı ve tutarlı hale getirmek için
    found_services.sort(key=lambda x: x["Keyword"])
    return found_services


@app.route("/", methods=["GET", "POST"])
def index():
    """Ana sayfa, domain sorgusu ve servis aramaları burada yapılır."""
    if request.method == "POST":
        domain = request.form.get("domain", "").strip()
        if not domain:
            return render_template("index.html", message="Lütfen bir domain girin.", domain=None)

        txt_records = get_txt_records(domain)
        if not txt_records:
            return render_template("index.html", message="TXT kaydı bulunamadı.", domain=domain)

        # TXT kayıtlarını birleştir ve sıralı hale getir
        combined_txt = " ".join(sorted(txt_records))
        results = search_services(combined_txt)

        if results:
            return render_template("index.html", domain=domain, results=results)
        else:
            return render_template("index.html", domain=domain, message="Hiçbir eşleşme bulunamadı.", results=None)

    return render_template("index.html", domain=None)


if __name__ == "__main__":
    app.run(debug=True)
