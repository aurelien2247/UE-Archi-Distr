from concurrent import futures
import grpc 
import sys
sys.path.append('../booking')  # Ajout du chemin pour le module booking
import booking_pb2
import booking_pb2_grpc
import time
from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

# Initialisation de l'application Flask
app = Flask(__name__)

# Configuration du serveur
PORT = 3203
HOST = '0.0.0.0'

import os

# Obtenir le chemin du répertoire du script en cours
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construire le chemin du fichier JSON contenant les utilisateurs
json_file_path = os.path.join(script_dir, 'data', 'users.json')

# Vérification de l'existence du fichier
if not os.path.exists(json_file_path):
    raise FileNotFoundError(f"Le fichier {json_file_path} est introuvable.")

# Charger la base de données JSON des utilisateurs
with open(json_file_path, "r") as jsf:
    users = json.load(jsf)["users"]
    print(f"{len(users)} utilisateurs chargés depuis {json_file_path}")  # Debug: impression du nombre d'utilisateurs chargés


@app.route("/", methods=['GET'])
def home():
    """
    Route de bienvenue pour le service utilisateur.
    """
    print("Route / appelée")  # Debug: impression de la route appelée
    return '<body style="background-color: #2c2c2c; color: #e0e0e0; font-family: Arial, sans-serif; display: flex;flex-direction: column;justify-content: center;align-items: center;height: 100vh;margin: 0;"><h1 style="font-size: 2em;color: #f0f0f0;">Bienvenue sur le composant <span style="color: #1e90ff">User</span><span style="margin-left: 10px;">🎉</span></h1></body>'


@app.route("/users", methods=['GET'])
def get_users():
    """
    Récupère la liste de tous les utilisateurs.
    """
    print("Route /users appelée")  # Debug: impression de la route appelée
    return make_response(jsonify(users), 200)


@app.route("/users/<id>", methods=['GET'])
def get_user(id):
    """
    Récupère les détails d'un utilisateur par son ID.
    """
    print(f"Route /users/{id} appelée")  # Debug: impression de l'ID appelé
    for user in users:
        if user['id'] == id:
            print(f"Utilisateur trouvé: {user}")  # Debug: impression de l'utilisateur trouvé
            return make_response(jsonify(user), 200)
    print(f"Utilisateur non trouvé pour l'ID: {id}")  # Debug: impression si utilisateur non trouvé
    return make_response(jsonify({"error": "User not found for id '" + id + "'"}), 404)


@app.route("/users/<id>", methods=['POST'])
def create_user(id):
    """
    Crée un nouvel utilisateur avec l'ID spécifié.
    """
    req = request.get_json()
    print(f"Requête reçue pour création d'utilisateur avec ID {id}: {req}")  # Debug: impression des détails de la requête
    for user in users:
        if str(user["id"]) == str(id):
            print(f"Erreur: Utilisateur avec l'ID {id} existe déjà")  # Debug: utilisateur déjà existant
            return make_response(jsonify({"error": "User ID already exists"}), 409)
    users.append(req)
    write(users)  # Sauvegarde des utilisateurs
    print(f"Nouvel utilisateur ajouté avec succès: {req}")  # Debug: nouvel utilisateur ajouté
    return make_response(jsonify({"message": "User added"}), 200)


def write(users):
    """
    Écrit la liste des utilisateurs dans le fichier JSON.
    """
    print("Mise à jour du fichier JSON des utilisateurs")  # Debug: mise à jour du fichier JSON
    with open(json_file_path, "w") as f:
        json.dump({"users": users}, f)


@app.route("/users/<id>/update_lastactive", methods=['PUT'])
def update_user_lastactive(id):
    """
    Met à jour le timestamp de la dernière activité de l'utilisateur.
    """
    print(f"Route /users/{id}/update_lastactive appelée")  # Debug: impression de la route appelée
    for user in users:
        if str(user["id"]) == str(id):
            user["last_active"] = round(time.time())
            write(users)  # Sauvegarde des changements
            print(f"Utilisateur {id} - Dernière activité mise à jour")  # Debug: dernière activité mise à jour
            return make_response(jsonify(user), 200)
    print(f"Erreur: Utilisateur avec ID {id} non trouvé")  # Debug: utilisateur non trouvé
    return make_response(jsonify({"error": "User not found"}), 404)


