import json
import random
import os

product_names = [
    "Carte Premium", "Carte Gold", "Carte Silver", "Carte Platinum", "Carte Diamond",
    "Carte Business", "Carte Corporate", "Carte Student", "Carte Family", "Carte Travel",
    "Carte Cashback", "Carte Rewards", "Carte Basic", "Carte Elite", "Carte Classic"
]

target_audiences = [
    "Clients Privilège Particuliers et Professionnels, détenteurs d’un compte chéques.",
    "Entreprises et Professionnels, détenteurs d’un compte commercial.",
    "Jeunes et étudiants, détenteurs d’un compte jeunesse.",
    "Familles et individus, détenteurs d’un compte commun.",
    "Voyageurs fréquents, détenteurs d’un compte international."
]

pricing_contributions = [
    "1 450 DH TTC/an", "1 200 DH TTC/an", "1 700 DH TTC/an", "2 000 DH TTC/an", "1 000 DH TTC/an",
    "1 500 DH TTC/an", "1 600 DH TTC/an", "1 800 DH TTC/an", "2 100 DH TTC/an", "1 250 DH TTC/an",
    "1 350 DH TTC/an", "1 550 DH TTC/an", "1 900 DH TTC/an", "2 200 DH TTC/an", "1 300 DH TTC/an"
]

extra_costs = [
    [
        "Frais de retrait GAB à l’étranger : 2% du montant de la transaction* + équivalent de 1$",
        "Frais de retrait GAB confrère au Maroc: 6 DH TTC*",
        "Commission sur paiement international: 1% du montant * + 10 DH HT*",
        "Frais de remplacement : 50 DH HT*",
        "Recalcul de code : Gratuit"
    ],
    [
        "Frais de retrait GAB à l’étranger : 2.5% du montant de la transaction* + équivalent de 1.5$",
        "Frais de retrait GAB confrère au Maroc: 5 DH TTC*",
        "Commission sur paiement international: 0.5% du montant * + 15 DH HT*",
        "Frais de remplacement : 45 DH HT*",
        "Recalcul de code : 10 DH"
    ],
    # Add more variations as needed
]

characteristics_list = [
    [
        {
            "title": "Plafonds de retraits et de paiement Carte Visa",
            "detail": {
                "head": ["Retrait Quotidien", "Paiement Mensuel"],
                "content": ["30.000 DH/jour à hauteur du solde du compte", "Jusqu'à 200 000 DH"]
            }
        },
        {
            "title": "Facilité de caisse",
            "detail": {
                "head": ["Plafonds"],
                "content": ["0 – 10 000 – 20 000 – 30 000 – 40 000 – 50 000 - 60 000 - 70 000 - 80 000 DH Sur le compte en DH"]
            }
        },
        {
            "title": "Personnalisation des services monétiques",
            "detail": {
                "head": ["Services monétiques"],
                "content": [
                    "Suspendre l'utilisation de sa carte ",
                    "Suspendre l'utilisation de sa carte pour le paiement et/ou le retrait, au Maroc et/ou à l’étranger ",
                    "Suspendre l'utilisation de sa carte pour le dépôt d’espèces sur guichet et le cash express automatique au Maroc ",
                    "Modifier les plafonds de retrait et de paiement au Maroc et à l’étranger à hauteur du plafond spécifique de la carte"
                ]
            }
        },
        {
            "title": "SERVICES GAB / E-BANKING",
            "detail": {
                "head": ["Liste des services"],
                "content": [
                    "Consultation du solde (local & international) ",
                    "Edition du relevé des 10 dernières opérations (local) ",
                    "Changement du code PIN",
                    "Paiement de factures IAM, Orange",
                    "Recharge téléphonique IAM, Orange, Inwi",
                    "Édition RIB ",
                    "Changement de code PIN ",
                    "Dépôt espèces (sur certains GAB) ",
                    "Remise chèques (sur certains GAB) "
                ]
            }
        }
    ],
    # Add more characteristic variations as needed
]

products = []

for i in range(15):
    product = {
        "productId": f"{i+1:03}",
        "productType": "CARTE",
        "productName": random.choice(product_names),
        "productTarget": [
            random.choice(target_audiences)
        ],
        "productDetails": {
            "pricing": {
                "contribution": random.choice(pricing_contributions),
                "extraCosts": random.choice(extra_costs)
            },
            "characteristics": random.choice(characteristics_list)
        }
    }
    products.append(product)

# Directory path
directory_path = "D:\\2ia projects\\Stage 2a\\DATASET\\CARTE"

# Create the directory if it doesn't exist
os.makedirs(directory_path, exist_ok=True)

# File path
file_path = os.path.join(directory_path, "sample_products.json")

# Save the products list to a JSON file
with open(file_path, "w", encoding="utf-8") as file:
    json.dump(products, file, ensure_ascii=False, indent=4)

print(f"Sample products JSON file has been saved to {file_path}")
