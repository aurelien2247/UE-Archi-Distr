from concurrent import futures
import grpc 
import booking_pb2
import booking_pb2_grpc
import sys 
import json
import os

# Ajout du chemin pour accéder aux fichiers showtime
sys.path.append('../showtime')
import showtime_pb2
import showtime_pb2_grpc 

# Configuration du service Booking
PORT = 3201
HOST = '0.0.0.0'

# Chargement de la base de données JSON des réservations
script_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(script_dir, 'data', 'bookings.json')

# Vérification de l'existence du fichier JSON
if not os.path.exists(json_file_path):
    raise FileNotFoundError(f"Le fichier {json_file_path} est introuvable.")
print(f"Chargement des réservations depuis {json_file_path}")  # Debug: Chemin du fichier JSON

# Lecture des réservations à partir du fichier JSON
with open(json_file_path, "r") as jsf:
    bookings = json.load(jsf)["bookings"]
    print(f"{len(bookings)} réservations chargées.")  # Debug: Nombre de réservations chargées

# Classe pour le service gRPC de réservations
class BookingService(booking_pb2_grpc.BookingServiceServicer):
    
    def GetBookings(self, request, context):
        """
        Récupère toutes les réservations et les retourne sous forme de réponse.
        """
        print("Appel de GetBookings")  # Debug: Impression de l'appel de la méthode
        response = booking_pb2.GetBookingsResponse()
        for booking in bookings:
            booking_proto = response.bookings.add()
            booking_proto.userid = booking["userid"]
            for date in booking["dates"]:
                booking_date = booking_proto.dates.add()
                booking_date.date = date["date"]
                for movie in date["movies"]:
                    booking_date.movies.add(id=movie)
        print("Réponse avec toutes les réservations envoyée.")  # Debug: Réponse envoyée
        return response

    def GetBookingByUser(self, request, context):
        """
        Récupère les réservations pour un utilisateur spécifique.
        """
        print(f"Appel de GetBookingByUser pour l'utilisateur {request.userid}")  # Debug: Impression de l'ID utilisateur
        for booking in bookings:
            if booking["userid"] == request.userid:
                response = booking_pb2.GetBookingByUserResponse()
                booking_proto = response.booking
                booking_proto.userid = booking["userid"]
                for date in booking["dates"]:
                    booking_date = booking_proto.dates.add()
                    booking_date.date = date["date"]
                    for movie in date["movies"]:
                        booking_date.movies.add(id=movie)
                print(f"Réservations trouvées pour l'utilisateur {request.userid}")  # Debug: Réservation trouvée
                return response
        # Gestion de l'erreur si l'utilisateur n'a pas de réservation
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details(f"Réservation introuvable pour l'utilisateur id: {request.userid}")
        print(f"Aucune réservation trouvée pour l'utilisateur {request.userid}")  # Debug: Aucune réservation trouvée
        return booking_pb2.GetBookingByUserResponse()

    def AddBooking(self, request, context):
        """
        Ajoute une nouvelle réservation après vérification des disponibilités.
        """
        print(f"Appel de AddBooking pour l'utilisateur {request.userid} à la date {request.date.date}")  # Debug: Impression de l'appel et des détails de la requête
        # Vérification des films disponibles via le service Showtime
        with grpc.insecure_channel('localhost:3202') as channel:
            stub = showtime_pb2_grpc.ShowtimeServiceStub(channel)
            showtime_request = showtime_pb2.GetShowtimesByDateRequest(date=request.date.date)
            showtime_response = stub.GetShowtimesByDate(showtime_request)

            # Vérification de la disponibilité des films
            if not showtime_response.showtime.movies:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(f"Aucun film disponible pour la date demandée: {request.date.date}")
                print(f"Aucun film disponible pour la date {request.date.date}")  # Debug: Aucun film disponible
                return booking_pb2.AddBookingResponse()

            movies_on_this_date = [movie for movie in showtime_response.showtime.movies]
            print(f"Films disponibles pour la date {request.date.date}: {movies_on_this_date}")  # Debug: Impression des films disponibles

            # Vérification si les films demandés sont disponibles
            for movie in request.date.movies:
                if movie.id not in movies_on_this_date:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details(f"Un ou plusieurs films ne sont pas disponibles pour la date demandée")
                    print(f"Film non disponible: {movie.id}")  # Debug: Impression du film non disponible
                    return booking_pb2.AddBookingResponse()

        # Recherche d'une réservation existante pour l'utilisateur
        user_booking = next((booking for booking in bookings if booking["userid"] == request.userid), None)

        # Création d'une nouvelle réservation si l'utilisateur n'en a pas
        if user_booking is None:
            user_booking = {
                "userid": request.userid,
                "dates": []
            }
            bookings.append(user_booking)
            print(f"Nouvelle réservation créée pour l'utilisateur {request.userid}")  # Debug: Nouvelle réservation créée

        # Vérification de l'existence d'une réservation pour la même date
        if any(date["date"] == request.date.date for date in user_booking["dates"]):
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(f"Une réservation existe déjà pour la date: {request.date.date}")
            print(f"Réservation existante pour la date {request.date.date} pour l'utilisateur {request.userid}")  # Debug: Réservation existante
            return booking_pb2.AddBookingResponse()

        # Ajout de la nouvelle réservation
        new_booking = {
            "date": request.date.date,
            "movies": [movie.id for movie in request.date.movies]
        }
        user_booking["dates"].append(new_booking)
        print(f"Nouvelle réservation ajoutée pour l'utilisateur {request.userid} à la date {request.date.date}")  # Debug: Réservation ajoutée

        # Écriture des réservations mises à jour dans le fichier JSON
        with open(json_file_path, "w") as jsf:
            json.dump({"bookings": bookings}, jsf)
            print("Fichier JSON mis à jour avec la nouvelle réservation.")  # Debug: Mise à jour du fichier JSON

        return booking_pb2.AddBookingResponse(message=f"Réservation ajoutée pour l'utilisateur {request.userid}")

# Fonction pour démarrer le serveur gRPC
def serve():
    print(f"Initialisation du serveur gRPC sur {HOST}:{PORT}")  # Debug: Impression de l'initialisation du serveur
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServiceServicer_to_server(BookingService(), server)
    server.add_insecure_port(f'{HOST}:{PORT}')
    server.start()
    print(f"Le serveur gRPC du service Booking fonctionne sur le port {PORT}")  # Debug: Le serveur démarre
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
