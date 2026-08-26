# GT7 Telemetry — Roadmap produit

## Vision

Construire une application de **race engineering / télémétrie GT7** combinant l'esthétique de Gran Turismo 7 avec une interface inspirée des outils d'ingénierie automobile et de mécatronique.

L'objectif n'est pas seulement de visualiser les données, mais de les transformer progressivement en informations permettant au pilote de comprendre et d'améliorer ses performances.

---

## 1. Direction artistique

### Style

- Inspiration GT7 + race engineering + mécatronique.
- Fond noir / anthracite.
- Blanc fortement contrasté.
- Rouge GT7 très saturé comme couleur d'accent.
- Cyan / bleu électrique pour les données et états actifs.
- Typographie technique et moderne.
- Cartes et panneaux angulaires.
- Séparateurs fins et hiérarchie visuelle forte.
- Gros chiffres pour les métriques importantes.
- Animations rapides et discrètes.
- Éviter l'esthétique « gamer/cyberpunk » excessive.
- Ne pas copier littéralement l'interface de GT7.

### Principe UX

L'interface doit privilégier les informations utiles au pilotage plutôt que d'afficher tous les champs télémétriques disponibles.

---

# 2. Architecture principale

Navigation proposée :

- Dashboard
- Live
- Sessions
- Laps
- Compare
- Cars
- Tracks
- Settings

Structure fonctionnelle :

```text
Dashboard
    │
    ├── Live Telemetry
    │
    ├── Sessions
    │      └── Lap Analysis
    │              └── Compare
    │
    ├── Cars
    │
    └── Tracks
```

---

# 3. Phase 1 — UI Shell

Créer le socle visuel de l'application React/Vite existante.

### Objectifs

- Sidebar principale.
- Navigation entre les sections.
- Header.
- Système de cartes / panels.
- Système de badges et indicateurs.
- Responsive desktop-first.
- Thème sombre cohérent.
- Composants graphiques réutilisables.

### Navigation

```text
GT7 TELEMETRY

Dashboard
Live
Sessions
Laps
Compare
Cars
Tracks

──────────────

Settings
```

---

# 4. Phase 2 — Dashboard

Le Dashboard doit fournir une vision rapide de l'activité.

### Hero

```text
GT7 TELEMETRY
RACE ENGINEERING SYSTEM

Monitor.
Analyze.
Improve.

[ LIVE SESSION ]
```

### KPIs

Afficher notamment :

- Best lap.
- Best sector.
- Top speed.
- Average speed.
- Total laps.
- Number of sessions.
- Most driven car.
- Most driven track.

### Recent Sessions

Table des dernières sessions :

- Date.
- Voiture.
- Circuit.
- Nombre de tours.
- Best lap.
- Session.

### Performance Evolution

Graphique de l'évolution des temps au tour.

---

# 5. Phase 3 — Live Telemetry

Exploiter les `TelemetrySample` reçus en temps réel.

## Instruments principaux

Afficher en priorité :

- Speed.
- RPM.
- Gear.
- Throttle.
- Brake.

Exemple :

```text
SPEED
247
KM/H

RPM
7 842

GEAR
5

THROTTLE  ████████████░
BRAKE     ███░░░░░░░░░
```

## Dynamique véhicule

Afficher :

- Vitesse.
- Accélération longitudinale.
- Accélération latérale.
- RPM.
- Gear.
- Steering.
- Throttle.
- Brake.
- Clutch.

## État du véhicule

Afficher :

- Fuel.
- Oil pressure.
- Water temperature.
- Oil temperature.
- Tyre temperatures FL / FR / RL / RR.
- Suspension height.
- Wheel RPS.

Ne pas afficher tous les champs bruts simultanément.

---

# 6. Phase 4 — Live Track Map

Exploiter :

- `position_x`
- `position_y`
- `position_z`

### Fonctionnalités

- Position actuelle du véhicule.
- Trace du véhicule.
- Historique de trajectoire.
- Coloration de la trajectoire selon la vitesse.
- Option future : coloration selon throttle / brake.
- Détection de surface via `surface_type`.

Cette infrastructure devra pouvoir être réutilisée plus tard pour comparer plusieurs tours.

---

# 7. Phase 5 — Sessions

