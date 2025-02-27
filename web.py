import json
import re
import requests
from flask import Flask, render_template, request
import logging
from cachetools import TTLCache

app = Flask(__name__)

#
# # Logging yapılandırması
# logging.basicConfig(
#     filename='dns_search.log',
#     level=logging.DEBUG,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

# 10 dakikalık önbellek (600 saniye TTL)
cache = TTLCache(maxsize=100, ttl=600)


def normalize(text):
    """Verilen metni JSON anahtarlarıyla eşleşecek şekilde normalize eder."""
    text = text.lower().strip()
    text = re.sub(r'(v=)?spf\d*', '', text)  # SPF ve v= terimlerini kaldır
    text = re.sub(r'~all|\+all|-all|\?all', '', text)  # SPF son eklerini kaldır
    text = re.sub(r'include:', '', text)  # "include:" ön ekini kaldır
    return text.strip()


def get_txt_records(domain):
    """Belirtilen domainin TXT kayıtlarını alır ve belirli bölümleri çıkarır."""
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
    parsed_values = []

    try:
        response = requests.get(url, timeout=5, headers={'User-Agent': 'DNSChecker/1.0'})
        response.raise_for_status()
        data = response.json()

        if "Answer" not in data:
            logging.warning(f"{domain} için DNS yanıtı boş: {data}")
            cache[domain] = []
            return []

        for answer in data.get("Answer", []):
            record = answer.get("data", "").strip('"')
            if record:
                records.append(record)
                parsed_values.append(record)  # Tüm TXT kaydını ekle
                # "include:" içeren bölümleri alma
                includes = re.findall(r'include:([\w\.-]+)', record)
                parsed_values.extend(includes)
                # Eşittirden önceki kısmı alma (SPF hariç)
                if "=" in record and "spf" not in record.lower():
                    key_part = record.split("=")[0].strip()
                    parsed_values.append(key_part)

        # Kayıtları alfabetik sıraya koyarak tutarlılık sağla ve tekrarları kaldır
        parsed_values = sorted(set(parsed_values))
        logging.info(f"İşlenmiş DNS TXT verileri: {domain} -> {parsed_values}")

    except requests.RequestException as e:
        logging.error(f"TXT kayıtları alınırken hata: {domain} -> {e}")
        parsed_values = []

    # Önbelleğe kaydet
    cache[domain] = parsed_values
    return parsed_values


def search_services(txt_records, json_file="result_1000.json"):
    """TXT kayıtlarını JSON dosyasındaki servislerle eşleştirir."""
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        logging.error(f"JSON dosyası bulunamadı: {json_file}")
        return []
    except json.JSONDecodeError as e:
        logging.error(f"JSON dosyası hatalı: {e}")
        return []

    found_services = []

    # Her bir TXT parçasını kontrol et
    for record in txt_records:
        norm_record = normalize(record)
        logging.debug(f"Normalleştirilmiş TXT parçası: {norm_record}")

        # JSON anahtarlarını tara
        for keyword in data.keys():
            norm_keyword = normalize(keyword)
            logging.debug(f"Kontrol: {norm_keyword} vs {norm_record}")
            # Tam eşleşme veya keyword'ün record içinde geçmesi
            if norm_keyword == norm_record or norm_keyword in norm_record:
                for service in data[keyword]:
                    found_services.append({
                        "Keyword": keyword,
                        "Service": service.get("Service", "Bilinmiyor"),
                        "Url": service.get("Url", ""),
                        "Icon": service.get("Icon", "")
                    })
                logging.debug(f"Eşleşme bulundu: {norm_keyword}")
            # Doğrulama token'ları için kısmi eşleşme (örneğin, "zoom" veya "zoom-domain-verification")
            elif "verify" in norm_record and any(part in norm_keyword for part in ["verify", "zoom"]):
                for service in data[keyword]:
                    if "zoom" in norm_keyword.lower():  # Zoom ile ilgili anahtarları hedefle
                        found_services.append({
                            "Keyword": keyword,
                            "Service": service.get("Service", "Bilinmiyor"),
                            "Url": service.get("Url", ""),
                            "Icon": service.get("Icon", "")
                        })
                        logging.debug(f"Kısmi eşleşme bulundu: {norm_keyword} -> {norm_record}")

    # Sonuçları Keyword'e göre sırala ve tekrarları kaldır
    found_services = list({v['Keyword']: v for v in found_services}.values())
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

        results = search_services(txt_records)

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
