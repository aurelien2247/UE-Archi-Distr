# UE-AD-A1-REST

## Sommaire
- [Introduction](#introduction)
- [Détails des composants](#details-des-composants)
- [Lancement](#lancement)
- [Test avec Postman](#test-avec-postman)

## Introduction <a name="introduction" />
Ce projet constitue une application simple pour gérer les films et les réservations d’utilisateurs dans un cinéma. L'application est composée de plusieurs micro-services, à savoir : **Showtime**, **Booking**, **User**, et **Movie**. Le micro service **User** communiquera avec le micro-service **Booking** et lui meme avec **Showtime** via gRPC pour une meilleure performance et évolutivité. La communication entre **User**, et **Movie** elle ce fera en Graphql.

<img src="/conception.png" alt="Diagramme  conceptuel de la solution"/>

- 🎥 **Movie** : Ce micro-service est responsable de la gestion des films disponibles dans le cinéma. Il utilise une base de données JSON pour stocker les informations sur les films, y compris le titre, la note, le réalisateur, et un identifiant unique.
```json
// Exemple de configuration pour un film
{
  "title": "The Good Dinosaur",
  "rating": 7.4,
  "director": "Peter Sohn",
  "id": "720d006c-3a57-4b6a-b18f-9b713b073f3c"
}
```
- ⏲ **Showtime** : Ce micro-service gère les horaires de passage des films. Il maintient une base de données JSON contenant les dates disponibles et les films projetés à ces dates.
```json
// Exemple d'une journée de disponibilité de films
{
  "date": "20151130",
  "movies": [
    "720d006c-3a57-4b6a-b18f-9b713b073f3c",
    "a8034f44-aee4-44cf-b32c-74cf452aaaae",
    "39ab85e5-5e8e-4dc5-afea-65dc368bd7ab"
  ]
}
```

- 📖 **Booking** : Ce micro-service est chargé de gérer les réservations effectuées par les utilisateurs. Il conserve une base de données JSON avec les réservations, en vérifiant la disponibilité des films via le service Showtime.
```json
// Exemple de réservations d'un utilisateur
{
  "userid": "chris_rivers",
  "dates": [
    {
      "date": "20151201",
      "movies": [
        "267eedb8-0f5d-42d5-8f43-72426b9fb3e6"
      ]
    }
  ]
}
```

- 👥 **User**: Ce micro-service agit comme point d'entrée pour les utilisateurs, leur permettant de consulter les films disponibles, les horaires et de réaliser des réservations. Il interagit avec les services Booking et Movie pour fournir ces fonctionnalités.
```json
//Exemple d'un utilisateur
{
      "date":"20151130",
      "movies":[
        "720d006c-3a57-4b6a-b18f-9b713b073f3c",
        "a8034f44-aee4-44cf-b32c-74cf452aaaae",
        "39ab85e5-5e8e-4dc5-afea-65dc368bd7ab"
      ]
    }
```
## Lancement <a name="launch" />
Pour lancer les 4 micro-services en simultané, il suffit de lancer le script ```launch.py``` situé à la racine du projet soit en double cliquant dessus, soit en faisant ```chemin/vers/le/projet> start ./launch.py``` dans un terminal.
> ⚠ Il est nécessaire d'avoir python d'intallé sur son poste.

Le script va d'abord lancer un environnement virtuel python puis y installer les dépendances communes qu'utilise les micro-services.

Si tout se déroule bien, vous devriez voir le mot FINISH dessiné dans la fenêtre de lancement suivie des 4 serveurs de développements des micro-services.

C'est dans cette fenêtre que vous pourrez suivre en temps réel l'utilisation de l'application et les différents appels qui sont effectués.
<img src="/trace.png" alt="Screenshot de la fenêtre actie lié à launch.py" />