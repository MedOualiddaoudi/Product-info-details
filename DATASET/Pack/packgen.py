import json
import random
import os
from jsonschema import validate, ValidationError
from collections import Counter

product_names = [
    "Pack Privilége MRE", "Pack Gold", "Pack Silver", "Pack Platinum", "Pack Diamond",
    "Pack Business", "Pack Corporate", "Pack Student", "Pack Family", "Pack Travel",
    "Pack Cashback", "Pack Rewards", "Pack Basic", "Pack Elite", "Pack Classic"
]

target_audiences = [
    "Clients Marocains résidants à l'étranger",
    "Entreprises et Professionnels, détenteurs d’un compte commercial.",
    "Jeunes et étudiants, détenteurs d’un compte jeunesse.",
    "Familles et individus, détenteurs d’un compte commun.",
    "Voyageurs fréquents, détenteurs d’un compte international."
]

formulas = [
    {
        "name": "Formule 1",
        "price": "100 DH TTC/AN",
        "features": [
            "Un compte chèque MRE avec frais de tenue de compte gratuits",
            "Une Carte Bancaire locale Premium contactless vous permettant d’accéder à un large réseau de guichets automatiques et commerçant",
            "Le Service Attijarinet Attijari mobile"
        ]
    },
    {
        "name": "Formule 2",
        "price": "50 DH TTC/AN",
        "features": [
            "Services GAB inclus",
            "Services LSB",
            {
                "Conditions préférentielles": [
                    "gratuité des frais de tenue de compte",
                    "gratuité des frais de virements et des frais des retraits déplacés",
                    "50% de réduction sur les frais des mises à disposition"
                ]
            }
        ]
    },
    {
        "name": "Formule 3",
        "price": "200 DH TTC/AN",
        "features": [
            "Un compte épargne avec frais de tenue de compte réduits",
            "Carte Bancaire Gold avec accès aux salons VIP",
            "Assistance voyage et assurance"
        ]
    },
    {
        "name": "Formule 4",
        "price": "75 DH TTC/AN",
        "features": [
            "Compte courant avec découvert autorisé",
            "Carte Bancaire contactless",
            "Notifications SMS pour chaque transaction"
        ]
    },
    {
        "name": "Formule 5",
        "price": "150 DH TTC/AN",
        "features": [
            "Compte joint avec frais de tenue de compte gratuits",
            "Carte Bancaire Platinum avec cashback sur les achats",
            "Service client dédié 24/7"
        ]
    },
    {
        "name": "Formule 6",
        "price": "300 DH TTC/AN",
        "features": [
            "Compte investissement avec conseils personnalisés",
            "Carte Bancaire Diamond avec assurances incluses",
            "Accès privilégié aux événements exclusifs"
        ]
    },
    {
        "name": "Formule 7",
        "price": "120 DH TTC/AN",
        "features": [
            "Compte jeune avec offres spéciales pour étudiants",
            "Carte Bancaire sans frais de retrait",
            "Programme de fidélité avec récompenses"
        ]
    },
    {
        "name": "Formule 8",
        "price": "90 DH TTC/AN",
        "features": [
            "Compte courant avec gestion en ligne",
            "Carte Bancaire avec limite de retrait ajustable",
            "Service de notifications push"
        ]
    }
]

products = []

for i in range(15):
    product = {
        "productId": f"{i+2:03}",  # Start from 002 to avoid conflict with the first product
        "productType": "PACK",
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
directory_path = r"D:\2ia projects\Stage 2a\DATASET\Pack"

# Create the directory if it doesn't exist
os.makedirs(directory_path, exist_ok=True)

# File path
file_path = os.path.join(directory_path, "sample_pack_products.json")

# Save the products list to a JSON file
with open(file_path, "w", encoding="utf-8") as file:
    json.dump(products, file, ensure_ascii=False, indent=4)

print(f"Sample pack products JSON file has been saved to {file_path}")

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
                                        "oneOf": [
                                            {"type": "string"},
                                            {
                                                "type": "object",
                                                "properties": {
                                                    "Conditions préférentielles": {
                                                        "type": "array",
                                                        "items": {"type": "string"}
                                                    }
                                                },
                                                "required": ["Conditions préférentielles"]
                                            }
                                        ]
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
