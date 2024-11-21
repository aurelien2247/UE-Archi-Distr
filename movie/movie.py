from ariadne import graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, QueryType, MutationType
from flask import Flask, make_response, render_template, request, jsonify
import resolvers as r
import json
import os

# Configuration des paramètres du serveur
PORT = 3001
HOST = '0.0.0.0'
app = Flask(__name__)

# Chargement des définitions de schéma GraphQL depuis un fichier
print("Chargement du schéma GraphQL à partir de 'movie.graphql'")  # Debug: Schéma GraphQL chargé
type_defs = load_schema_from_path('movie.graphql')

# Définition des types GraphQL : requêtes et mutations
query = QueryType()
mutation = MutationType()
movie = ObjectType('Movie')
actor = ObjectType('Actor')

# Configuration des résolveurs de requête
query.set_field('movie_with_id', r.movie_with_id)
query.set_field('get_movie_by_title', r.get_movie_by_title)

# Configuration des résolveurs de mutation
mutation.set_field('update_movie_rate', r.update_movie_rate)
mutation.set_field('add_movie', r.add_movie)
mutation.set_field('delete_movie', r.delete_movie)

# Ajout du champ 'actors' au type 'Movie'
movie.set_field('actors', r.resolve_actors_in_movie)

# Obtenir le chemin du répertoire du script en cours
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construire le chemin du fichier JSON en fonction du répertoire du script
json_file_path = os.path.join(script_dir, 'data', 'movies.json')

# Vérifier si le fichier existe
if not os.path.exists(json_file_path):
    raise FileNotFoundError(f"Le fichier {json_file_path} est introuvable.")
print(f"Fichier JSON trouvé : {json_file_path}")  # Debug: Fichier JSON trouvé

# Charger la base de données JSON
with open(json_file_path, "r") as jsf:
    movies = json.load(jsf)["movies"]
    print(f"{len(movies)} films chargés depuis le fichier JSON.")  # Debug: Nombre de films chargés

# Création du schéma exécutable à partir des types et des résolveurs
schema = make_executable_schema(type_defs, movie, query, mutation, actor)

@app.route("/help", methods=['GET'])
def get_help():
    print("Appel de la route /help")  # Debug: Impression de la route appelée
    return make_response(render_template('help.html'), 200)

@app.route("/template", methods=['GET'])
def template():
    print("Appel de la route /template")  # Debug: Impression de la route appelée
    return make_response(render_template('index.html'), 200)

@app.route("/json", methods=['GET'])
def get_json():
    print("Appel de la route /json")  # Debug: Impression de la route appelée
    res = make_response(jsonify(movies), 200)
    return res

# Point d'entrée racine pour le service
@app.route("/", methods=['GET'])
def home():
    """
    Route de bienvenue pour le service utilisateur.
    """
    print("Appel de la route racine /")  # Debug: Impression de la route appelée
    return make_response(
        '<body style="background-color: #2c2c2c; color: #e0e0e0; font-family: Arial, sans-serif; display: flex;flex-direction: column;justify-content: center;align-items: center;height: 100vh;margin: 0;"><h1 style="font-size: 2em;color: #f0f0f0;">Bienvenue sur le composant <span style="color: #1e90ff">Movie</span><span style="margin-left: 10px;">🎉</span></h1></body>',
        200
    )

# Point d'entrée pour les requêtes GraphQL
@app.route('/graphql', methods=['POST'])
def graphql_server():
    print("Appel de la route /graphql")  # Debug: Impression de la route appelée
    data = request.get_json()
    print(f"Données reçues pour GraphQL : {data}")  # Debug: Données reçues
    success, result = graphql_sync(
        schema,
        data,
        context_value=None,
        debug=app.debug
    )
    status_code = 200 if success else 400
    print(f"Résultat GraphQL : {result}, Statut : {status_code}")  # Debug: Résultat et statut
    return jsonify(result), status_code

# Point d'entrée pour récupérer des informations sur un film et ses acteurs
@app.route('/movieactors/<movieid>', methods=['GET'])
def movie_with_actors(movieid):
    print(f"Appel de la route /movieactors avec l'ID du film : {movieid}")  # Debug: Impression de l'ID du film
    movie_data = r.get_movie_with_actors(movieid)
    if movie_data:
        print(f"Données du film trouvées pour l'ID {movieid}")  # Debug: Film trouvé
        return jsonify(movie_data), 200
    print(f"Aucun film trouvé pour l'ID {movieid}")  # Debug: Film non trouvé
    return jsonify({"error": "Movie not found"}), 404

# Démarrage du serveur Flask
if __name__ == "__main__":
    print(f"Le serveur démarre sur {HOST}:{PORT}")  # Debug: Démarrage du serveur
    app.run(host=HOST, port=PORT)
