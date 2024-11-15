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


@app.route("/", methods=['GET'])
def home():
    """
    Route de bienvenue pour le service utilisateur.
    """
    return '<body style="background-color: #2c2c2c; color: #e0e0e0; font-family: Arial, sans-serif; display: flex;flex-direction: column;justify-content: center;align-items: center;height: 100vh;margin: 0;"><h1 style="font-size: 2em;color: #f0f0f0;">Bienvenue sur le composant <span style="color: #1e90ff">User</span><span style="margin-left: 10px;">🎉</span></h1></body>'


@app.route("/users", methods=['GET'])
def get_users():
    """
    Récupère la liste de tous les utilisateurs.
    """
    return make_response(jsonify(users), 200)


@app.route("/users/<id>", methods=['GET'])
def get_user(id):
    """
    Récupère les détails d'un utilisateur par son ID.
    """
    for user in users:
        if user['id'] == id:
            return make_response(jsonify(user), 200)
    return make_response(jsonify({"error": "User not found for id '" + id + "'"}), 404)


@app.route("/users/<id>", methods=['POST'])
def create_user(id):
    """
    Crée un nouvel utilisateur avec l'ID spécifié.
    """
    req = request.get_json()
    for user in users:
        if str(user["id"]) == str(id):
            return make_response(jsonify({"error": "User ID already exists"}), 409)
    users.append(req)
    write(users)  # Sauvegarde des utilisateurs
    return make_response(jsonify({"message": "User added"}), 200)


def write(users):
    """
    Écrit la liste des utilisateurs dans le fichier JSON.
    """
    with open(json_file_path, "w") as f:
        json.dump({"users": users}, f)


@app.route("/users/<id>/update_lastactive", methods=['PUT'])
def update_user_lastactive(id):
    """
    Met à jour le timestamp de la dernière activité de l'utilisateur.
    """
    for user in users:
        if str(user["id"]) == str(id):
            user["last_active"] = round(time.time())
            write(users)  # Sauvegarde des changements
            return make_response(jsonify(user), 200)
    return make_response(jsonify({"error": "User not found"}), 404)


@app.route("/users/<id>/update_name", methods=['PUT'])
def update_user_name(id):
    """
    Met à jour le nom de l'utilisateur spécifié par son ID.
    """
    if request.args:
        name = request.args.get("name")
        if name is None:
            return make_response(jsonify({"error": "Name not provided"}), 400)
        for user in users:
            if str(user["id"]) == str(id):
                user["name"] = name
                write(users)  # Sauvegarde des changements
                return make_response(jsonify(user), 200)
    return make_response(jsonify({"error": "User not found or name not provided"}), 404)


@app.route("/users/<id>/bookings", methods=['GET'])
def get_user_bookings(id):
    """
    Récupère les réservations de l'utilisateur à partir du service Booking via gRPC.
    """
    with grpc.insecure_channel('localhost:3201') as channel:
        stub = booking_pb2_grpc.BookingServiceStub(channel)
        
        # Préparation de la requête gRPC
        request = booking_pb2.GetBookingByUserRequest(userid=id)

        # Exécution de l'appel gRPC
        try:
            response = stub.GetBookingByUser(request)
            bookings = {
                "userid": response.booking.userid,
                "dates": [{"date": date.date, "movies": [movie.id for movie in date.movies]} for date in response.booking.dates]
            }
            return jsonify(bookings)
        except grpc.RpcError as e:
            return make_response(jsonify({"error": e.details()}), e.code())


@app.route("/users/<id>/detailed_bookings", methods=['GET'])
def get_user_detailed_bookings(id):
    """
    Récupère les réservations détaillées de l'utilisateur, y compris les détails des films.
    """
    bookings = get_user_bookings(id)
    
    if bookings.status_code != 200:
        return bookings  # Si une erreur est retournée par la requête REST
    
    # Vérification des données reçues
    bookings_json = bookings.get_json()

    if not bookings_json or bookings_json.get("userid") != id:
        return make_response(jsonify({"error": f"No bookings found for user {id}"}), 404)
    
    # Récupération des réservations pour l'utilisateur
    user_bookings = bookings_json.get("dates", [])
    
    if not user_bookings:
        return make_response(jsonify({"error": f"No bookings found for user {id}"}), 404)
    
    # Log des réservations trouvées
    print(f"User {id} bookings:", user_bookings)
    
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
            response = requests.post('http://localhost:3001/graphql', json={'query': query})         
            
            if response.status_code == 200:
                movie_data = response.json().get('data', {}).get('movie_with_id')
                if movie_data:
                    # Ajouter les détails du film à la réservation
                    booking_details["movies"].append(movie_data)
        
        # Ajouter les détails de la réservation à la liste
        detailed_bookings.append(booking_details)
    
    # Mise à jour de la dernière visite
    update_user_lastactive(id)
    
    return make_response(jsonify({id: detailed_bookings}), 200)


if __name__ == "__main__":
    print("Server running on port %s" % (PORT))
    app.run(host=HOST, port=PORT)  # Lancement du serveur Flask
