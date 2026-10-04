import qrcode
import json
import random
import uuid
import os

ROUTERS_COUNT = 15
# Les ordinateurs sont numerotés de 1 à 15

MEALS = {
    "Burger": ["Pain Supérieur", "Salade", "Tomate", "Viande", "Pain Inférieur"],
    "Pizza": ["Pâte", "Sauce Tomate", "Fromage", "Olives", "Jambon"],
    "Tacos": ["Galette", "Frites", "Viande Hachée", "Sauce Fromagère", "Salade"],
    "Sushi": ["Riz", "Algue Nori", "Saumon", "Avocat", "Sauce Soja"]
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "qrs")
ROUTES_FILE = os.path.join(BASE_DIR, "routes.json")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

routes = {}

print("Génération des paquets et des chemins...")

for meal_name, parts in MEALS.items():
    meal_dir = os.path.join(OUTPUT_DIR, meal_name)
    if not os.path.exists(meal_dir):
        os.makedirs(meal_dir)
        
    for part in parts:
        packet_id = str(uuid.uuid4())[:8] # Un identifiant court de 8 caractères
        packet_full_name = f"{meal_name} - {part}"
        
        # Generation du chemin (4 sauts distincts + Arrivée)
        # On choisit 4 PCs au hasard parmi les 19 sans doublon
        PCs = list(range(1, ROUTERS_COUNT + 1))
        random.shuffle(PCs)
        path = PCs[:4]
        
        package_info = {
            "name": packet_full_name,
            "meal": meal_name,
            "part": part,
            "path": path, # Ex: [4, 15, 2, 19]
            "destination": "Arrivée"
        }
        
        routes[packet_id] = package_info
        
        # Création du QR Code
        # On insère les métadonnées de base dans le QR code pour la lecture côté client
        qr_data = json.dumps({"id": packet_id, "name": packet_full_name})
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        file_path = os.path.join(meal_dir, f"{part}_{packet_id}.png")
        img.save(file_path)
        print(f"Créé : {file_path} avec le chemin {path}")

with open(ROUTES_FILE, "w", encoding="utf-8") as f:
    json.dump(routes, f, ensure_ascii=False, indent=4)

print(f"\nTous les QR codes ont été générés dans '{OUTPUT_DIR}'.")
print(f"Fichier de routage '{ROUTES_FILE}' sauvegardé avec succès.")
