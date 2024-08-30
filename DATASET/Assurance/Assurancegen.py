import json
import random
import os
from jsonschema import validate, ValidationError
from collections import Counter

# Define product names, target audiences, and formulas for ASSURANCE products
product_names = [
    "Assurance Vie", "Assurance Habitation", "Assurance Auto", "Assurance Santé", "Assurance Voyage",
    "Assurance Prévoyance", "Assurance Emprunteur", "Assurance Scolaire", "Assurance Animaux", "Assurance Mobilité"
]

target_audiences = [
    "Particuliers", "Professionnels", "Familles", "Jeunes", "Seniors"
]

formulas = [
    {
        "name": "Formule Basic",
        "price": "500 DH TTC/AN",
        "features": [
            "Couverture de base",
            "Assistance 24/7",
            "Gestion en ligne"
        ]
    },
    {
        "name": "Formule Confort",
        "price": "1000 DH TTC/AN",
        "features": [
            "Couverture étendue",
            "Assistance VIP",
            "Service client dédié"
        ]
    },
    {
        "name": "Formule Premium",
        "price": "1500 DH TTC/AN",
        "features": [
            "Couverture complète",
            "Accès à des services exclusifs",
            "Indemnisation rapide"
        ]
    },
    {
        "name": "Formule Eco",
        "price": "750 DH TTC/AN",
        "features": [
            "Couverture économique",
            "Gestion en ligne",
            "Assistance téléphonique"
        ]
    },
    {
        "name": "Formule Plus",
        "price": "1250 DH TTC/AN",
        "features": [
            "Couverture étendue",
            "Service client prioritaire",
            "Options de personnalisation"
        ]
    }
]

# Generate mock assurance products
products = []

for i in range(10):
    product = {
        "productId": f"A{i+1:03}",
        "productType": "ASSURANCE",
        "productName": random.choice(product_names),
        "productTarget": [
            random.choice(target_audiences)
        ],
        "productDetails": {
            "formulas": random.sample(formulas, k=2)  # Select 2 random formulas
        }
    }
    products.append(product)

# Directory path
directory_path = "D:\\2ia projects\\Stage 2a\\DATASET\\ASSURANCE"

# Create the directory if it doesn't exist
os.makedirs(directory_path, exist_ok=True)

# File path
file_path = os.path.join(directory_path, "sample_assurance_products.json")

# Save the products list to a JSON file
with open(file_path, "w", encoding="utf-8") as file:
    json.dump(products, file, ensure_ascii=False, indent=4)

print(f"Sample assurance products JSON file has been saved to {file_path}")

# JSON Schema for validation
schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "productId": {"type": "string"},
            "productType": {"type": "string"},
            "productName": {"type": "string"},
            "productTarget": {
                "type": "array",
                "items": {"type": "string"}
            },
            "productDetails": {
                "type": "object",
                "properties": {
                    "formulas": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "price": {"type": "string"},
                                "features": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                }
                            },
                            "required": ["name", "price", "features"]
                        }
                    }
                },
                "required": ["formulas"]
            }
        },
        "required": ["productId", "productType", "productName", "productTarget", "productDetails"]
    }
}

# Load JSON data from the file
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Validate JSON structure
try:
    validate(instance=data, schema=schema)
    print("JSON structure is valid.")
except ValidationError as e:
    print(f"JSON structure is invalid: {e.message}")

# Check data consistency and uniqueness
product_ids = set()
unique = True
for product in data:
    if product["productId"] in product_ids:
        unique = False
        print(f"Duplicate productId found: {product['productId']}")
    else:
        product_ids.add(product["productId"])
    # Check logical ranges (example)
    try:
        price = int(product["productDetails"]["formulas"][0]["price"].split()[0])
        if not (0 <= price <= 10000):
            print(f"Unreasonable price found: {product['productId']} - {price}")
    except ValueError:
        print(f"Invalid price format: {product['productId']} - {product['productDetails']['formulas'][0]['price']}")

if unique:
    print("All product IDs are unique.")

# Analyze data distribution
product_names = [product["productName"] for product in data]
name_distribution = Counter(product_names)
print("Product name distribution:")
for name, count in name_distribution.items():
    print(f"{name}: {count}")

# Check a sample entry
print("\nSample product entry:")
print(json.dumps(data[0], indent=4, ensure_ascii=False))
