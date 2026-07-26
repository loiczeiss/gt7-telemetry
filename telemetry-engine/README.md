# GT7 Telemetry Engine - Étape 2 : Session Management

Moteur d'analyse télémétrique pour Gran Turismo 7 sur PS5.

## Structure du projet

- `collector/` : Réception (UDP) et simulation de données.
- `models/` : Modèles de données Pydantic (Session, Lap, TelemetrySample).
- `session/` : Logique métier (détection de tours, validation, gestion de session).
- `storage/` : Gestion de la persistance (SQLite relationnel).
- `tests/` : Tests automatisés.

## Installation

1. Assurez-vous d'avoir Python 3.12+ installé.
2. Installez les dépendances :
   ```bash
   pip install -r telemetry-engine/requirements.txt
   ```

## Utilisation

### Lancer le moteur (Mock)
Pour tester le pipeline complet avec des données simulées :
```bash
$env:PYTHONPATH="telemetry-engine"; python telemetry-engine/main.py
```

### Lancer le moteur (Real PS5)
Pour écouter une vraie PS5 (nécessite d'être sur le même réseau) :
```bash
$env:PYTHONPATH="telemetry-engine"; python telemetry-engine/main.py --real
```

### Lancer les tests
```bash
$env:PYTHONPATH="telemetry-engine"; python -m pytest telemetry-engine/tests/
```

## Fonctionnalités de Session
- **Auto-détection de tours** : Le système détecte le passage sur la ligne d'arrivée via le reset de la distance totale parcourue.
- **Validation** : Les tours trop courts ou sans assez de données sont marqués comme invalides.
- **Stockage relationnel** : Les données sont organisées par Session -> Tours -> Échantillons.

## Prochaines étapes
- Implémentation du "Heartbeat" UDP automatique pour réveiller la télémétrie GT7.
- Détection automatique du circuit et de la voiture via les ID envoyés par GT7.
- Interface API FastAPI pour visualiser les tours en temps réel.