L'API actuelle doit évoluer pour permettre le listing.

### Endpoints à prévoir

```text
GET /api/sessions
GET /api/laps
```

### Interface

Table avec :

- Date.
- Voiture.
- Circuit.
- Best lap.
- Nombre de tours.
- Statut.
- Action View.

### Filtres

- Recherche.
- Voiture.
- Circuit.
- Date.
- Validité.
- Tri.
- Pagination.

---

# 8. Phase 6 — Lap Analysis

Fonctionnalité centrale du produit.

Lorsqu'un tour est ouvert :

```text
LAP #17

2:18.421
VALID

Porsche 911 GT3
Spa-Francorchamps
```

### Métriques principales

- Lap time.
- Best lap.
- Average lap.
- Top speed.
- Average speed.
- Nombre de samples.
- Validité.

### Graphiques

Graphiques synchronisés :

- Speed.
- Throttle / Brake.
- RPM.
- Gear.
- Steering.

### Axe de comparaison

Privilégier **la distance parcourue** plutôt que seulement le temps.

Cela permet de comparer deux tours indépendamment de leur durée.

---

# 9. Phase 7 — Lap Comparison

Fonctionnalité prioritaire.

## Comparaison primaire

Comparer en priorité :

1. Même `car_code`.
2. Sinon, même `car_category`.

Ne jamais présenter deux voitures différentes comme directement équivalentes sans indiquer clairement leur niveau de comparaison.

### Exemple

```text
Porsche 911 GT3
car_code: XXXXX

Lap #14
2:19.821

vs

Lap #18
2:18.421
```

### Comparaison secondaire

Si aucun tour de la même voiture n'est disponible :

```text
Même catégorie

GR.3
```

`car_category` sert alors à trouver des véhicules comparables.

`car_code` permet une identification plus précise.

---

# 10. Phase 8 — Delta Analysis

Transformer la comparaison en analyse de performance.

### Comparaison par zone

```text
             LAP A       LAP B       DELTA

Turn 1       152 km/h    147 km/h    -5
Turn 2       128 km/h    133 km/h    +5
Turn 3       174 km/h    175 km/h    +1
```

### Delta temporel

Afficher les pertes et gains de temps le long du tour.

### Sur la Track Map

Afficher les zones où le pilote :

- gagne du temps ;
- perd du temps ;
- freine plus tôt ;
- accélère plus tôt ;
- atteint une vitesse minimale différente.

---

# 11. Phase 9 — Sector / Corner Analysis

À développer lorsque les données et algorithmes nécessaires sont suffisamment définis.

## Braking Analysis

Potentiellement :

- Brake point.
- Peak brake pressure.
- Braking duration.
- Trail braking duration.
- Minimum speed.

## Corner Exit

Potentiellement :

- Throttle application.
- Time to full throttle.
- Exit speed.

## Consistency

Exemple :

```text
LAP CONSISTENCY

█████████████████░░ 86%

Best       2:18.421
Average    2:19.182
Spread     0.761s
```

Les métriques doivent être calculées à partir de règles clairement définies et non simplement inventées à partir des données.

---

# 12. Phase 10 — Car Explorer

Utiliser les métadonnées disponibles :

- `car_code`
- `car_name`
- `manufacturer_id`
- `car_category`

### Vue voiture

```text
PORSCHE 911 GT3

Sessions       24
Laps           318
Best Lap       2:18.421
Average Lap    2:20.821
Top Speed      291 km/h
```

### Analyse

- Performance par circuit.
- Évolution des temps.
- Nombre de sessions.
- Nombre de tours.
- Best lap.
- Average lap.
- Top speed.

---

# 13. Phase 11 — Track Explorer

### Vue circuit

```text
SPA-FRANCORCHAMPS

Sessions       34
Laps           421

Best overall
2:18.421

Your best
2:18.421

Average
2:21.823
```

### Progression

Graphique de progression :

```text
Session 1     2:25
Session 2     2:23
Session 3     2:21
Session 4     2:19
Session 5     2:18
```

---

# 14. Phase 12 — Backend API

API actuelle :

```text
GET /api/sessions/{session_id}
GET /api/laps/{lap_id}
```

### Routes à ajouter progressivement

