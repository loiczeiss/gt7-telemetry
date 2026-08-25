# GT7 Telemetry Engine - Étape 3 : Heartbeat + capture PS5

Moteur d'analyse télémétrique pour Gran Turismo 7 sur PS5.

## Structure du projet

- `collector/` : Réception UDP, heartbeat, déchiffrement Salsa20, simulation.
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
Pour tester le pipeline complet avec des données simulées (100 samples, pas un tour complet) :
```bash
$env:PYTHONPATH="telemetry-engine"; python telemetry-engine/main.py
```

### Lancer le moteur (Real PS5)

PC et PS5 sur le même LAN. Définir l'IP de la console, puis lancer `--real` :

```powershell
$env:PYTHONPATH="telemetry-engine"
$env:GT7_PS5_IP="192.168.1.12"
python telemetry-engine/main.py --real
```

Le collector :

1. Bind UDP sur `0.0.0.0:33740` (paquets PS5 → PC).
2. Envoie un heartbeat `A` vers `GT7_PS5_IP:33739` immédiatement, puis toutes les 2 s.
3. Déchiffre chaque paquet (Salsa20, clé communautaire GT7).
4. Enregistre tous les samples (pas de plafond à 100) et découpe les tours avec `lap_count` fourni par GT7.

`GT7_PS5_IP` est obligatoire en `--real` et ne peut pas être `0.0.0.0`. Ctrl+C termine la session et sauvegarde le dernier tour.

### Lancer les tests
```bash
$env:PYTHONPATH="telemetry-engine"; python -m pytest telemetry-engine/tests/
```

## Fonctionnalités de Session
- **Détection de tours** : transitions du compteur `lap_count` fourni par GT7.
- **Validation** : tours trop courts ou sans assez de données marqués invalides.
- **Stockage relationnel** : Session -> Tours -> Échantillons.

## Prochaines étapes
- Détection automatique du circuit et de la voiture via les ID envoyés par GT7.
- Interface API FastAPI pour visualiser les tours en temps réel.
