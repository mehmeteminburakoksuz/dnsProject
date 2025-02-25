import subprocess

# Sahiplik doğrulaması için yaygın anahtar kelimeler
verification_keywords = {

    "google": [
        "google-site-verification",
        "google.com",
        "google-gws-recovery-domain-verification",
        "_spf.google.com",
        "_netblocks.google.com",
        "_netblocks2.google.com",
        "_netblocks3.google.com",
        "aspmx.googlemail.com"
        # vs. google ile ilgili yakalamak istediğiniz diğer kayıtlar
    ],
    "facebook": [
        "facebook-domain-verification",
        "facebookmail.com",
        "_spf.fb.com"
    ],
    "amazon": [
        "amazonses.com",
        "amazonses:",  # amazonses:<token> şeklinde başlayanlar
        "spf1.amazon.com",
        "spf2.amazon.com",
        "amazon.com"
    ],
    "apple": [
        "apple-domain-verification",
        "_spf.apple.com",
        "_spf-txn.apple.com"
    ],
    "microsoft": [
        "MS",
        "ms",
        "msfpkey",
        "spf.protection.outlook.com",
        "spf-a.hotmail.com",
        "spf-b.hotmail.com",
        "spf-c.hotmail.com",
        "spf-d.hotmail.com",
        "spfa.microsoftonline.com",
        "spf-mfa.microsoftonline.com",
        # vb. Microsoft/Outlook/Hotmail/Office 365 eşleşmeleri
    ],
    "cisco": [
        "cisco-ci-domain-verification",
        "ciscocidomainverification",
        "intersight"  # Cisco Intersight
        # vb. cisco ile ilgili
    ],
    "onetrust": [
        "onetrust-domain-verification"
    ],
    "zoom": [
        "zoom-domain-verification",
        "Zoom"  # (eğer bu şekilde geçenleri de Zoom’a atamak isterseniz)
    ],
    "docusign": [
        "docusign"
    ],
    "autodesk": [
        "autodesk-domain-verification"
    ],
    "stripe": [
        "stripe-verification"
    ],
    "pardot": [
        # Pardot kayıtları: "pardotXXXXXX" gibi geçenleri yakalamak isterseniz
        "pardot"
    ],
    "canva": [
        "canva-site-verification"
    ],
    "uber": [
        "uber-domain-verification"
    ],
    "liveramp": [
        "liveramp-site-verification"
    ],
    "pendo": [
        "pendo-domain-verification"
    ],
    "adobe": [
        "adobe-sign-verification",
        "adobe-idp-site-verification",
        "_github-challenge-adobe"
    ],
    "mixpanel": [
        "mixpanel-domain-verify"
    ],
    "slack": [
        "slack-domain-verification"
    ],
    "twitter": [
        "_thirdparty.twitter.com"
    ],
    "loom": [
        "loom-site-verification",
        "loom-verification"
    ],
    "miro": [
        "miro-verification"
    ],
    "dropbox": [
        "dropbox-domain-verification"
    ],
    "atlassian": [
        "atlassian-domain-verification",
        "atlassian-sending-domain-verification"
    ],
    "box": [
        "box-domain-verification"
    ],
    "wrike": [
        "wrike-verification"
    ],
    "sprig": [
        "sprig-site-verification"
    ],
    "paypal": [
        "pp._spf.paypal.com",
        "3ph1._spf.paypal.com",
        "3ph2._spf.paypal.com",
        "3ph3._spf.paypal.com",
        "3ph4._spf.paypal.com"
    ],
    "1password": [
        "1password-site-verification"
    ],
    "twilio": [
        "twilio-domain-verification"
    ],
    "zapier": [
        "zapier-domain-verification-challenge"
    ],
    "docker": [
        "docker-verification"
    ],
    "mongodb": [
        "mongodb-site-verification"
    ],
    "jamf": [
        "jamf-site-verification"
    ],
    "paloaltonetworks": [
        "paloaltonetworks-site-verification"
    ],
    "yahoo": [
        "yahoo-verification-key"
    ],
    "notion": [
        "notion-domain-verification"
    ],
    "pinterest": [
        "pinterest-site-verification"
    ],
    "logmein": [
        "logmein-verification-code"
    ],
    "datadome": [
        "datadome-domain-verify"
    ],
    "spycloud": [
        "spycloud-domain-verification"
    ],
    "bugcrowd": [
        "bugcrowd-verification"
    ],
    "postman": [
        "postman-domain-verification"
    ],
    "mailgun": [
        "mailgun.org"
    ],
    "happeo": [
        "happeo-site-verification"
    ],
    "openai": [
        "openai-domain-verification"
    ],
    "github": [
        "github-verification",
        "_github-challenge-"
        # vb. GitHub ile ilgili bir şey yakalamak isterseniz
    ],
    "segment": [
        "segment-site-verification"
    ],
    "citrix": [
        "citrix-verification-code"
    ],
    "wiz": [
        "wiz-domain-verification"
    ],
    "knowbe4": [
        "knowbe4-site-verification"
    ],
    "brave": [
        "brave-ledger-verification"
    ],
    "successfactors": [
        "successfactors-site-verification"
    ],
    "cloudhealth": [
        "cloudhealth"
    ],
    "monday": [
        "monday-com-verification"
    ],
    "lucid": [
        "lucid-verification"
    ],
    "teamviewer": [
        "teamviewer-sso-verification"
    ],
    "anodot": [
        "anodot-domain-verification"
    ],
    "rippling": [
        "rippling-domain-verification"
    ],
    "zendesk": [
        "mail.zendesk.com",
        "smtp.zendesk.com",
        "_spf.zdsys.com",
        "support.zendesk.com",
        "zendeskverification"
    ],
    "coda": [
        "coda-verification"
    ],
    "gentrace": [
        "gentrace-domain-verification"
    ],
    "astro": [
        "astro-domain-verification"
    ],
    "northpass": [
        "northpass-domain-verification"
    ],
    "shopify": [
        "shopify-verification-code",
        "shops.shopify.com"
    ],
    "wework": [
        "wework-site-verification"
    ],
    "meltwater": [
        "meltwater-domain-verification"
    ],

}


def get_txt_records(domain):
    """TXT kayıtlarını almak için dig komutunu çalıştırır."""
    try:
        result = subprocess.run(['dig', domain, 'TXT'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return result.stdout.decode('utf-8').splitlines()  # Sonuçları satır satır döndür
        else:
            return f"Error: {result.stderr.decode('utf-8')}"  # Hata mesajını döndür
    except Exception as e:
        return f"An error occurred: {str(e)}"


def verify_ownership(txt_records):
    """TXT kayıtlarında site sahipliği doğrulama anahtarlarını arar."""
    verified_platforms = []

    # TXT kayıtlarındaki her bir kaydı kontrol et
    for platform, keywords in verification_keywords.items():
        for keyword in keywords:
            for record in txt_records:
                if isinstance(record, str) and keyword.lower() in record.lower():
                    verified_platforms.append(platform)
                    break  # Aynı platformu birden fazla eklememek için döngüyü kır

    return verified_platforms


# Kullanıcıdan domain girişi al
domain = input("Enter the domain: ")

# TXT kayıtlarını al
txt_records = get_txt_records(domain)

# Sahiplik doğrulaması yapan platformları tespit et
verified_platforms = verify_ownership(txt_records)

# Sonuçları ekrana yazdır
if verified_platforms:
    print("Ownership verification detected for the following platforms:")
    for platform in verified_platforms:
        print(f"- {platform}")
else:
    print("No ownership verification detected in the TXT records.")