```text
GET /api/sessions
GET /api/laps
GET /api/cars
GET /api/tracks
GET /api/sessions/{id}/summary
GET /api/laps/{id}/telemetry
```

### Live

Prévoir une couche temps réel, par exemple :

```text
WebSocket /api/live
```

ou SSE selon les besoins de l'architecture existante.

---

# 15. Phase 13 — Données dérivées

Une fois le MVP stable, exploiter davantage les données brutes.

## Performance

- Top speed.
- Average speed.
- Acceleration.
- Deceleration.
- 0–100.
- 100–200.
- etc.

## Driving

- Brake points.
- Braking duration.
- Brake intensity.
- Throttle application.
- Throttle lift.
- Steering input.
- Gear changes.

## Vehicle Dynamics

Potentiellement exploiter :

```text
angular_velocity
rotation_pitch
rotation_yaw
rotation_roll

sway
heave
surge

susp_height
wheel_rps
```

Objectif : évoluer vers une véritable analyse de dynamique véhicule / mécatronique.

---

# 16. Phase 14 — Insights

Future couche d'analyse intelligente.

Exemples :

- Weakest sector.
- Largest time loss.
- Inconsistent braking.
- Early braking.
- Late throttle application.
- Best corner entry.
- Best corner exit.
- Driving consistency.
- Performance progression.

Exemple :

```text
POTENTIAL IMPROVEMENT

You lose approximately 0.42s
in the second sector compared
with your best lap.
```

Cette phase pourra éventuellement intégrer une couche IA.

---

# 17. Modèle de données actuel

Le backend utilise :

- Python.
- FastAPI.
- Pydantic.
- SQLAlchemy.
- SQLite.

Relation actuelle :

```text
Session
   │
   └── Lap
         │
         └── TelemetrySample
```

La télémétrie contient notamment :

### Position / mouvement

- position_x
- position_y
- position_z
- velocity_x
- velocity_y
- velocity_z
- speed

### Moteur / transmission

- rpm
- gear
- suggested_gear
- throttle
- brake
- clutch
- boost

### Fluides / températures

- fuel_level
- fuel_capacity
- oil_pressure
- water_temp
- oil_temp
- tyre_temp_fl
- tyre_temp_fr
- tyre_temp_rl
- tyre_temp_rr

### Tours

- lap_count
- total_laps
- best_laptime_ms
- last_laptime_ms
- current_lap_ms

### Direction / châssis

- steering
- wheel_base
- surface_type
- car_category
- car_code

### PacketA / PacketB / PacketC

- rotation_pitch
- rotation_yaw
- rotation_roll
- orientation_to_north
- angular_velocity_x/y/z
- body_height
- day_progression
- race_start_position
- pre_race_num_cars
- min_alert_rpm
- max_alert_rpm
- calc_max_speed
- road_plane
- wheel_rps
- tyre_radius
- suspension height
- clutch / gearbox data
- wheel_rotation
- steering_angular_velocity
- sway
- heave
- surge

---

# 18. Priorités MVP

L'ordre recommandé est :

```text
1. UI Shell
       ↓
2. Dashboard
       ↓
3. Live Telemetry
       ↓
4. Sessions
       ↓
5. Lap Analysis
       ↓
6. Lap Comparison
       ↓
7. Track Map
       ↓
8. Cars
       ↓
9. Tracks
```

Puis :

```text
10. Delta Analysis
11. Sector Analysis
12. Corner Analysis
13. Vehicle Dynamics
14. Driving Insights
15. AI Analysis
```

---

# 19. Principe architectural pour v0

Le frontend doit être ajouté au **projet React/Vite existant**.

Ne pas recréer une application indépendante.

Le générateur UI doit :

- inspecter la structure existante ;
- conserver l'architecture actuelle ;
- réutiliser les dépendances présentes lorsque possible ;
- ne pas remplacer inutilement la configuration ;
- isoler les appels API dans une couche claire ;
- permettre l'utilisation temporaire de données mockées lorsque les endpoints ne sont pas encore disponibles ;
- rendre facile le remplacement des mocks par les endpoints FastAPI réels.

L'objectif est de construire progressivement l'interface autour du backend existant, et non de créer un prototype visuel déconnecté du moteur de télémétrie.