@app.route("/users/<id>/update_name", methods=['PUT'])
def update_user_name(id):
    """
    Met à jour le nom de l'utilisateur spécifié par son ID.
    """
    print(f"Route /users/{id}/update_name appelée")  # Debug: impression de la route appelée
    if request.args:
        name = request.args.get("name")
        print(f"Requête pour changer le nom de l'utilisateur {id} en {name}")  # Debug: impression du nouveau nom
        if name is None:
            print("Erreur: Aucun nom fourni")  # Debug: erreur si aucun nom n'est fourni
            return make_response(jsonify({"error": "Name not provided"}), 400)
        for user in users:
            if str(user["id"]) == str(id):
                user["name"] = name
                write(users)  # Sauvegarde des changements
                print(f"Nom de l'utilisateur {id} mis à jour en {name}")  # Debug: nom mis à jour
                return make_response(jsonify(user), 200)
    print(f"Erreur: Utilisateur avec ID {id} non trouvé ou nom non fourni")  # Debug: utilisateur non trouvé ou nom manquant
    return make_response(jsonify({"error": "User not found or name not provided"}), 404)


@app.route("/users/<id>/bookings", methods=['GET'])
def get_user_bookings(id):
    """
    Récupère les réservations de l'utilisateur à partir du service Booking via gRPC.
    """
    print(f"Route /users/{id}/bookings appelée")  # Debug: impression de la route appelée
    with grpc.insecure_channel('localhost:3201') as channel:
        stub = booking_pb2_grpc.BookingServiceStub(channel)
        
        # Préparation de la requête gRPC
        request = booking_pb2.GetBookingByUserRequest(userid=id)
        print(f"Requête gRPC envoyée pour l'utilisateur {id}")  # Debug: impression de la requête gRPC envoyée

        # Exécution de l'appel gRPC
        try:
            response = stub.GetBookingByUser(request)
            bookings = {
                "userid": response.booking.userid,
                "dates": [{"date": date.date, "movies": [movie.id for movie in date.movies]} for date in response.booking.dates]
            }
            print(f"Réponse gRPC reçue pour l'utilisateur {id}: {bookings}")  # Debug: impression de la réponse gRPC
            return jsonify(bookings)
        except grpc.RpcError as e:
            print(f"Erreur gRPC: {e.details()}")  # Debug: impression de l'erreur gRPC
            return make_response(jsonify({"error": e.details()}), e.code())


@app.route("/users/<id>/detailed_bookings", methods=['GET'])
def get_user_detailed_bookings(id):
    """
    Récupère les réservations détaillées de l'utilisateur, y compris les détails des films.
    """
    print(f"Route /users/{id}/detailed_bookings appelée")  # Debug: impression de la route appelée
    bookings = get_user_bookings(id)
    
    if bookings.status_code != 200:
        print(f"Erreur lors de la récupération des réservations pour l'utilisateur {id}")  # Debug: erreur lors de la récupération
        return bookings  # Si une erreur est retournée par la requête REST
    
    # Vérification des données reçues
    bookings_json = bookings.get_json()

    if not bookings_json or bookings_json.get("userid") != id:
        print(f"Aucune réservation trouvée pour l'utilisateur {id}")  # Debug: impression si aucune réservation n'est trouvée
        return make_response(jsonify({"error": f"No bookings found for user {id}"}), 404)
    
    # Récupération des réservations pour l'utilisateur
    user_bookings = bookings_json.get("dates", [])
    
    if not user_bookings:
        print(f"Aucune réservation trouvée pour l'utilisateur {id}")  # Debug: aucune réservation trouvée
        return make_response(jsonify({"error": f"No bookings found for user {id}"}), 404)
    
    # Log des réservations trouvées
    print(f"Réservations trouvées pour l'utilisateur {id}: {user_bookings}")  # Debug: impression des réservations trouvées
    
    detailed_bookings = []
    for booking in user_bookings:
        booking_details = {
            "date": booking["date"],
            "movies": []
        }
        for movie_id in booking.get("movies", []):
            # Requête GraphQL pour récupérer les détails du film
            query = f"""
            {{
                movie_with_id(_id: "{movie_id}") {{
                    id
                    title
                    director
                    rating
                }}
            }}
            """
            print(f"Requête GraphQL envoyée pour le film {movie_id}")  # Debug: impression de la requête GraphQL
            response = requests.post('http://localhost:3001/graphql', json={'query': query})         
            
            if response.status_code == 200:
                movie_data = response.json().get('data', {}).get('movie_with_id')
                if movie_data:
                    # Ajouter les détails du film à la réservation
                    print(f"Détails du film {movie_id} reçus: {movie_data}")  # Debug: détails du film reçus
                    booking_details["movies"].append(movie_data)
        
        # Ajouter les détails de la réservation à la liste
        detailed_bookings.append(booking_details)
    
    # Mise à jour de la dernière visite
    update_user_lastactive(id)
    
    return make_response(jsonify({id: detailed_bookings}), 200)


if __name__ == "__main__":
    print("Server running on port %s" % (PORT))  # Debug: impression que le serveur démarre
    app.run(host=HOST, port=PORT)  # Lancement du serveur Flask
