import json
import re
import requests
from flask import Flask, render_template, request
from fuzzywuzzy import fuzz
import logging
from cachetools import TTLCache

app = Flask(__name__)

# # Logging yapılandırması
# logging.basicConfig(
#     filename='dns_search.log',
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

# 10 dakikalık önbellek (600 saniye TTL)
cache = TTLCache(maxsize=100, ttl=600)

def normalize(text):
    """Verilen metni normalize eder (küçük harfe çevirir, spf numaralarını kaldırır ve boşlukları temizler)."""
    return re.sub(r'(spf)\d+', r'\1', text.lower().strip())

def get_txt_records(domain):
    """Belirtilen domainin TXT kayıtlarını alır ve önbellekle tutarlılık sağlar."""
    domain = domain.strip().lower()
    if not domain:
        logging.warning("Boş domain girildi.")
        return []

    # Önbellekten kontrol et
    if domain in cache:
        logging.info(f"Önbellekten alındı: {domain} -> {cache[domain]}")
        return cache[domain]

    url = f"https://dns.google/resolve?name={domain}&type=TXT"
    records = []
    try:
        response = requests.get(url, timeout=5, headers={'User-Agent': 'DNSChecker/1.0'})
        response.raise_for_status()
        data = response.json()

        if "Answer" not in data:
            logging.warning(f"{domain} için DNS yanıtı boş: {data}")
            cache[domain] = records
            return records

        for answer in data.get("Answer", []):
            record = answer.get("data", "").strip('"')
            if record:
                records.append(record)

        # Kayıtları alfabetik sıraya koyarak tutarlılık sağla
        records.sort()
        logging.info(f"DNS TXT kayıtları alındı: {domain} -> {records}")
    except requests.RequestException as e:
        logging.error(f"TXT kayıtları alınırken hata: {domain} -> {e}")
        records = []

    # Önbelleğe kaydet
    cache[domain] = records
    return records

def search_services(txt_data, json_file="result_1000.json"):
    """TXT verisini analiz ederek JSON dosyasındaki servislerle eşleştirir."""
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        logging.error(f"JSON dosyası bulunamadı: {json_file}")
        return []
    except json.JSONDecodeError as e:
        logging.error(f"JSON dosyası hatalı: {e}")
        return []

    norm_txt = normalize(txt_data)
    found_services = []

    # JSON anahtarlarını sıralı şekilde tara
    for keyword in sorted(data.keys()):  # Tutarlılık için sıralama
        norm_keyword = normalize(keyword)
        similarity = fuzz.partial_ratio(norm_keyword, norm_txt)
        logging.debug(f"Eşleşme kontrolü: {norm_keyword} vs {norm_txt} -> {similarity}%")
        if similarity >= 85:  # Daha kesin eşleşme için %85'e çektim
            for service in data[keyword]:
                found_services.append({
                    "Keyword": keyword,
                    "Service": service.get("Service", "Bilinmiyor"),
                    "Url": service.get("Url", ""),
                    "Icon": service.get("Icon", "")
                })

    # Sonuçları Keyword'e göre sırala
    found_services.sort(key=lambda x: x["Keyword"])
    logging.info(f"Bulunan servisler: {len(found_services)} -> {found_services}")
    return found_services

@app.route("/", methods=["GET", "POST"])
def index():
    """Ana sayfa, domain sorgusu ve servis aramaları burada yapılır."""
    if request.method == "POST":
        domain = request.form.get("domain", "").strip()
        if not domain:
            logging.warning("Domain girilmedi.")
            return render_template("index.html", message="Lütfen bir domain girin.", domain=None)

        txt_records = get_txt_records(domain)
        if not txt_records:
            logging.info(f"{domain} için TXT kaydı bulunamadı.")
            return render_template("index.html", message="TXT kaydı bulunamadı.", domain=domain)

        combined_txt = " ".join(txt_records)
        results = search_services(combined_txt)

        if results:
            logging.info(f"{domain} için {len(results)} servis bulundu.")
            return render_template("index.html", domain=domain, results=results)
        else:
            logging.info(f"{domain} için eşleşme bulunamadı.")
            return render_template("index.html", domain=domain, message="Hiçbir eşleşme bulunamadı.", results=None)

    logging.info("Ana sayfa yüklendi.")
    return render_template("index.html", domain=None)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
