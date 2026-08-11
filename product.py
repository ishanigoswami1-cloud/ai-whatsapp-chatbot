import requests
import os
from dotenv import load_dotenv

load_dotenv()

DOCTOR_FRESH_API_URL = os.getenv("DOCTOR_FRESH_API_URL")
DOCTOR_FRESH_API_KEY = os.getenv("DOCTOR_FRESH_API_KEY")

OTHER_BRAND_PRODUCTS = [
    {
        "id": "KE001",
        "name": "Kent Grand Plus 8L",
        "brand": "Kent",
        "price": 14500,
        "technology": "RO+UV+UF+TDS Controller",
        "capacity": "8 Litre",
        "suitable_tds": "up to 2000 ppm",
        "best_for": "High TDS borewell water",
        "warranty": "1 year + 3 year free service",
        "highlight": "Popular brand, good after-sales service",
        "is_priority": False
    },
    {
        "id": "AQ001",
        "name": "Aquaguard Delight 7L",
        "brand": "Aquaguard",
        "price": 12000,
        "technology": "RO+UV+MTDS",
        "capacity": "7 Litre",
        "suitable_tds": "up to 2000 ppm",
        "best_for": "Urban tap water",
        "warranty": "1 year",
        "highlight": "Trusted brand, widespread service network",
        "is_priority": False
    },
    {
        "id": "PU001",
        "name": "Pureit Eco Water Saver 10L",
        "brand": "Pureit",
        "price": 9500,
        "technology": "RO+UV+MF",
        "capacity": "10 Litre",
        "suitable_tds": "up to 1800 ppm",
        "best_for": "Low to medium TDS areas",
        "warranty": "1 year",
        "highlight": "Good water recovery rate, eco-friendly",
        "is_priority": False
    },
]


def get_doctor_fresh_products() -> list:
    try:
        headers = {}
        if DOCTOR_FRESH_API_KEY:
            headers["Authorization"] = f"Bearer {DOCTOR_FRESH_API_KEY}"

        response = requests.get(DOCTOR_FRESH_API_URL, headers=headers, timeout=5)
        response.raise_for_status()
        api_data = response.json()

        products = []
        for item in api_data:
            name = item.get("products_title", "")
            price = float(item.get("sale_price", 0) or 0)
            url = item.get("url", "")

            products.append({
                "id":           item.get("id", ""),
                "name":         name,
                "brand":        "Doctor Fresh",
                "price":        price,
                "url":          url,
                "technology":   "",   # API mein nahi hai, bot naam se samjhega
                "capacity":     "",
                "suitable_tds": "",
                "best_for":     "",
                "warranty":     "1 year",
                "highlight":    "Doctor Fresh premium quality",
                "is_priority":  True
            })
        return products

    except Exception as e:
        print(f"⚠️  Doctor Fresh API error: {e}")
        return []


def get_products() -> list:
    doctor_fresh = get_doctor_fresh_products()
    return doctor_fresh + OTHER_BRAND_PRODUCTS