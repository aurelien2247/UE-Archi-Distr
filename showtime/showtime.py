from concurrent import futures
import grpc
import showtime_pb2
import showtime_pb2_grpc
import json
import os

# Configuration du serveur
PORT = 3202
HOST = '0.0.0.0'

# Chargement du fichier JSON contenant les horaires
script_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(script_dir, 'data', 'times.json')

# Vérification de l'existence du fichier JSON
if not os.path.exists(json_file_path):
    raise FileNotFoundError(f"Le fichier {json_file_path} est introuvable.")
print(f"Fichier JSON trouvé : {json_file_path}")  # Debug: Fichier trouvé

# Chargement des horaires depuis le fichier JSON
with open(json_file_path, "r") as jsf:
    schedule = json.load(jsf)["schedule"]
    print(f"{len(schedule)} dates chargées depuis le fichier JSON.")  # Debug: Nombre de dates chargées

# Classe implémentant le service gRPC pour les horaires
class ShowtimeService(showtime_pb2_grpc.ShowtimeServiceServicer):
    def __init__(self):
        # Chargement des horaires lors de l'initialisation du service
        print("Initialisation du service Showtime...")  # Debug: Initialisation du service
        with open('{}/data/times.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["schedule"]
        print("Horaires chargés avec succès dans ShowtimeService.")  # Debug: Chargement réussi

    def GetShowtimes(self, request, context):
        """
        Récupère tous les horaires disponibles.
        """
        print("Appel de la méthode GetShowtimes.")  # Debug: Appel de GetShowtimes
        response = showtime_pb2.GetShowtimesResponse()
        for day in schedule:
            showtime = response.showtimes.add()
            showtime.date = day["date"]
            showtime.movies.extend(day["movies"])  # Ajoute les films pour la date
        print(f"Renvoi de {len(response.showtimes)} horaires.")  # Debug: Nombre d'horaires renvoyés
        return response

    def GetShowtimesByDate(self, request, context):
        """
        Récupère les horaires pour une date spécifiée.
        """
        print(f"Appel de GetShowtimesByDate pour la date : {request.date}")  # Debug: Date demandée
        requested_date = request.date
        for day in schedule:
            if str(day["date"]) == str(requested_date):
                response = showtime_pb2.GetShowtimesByDateResponse()
                showtime = response.showtime
                showtime.date = day["date"]
                showtime.movies.extend(day["movies"])  # Ajoute les films pour la date
                print(f"Horaires trouvés pour la date {requested_date}.")  # Debug: Horaires trouvés
                return response
        
        # Si la date n'est pas trouvée, retourne une erreur NOT_FOUND
        print(f"Date non trouvée : {requested_date}")  # Debug: Date non trouvée
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details(f"Date not found: {requested_date}")
        return showtime_pb2.GetShowtimesByDateResponse()

def serve():
    """
    Fonction pour démarrer le serveur gRPC.
    """
    print(f"Lancement du serveur sur {HOST}:{PORT}")  # Debug: Démarrage du serveur
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    showtime_pb2_grpc.add_ShowtimeServiceServicer_to_server(ShowtimeService(), server)
    server.add_insecure_port('[::]:3202')  # Port d'écoute du serveur
    server.start()
    print(f"Le serveur gRPC Showtime fonctionne sur le port {PORT}")  # Debug: Serveur démarré
    server.wait_for_termination()

if __name__ == '__main__':
    serve()  # Lancement du serveur si ce fichier est exécuté directement
