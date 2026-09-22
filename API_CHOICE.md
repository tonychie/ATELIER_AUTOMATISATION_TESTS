# API Choice

- Étudiant : Alexandre Montard
- API choisie : Agify (agify.io)
- URL base : https://api.agify.io
- Documentation officielle / README : https://agify.io/our-data
- Auth : None
- Endpoints testés :
  - GET /?name={prenom}
  - GET / (sans paramètre, pour vérifier la gestion d'erreur)
- Hypothèses de contrat (champs attendus, types, codes) :
  - 200 OK sur requête avec `name` valide
  - Réponse JSON avec les champs `name` (string), `age` (int ou null), `count` (int)
  - `name` inconnu -> 200 avec `age: null` et `count: 0` (pas d'erreur serveur)
  - `name` manquant -> code d'erreur 400/422
- Limites / rate limiting connu : 1000 requêtes/jour en accès anonyme (IP), au-delà -> 429
- Risques (instabilité, downtime, CORS, etc.) : dépendance à un service tiers gratuit, pas de SLA garanti ; quota journalier partagé par IP.
