# GT7 Telemetry Engine - Étape 3 : Heartbeat + capture PS5

Moteur d'analyse télémétrique pour Gran Turismo 7 sur PS5.

## Structure du projet

- `collector/` : Réception UDP, heartbeat, déchiffrement Salsa20, simulation.
- `models/` : Modèles de données Pydantic (Session, Lap, TelemetrySample).
- `session/` : Logique métier (détection de tours, validation, gestion de session).
- `storage/` : Gestion de la persistance (SQLite relationnel).
- `api/` : API FastAPI pour consulter les sessions et les tours enregistrés.
- `tests/` : Tests automatisés.

## Installation

1. Assurez-vous d'avoir Python 3.12+ installé.
2. Installez les dépendances :
   ```bash
   pip install -r telemetry_engine/requirements.txt
   ```

Depuis la racine du projet, le moteur Python utilise `telemetry_engine` comme
racine d'import. Dans PowerShell :

```powershell
$env:PYTHONPATH="telemetry_engine"
```

## Workflow de test

Le mode mock permet de tester le pipeline localement sans PS5. Il génère 100
`TelemetrySample`, les envoie au `SessionManager`, valide les tours et
persiste la session dans SQLite :

```bash
python telemetry_engine/main.py
```

Pour lancer les tests automatisés :

```powershell
python -m pytest telemetry_engine/tests/ -q
```

Les tests couvrent notamment le déchiffrement Salsa20, le décodage des
offsets PacketA/PacketB/PacketC, le heartbeat, l'écoute UDP, la persistance
SQLite et la gestion des tours. Les limites d'un tour sont déterminées par
`lap_count`, fourni directement par GT7; la distance n'est pas utilisée pour
compter les tours.

## Workflow réel PS5

Le PC et la PS5 doivent être sur le même réseau local. Configurez l'adresse
IP de la console et, si nécessaire, l'adresse locale du PC :

```powershell
$env:GT7_PS5_IP="192.168.1.12"
$env:GT7_LISTEN_IP="192.168.1.8"
$env:PYTHONPATH="telemetry_engine"
python telemetry_engine/main.py --real
```

Le flux réel fonctionne ainsi :

1. Le listener UDP s'attache à `GT7_LISTEN_IP:GT7_LISTEN_PORT` (`33740` par défaut).
2. Le heartbeat envoie `C` à `GT7_PS5_IP:33739` immédiatement, puis toutes les 2 secondes.
3. Chaque paquet reçu est déchiffré avec Salsa20 puis décodé selon les offsets GT7.
4. Le `TelemetrySample` est transmis au `SessionManager`.
5. Le `LapDetector` crée et clôture les tours uniquement lors d'une transition de `lap_count`.
6. Les samples et les tours sont sauvegardés dans SQLite jusqu'à l'arrêt avec Ctrl+C.

`GT7_PS5_IP` est obligatoire en mode `--real` et ne peut pas être `0.0.0.0`.
`GT7_LISTEN_IP` doit être l'adresse réseau du PC; `GT7_LISTEN_PORT` vaut
`33740` par défaut. Ctrl+C arrête le listener et le heartbeat, puis sauvegarde
le dernier tour et clôture la session.

Pour changer les ports :

```powershell
$env:GT7_LISTEN_PORT="33740"
$env:GT7_PS5_IP="192.168.1.12"
```

## Fonctionnement des sessions

Une session est créée au démarrage du moteur et reçoit les échantillons dans
l'ordre de réception. Pour chaque `TelemetrySample` :

1. `LapDetector` ignore les compteurs `lap_count` invalides et les paquets
    reçus en retard ou en double.
2. Une transition de `lap_count` clôt le tour précédent et démarre le nouveau.
3. L'échantillon qui contient le nouveau compteur appartient au nouveau tour.
4. `LapValidator` valide le tour s'il contient suffisamment d'échantillons et,
    lorsqu'un meilleur temps GT7 est disponible, si sa durée est cohérente.
5. Le tour terminé est sauvegardé dans SQLite avec tous ses samples.

La fin de session avec Ctrl+C clôture également le tour en cours à partir du
dernier timestamp valide. Le stockage suit la relation :
`Session -> Lap -> TelemetrySample`.

## API HTTP

L'API est implémentée avec FastAPI et lit la même base SQLite que le moteur
(`telemetry.db` à la racine du projet). Démarrez-la depuis la racine du projet
avec l'environnement virtuel activé :

```powershell
$env:PYTHONPATH="telemetry_engine"
uvicorn api.main:app --app-dir telemetry_engine --reload
```

Elle est alors accessible à l'adresse `http://127.0.0.1:8000`. La
documentation interactive Swagger UI est disponible sur
`http://127.0.0.1:8000/docs` et la documentation OpenAPI sur
`http://127.0.0.1:8000/openapi.json`.

Endpoints actuellement disponibles :

| Méthode | URL | Description |
| --- | --- | --- |
| `GET` | `/api/sessions/{session_id}` | Retourne une session avec ses tours et samples. |
| `GET` | `/api/laps/{lap_id}` | Retourne un tour avec ses samples. |

Exemples :

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/sessions/1
Invoke-RestMethod http://127.0.0.1:8000/api/laps/1
```

Lancez le collector et l'API dans deux terminaux séparés pour alimenter la
base pendant les requêtes. Le collector mock peut d'abord créer des données
locales avec `python telemetry_engine/main.py`.

## Prochaines étapes

- Ajouter une route pour lister les sessions et les tours.
- Enrichir les métadonnées de session avec le circuit et le véhicule identifiés
   à partir de `car_code` et `car_category`.
- Ajouter des outils d'analyse des tours: comparaison des temps, secteurs et
   export des données télémétriques.
