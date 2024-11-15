from flask import json
import os

# Définir le chemin de la base de données
DATA_DIR = os.path.join(".", "data")
MOVIES_FILE = os.path.join(DATA_DIR, "movies.json")
ACTORS_FILE = os.path.join(DATA_DIR, "actors.json")

# Charger les films depuis le fichier JSON
def load_movies():
    with open(MOVIES_FILE, "r") as file:
        return json.load(file)['movies']

# Sauvegarder les films dans le fichier JSON
def save_movies(movies):
    with open(MOVIES_FILE, "w") as file:
        json.dump({"movies": movies}, file)

# Fonction pour récupérer un film par titre
def get_movie_by_title(_, info, title):
    movies = load_movies()
    for movie in movies:
        if movie['title'].lower() == title.lower():
            return movie
    return None

# Fonction pour récupérer un film par son ID
def movie_with_id(_, info, _id):
    movies = load_movies()
    for movie in movies:
        if movie['id'] == _id:
            return movie
    return None  # Si aucun film n'est trouvé

# Fonction pour ajouter un nouveau film
def add_movie(_, info, _id, title, director, rating):
    movies = load_movies()
    for movie in movies:
        if movie['id'] == _id:
            return {"error": "Movie ID already exists"}  # Vérifie si l'ID existe déjà

    new_movie = {
        "id": _id,
        "title": title,
        "director": director,
        "rating": rating
    }
    movies.append(new_movie)  # Ajoute le nouveau film à la liste
    save_movies(movies)  # Sauvegarde les films mis à jour
    return new_movie

# Fonction pour supprimer un film par son ID
def delete_movie(_, info, _id):
    movies = load_movies()
    for movie in movies:
        if movie['id'] == _id:
            movies.remove(movie)  # Supprime le film trouvé
            save_movies(movies)  # Sauvegarde les films mis à jour
            return movie
    return {"error": "Movie ID not found"}  # Si l'ID du film n'est pas trouvé

# Fonction pour mettre à jour la note d'un film
def update_movie_rate(_, info, _id, _rate):
    movies = load_movies()
    for movie in movies:
        if movie['id'] == _id:
            movie['rating'] = _rate  # Met à jour la note
            save_movies(movies)  # Sauvegarde les films mis à jour
            return movie
    return None  # Si aucun film n'est trouvé

# Fonction pour récupérer un film et ses acteurs par ID
def get_movie_with_actors(movieid):
    with open(MOVIES_FILE, "r") as movie_file, open(ACTORS_FILE, "r") as actors_file:
        movies = json.load(movie_file)
        actors = json.load(actors_file)
        
        # Trouver le film correspondant à l'ID fourni
        movie = next((m for m in movies['movies'] if m['id'] == movieid), None)
        if not movie:
            return None  # Si aucun film n'est trouvé
        
        # Trouver les acteurs associés à ce film
        movie_actors = [
            {
                "id": actor["id"],
                "firstname": actor["firstname"],
                "lastname": actor["lastname"],
                "birthyear": actor["birthyear"]
            }
            for actor in actors['actors'] if movieid in actor['films']
        ]
        
        # Ajouter les acteurs aux données du film
        movie_with_actors = {
            "movie": movie,
            "actors": movie_actors
        }
        
        return movie_with_actors

# Fonction pour résoudre les acteurs d'un film donné
def resolve_actors_in_movie(movie, info):
    with open(ACTORS_FILE, "r") as file:
        actors = json.load(file)
        return [actor for actor in actors['actors'] if movie['id'] in actor['films']]
