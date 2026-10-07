import json
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Load routes
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTES_FILE = os.path.join(BASE_DIR, "routes.json")
routes = {}
if os.path.exists(ROUTES_FILE):
    with open(ROUTES_FILE, "r", encoding="utf-8") as f:
        routes = json.load(f)
else:
    print(f"ATTENTION : Le fichier de routage {ROUTES_FILE} est introuvable. Tous les paquets seront refusés.")

# Track progress of each packet in memory
# packet_id -> current_step (index in path array)
packet_states = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/scan", methods=["POST"])
def scan():
    data = request.json
    pc_id = str(data.get("pc_id"))
    packet_id = data.get("packet_id")
    packet_name = data.get("packet_name")
    
    if packet_id not in routes:
        # Fallback to name match in case routes.json was re-generated with new IDs
        found_id = None
        if packet_name:
            for r_id, r_info in routes.items():
                if r_info.get("name") == packet_name:
                    found_id = r_id
                    break
        
        if found_id:
            packet_id = found_id
        else:
            return jsonify({"status": "error", "message": "Paquet inconnu !", "details": "QR code non reconnu dans la base (ID incompatible)." })
    
    packet_info = routes[packet_id]
    path = packet_info["path"]
    
    # Initialize state if not present
    if packet_id not in packet_states:
        packet_states[packet_id] = -1 # Not dispatched yet
        
    current_step = packet_states[packet_id]
    
    # Scenario 1: Départ
    if pc_id == "Départ":
        packet_states[packet_id] = 0 # Now waiting for first node in path
        return jsonify({
            "status": "success",
            "message": f"Paquet envoyé ! Votre premier saut est le PC numéro : {path[0]}",
            "packet_name": packet_info["name"]
        })
        
    # Scenario 2: Arrivée
    if pc_id == "Arrivée":
        if current_step == len(path):
            packet_states[packet_id] = len(path) + 1 # Arrived !
            return jsonify({
                "status": "success",
                "message": f"Félicitations ! Le paquet est arrivé à destination.",
                "packet_name": packet_info["name"],
                "arrived": True
            })
        else:
            expected_pc = path[current_step] if 0 <= current_step < len(path) else "Départ"
            return jsonify({
                "status": "error",
                "message": "Erreur : Le paquet a sauté une étape !",
                "details": f"Veuillez vous rendre au prochain saut attendu : PC {expected_pc}."
            })
            
    # Scenario 3: Router PC (1 to 19)
    try:
        pc_id_int = int(pc_id)
    except ValueError:
        return jsonify({"status": "error", "message": "Identifiant PC invalide."})
        
    if current_step < 0:
        return jsonify({
            "status": "error",
            "message": "Erreur de routage : Ce paquet n'a pas encore quitté le poste Départ.",
            "details": "Veuillez vous rendre d'abord au poste 'Départ'."
        })
        
    if current_step >= len(path):
        return jsonify({
            "status": "error",
            "message": "Le paquet a déjà fini son trajet dans le réseau.",
            "details": "Rendez-vous à l'Arrivée pour le livrer."
        })
        
    # Check if the scanned PC is the EXPECTED next hop
    expected_pc = path[current_step]
    
    if pc_id_int == expected_pc:
        # Success! 
        current_step += 1
        packet_states[packet_id] = current_step
        
        # What is the next hop?
        if current_step < len(path):
            next_hop = path[current_step]
            return jsonify({
                "status": "success",
                "message": f"Bravo ! Votre prochain saut est : PC {next_hop}",
                "packet_name": packet_info["name"]
            })
        else:
            return jsonify({
                "status": "success",
                "message": "Dernier saut validé !",
                "details": "Allez livrer le paquet au poste 'Arrivée'.",
                "packet_name": packet_info["name"]
            })
    else:
        # Error: wrong path
        return jsonify({
            "status": "error",
            "message": f"Erreur de Routage ! Vous deviez aller au PC {expected_pc}.",
            "details": f"Paquet mal aiguillé. Retournez au PC {expected_pc}."
        })

if __name__ == "__main__":
    # Load routes on startup to ensure no crash
    print(f"Loaded {len(routes)} routes.")
    app.run(host="10.31.25.81", port=5000, debug=True, ssl_context="adhoc")
