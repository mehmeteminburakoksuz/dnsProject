import requests
import socket
import json

# **Genişletilmiş Bulut Servisleri Listesi**
cloud_services = {
    "IaaS": [
        "Amazon AWS", "Google Cloud", "Microsoft Azure", "IBM Cloud", "Oracle Cloud", "DigitalOcean", "Linode",
        "Alibaba Cloud", "Hetzner", "OVH", "Rackspace", "Vultr"
    ],
    "PaaS": [
        "Heroku", "Netlify", "Vercel", "Render", "Firebase", "Fly.io", "Cloudflare Pages",
        "Railway", "Supabase", "App Engine", "OpenShift", "Kinsta"
    ],
    "SaaS": [
        "Google Analytics", "HubSpot", "Salesforce", "Shopify", "Stripe", "Mailchimp",
        "Intercom", "Zendesk", "Tawk.to", "Hotjar", "Plausible Analytics", "Segment",
        "SendGrid", "Twilio", "Cloudinary", "Algolia", "New Relic"
    ]
}

# **Servislerin Anahtar Kelimeleri veya Alan Adları**
service_identifiers = {
    "Amazon AWS": ["amazonaws.com", "s3.amazonaws.com", "ec2", "cloudfront.net"],
    "Google Cloud": ["gcp", "googleapis.com", "storage.googleapis.com", "compute.googleapis.com"],
    "Microsoft Azure": ["azure.com", "cloudapp.net", "azureedge.net", "blob.core.windows.net"],
    "IBM Cloud": ["cloud.ibm.com", "objectstorage.softlayer.net"],
    "Oracle Cloud": ["oraclecloud.com", "objectstorage.oraclecloud.com"],
    "DigitalOcean": ["digitalocean.com", "do.co", "spaces.nyc3.digitaloceanspaces.com"],
    "Linode": ["linode.com", "linodeobjects.com"],
    "Alibaba Cloud": ["aliyuncs.com", "alibabacloud.com"],
    "Hetzner": ["hetzner.com"],
    "OVH": ["ovh.com"],
    "Rackspace": ["rackcdn.com"],
    "Vultr": ["vultr.com"],

    "Heroku": ["herokuapp.com"],
    "Netlify": ["netlify.app", "netlify.com"],
    "Vercel": ["vercel.app", "vercel.com"],
    "Firebase": ["firebaseio.com", "firebasestorage.googleapis.com"],
    "Cloudflare": ["cloudflare.com", "cdn-cgi"],
    "Railway": ["railway.app"],
    "Supabase": ["supabase.co"],

    "Google Analytics": ["google-analytics.com", "analytics.js"],
    "HubSpot": ["hubspot.com"],
    "Salesforce": ["salesforce.com"],
    "Shopify": ["myshopify.com"],
    "Stripe": ["stripe.com"],
    "Mailchimp": ["list-manage.com"],
    "Intercom": ["intercom.io"],
    "Zendesk": ["zendesk.com"],
    "Tawk.to": ["tawk.to"],
    "Hotjar": ["hotjar.com"],
    "Plausible Analytics": ["plausible.io"],
    "Segment": ["segment.com"],
    "SendGrid": ["sendgrid.net"],
    "Twilio": ["twilio.com"],
    "Cloudinary": ["cloudinary.com"],
    "Algolia": ["algolia.net"],
    "New Relic": ["newrelic.com"]
}


def get_dns_records(domain):
    """DNS kayıtlarını alır ve IP adresini döndürür"""
    try:
        ip_address = socket.gethostbyname(domain)
        return ip_address
    except socket.gaierror:
        return None


def check_services(url):
    """Web sitesinde hangi servislerin kullanıldığını kontrol eder"""
    found_services = {"IaaS": [], "PaaS": [], "SaaS": []}

    try:
        response = requests.get(url, timeout=5)
        content = response.text
        headers = response.headers
        ip_address = get_dns_records(url.replace("https://", "").replace("http://", "").split("/")[0])

        # İçerik, başlıklar ve IP adresinde servisleri ara
        for service, patterns in service_identifiers.items():
            if any(pattern in content for pattern in patterns) or any(
                    pattern in headers.values() for pattern in patterns):
                for category, services in cloud_services.items():
                    if service in services:
                        found_services[category].append(service)

            # DNS/IP analizinde servis tespiti
            if ip_address:
                if "amazonaws.com" in ip_address:
                    found_services["IaaS"].append("Amazon AWS")
                elif "googleusercontent.com" in ip_address:
                    found_services["IaaS"].append("Google Cloud")
                elif "azure" in ip_address:
                    found_services["IaaS"].append("Microsoft Azure")

    except requests.RequestException:
        return {"error": "Web sitesine ulaşılamadı"}

    return found_services


# Kullanıcıdan URL al
website = input("Analiz edilecek siteyi girin (https://example.com): ")
result = check_services(website)

# Sonuçları JSON olarak yazdır
print(json.dumps(result, indent=4, ensure_ascii=False))
