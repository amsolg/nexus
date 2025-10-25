# NEXUS - Système de Déclenchement Événementiel

## IDENTITÉ
Vous êtes Claude Code, assistant de développement pour le projet **Nexus**. Votre mission est d'implémenter un système de déclenchement événementiel robuste et extensible qui transforme un agent IA passif en un système proactif capable de réagir en temps réel aux changements environnementaux.

## VISION DU PROJET

### Objectif Principal
Nexus est le sous-système de déclenchement du projet Mind-Mapper, conçu pour implémenter une Architecture Événementielle (EDA) qui permet à l'agent d'évoluer d'un modèle passif piloté par commandes vers un système autonome et réactif.

### Caractéristiques Fondamentales
- **Réactivité en Temps Réel** : Latence <100ms entre détection et traitement d'événement
- **Architecture Découplée** : Producteurs et consommateurs indépendants via bus de messages
- **Extensibilité** : Ajout de nouveaux producteurs sans modification du code central
- **Robustesse** : Circuit breaker, retry logic, et récupération automatique

## ARCHITECTURE TECHNIQUE

### Stack Technologique

**Core Framework**
- **Python 3.11+** : Runtime principal avec support asyncio optimisé
- **asyncio** : Programmation asynchrone pour performances maximales
- **Pydantic** : Validation et sérialisation des événements
- **structlog** : Logging structuré pour observabilité

**Bus de Messages**
- **PyMQ** : Bus de messages léger sans dépendance serveur externe
- **JSON** : Format de sérialisation standardisé
- **Memory-based** : Stockage local pour simplicité déploiement

**Producteurs Spécialisés**
- **aioimaplib** : Client IMAP asynchrone pour emails
- **Watchdog** : Surveillance système de fichiers
- **APScheduler** : Planificateur pour tâches récurrentes
- **aiohttp** : Client HTTP pour API externes

### Patterns Architecturaux

**Pattern Principal : Event-Driven Architecture (EDA)**
- Découplage complet entre producteurs et consommateurs
- Communication asynchrone via messages standardisés
- Évolutivité par ajout de producteurs

**Patterns Secondaires**
- **Producer-Consumer** : Séparation génération/traitement événements
- **Observer Pattern** : Surveillance changements d'état
- **Circuit Breaker** : Isolation des composants défaillants
- **Command Pattern** : Encapsulation des requêtes

### Architecture des Composants

```
┌─────────────────────────────────────────────────────────────────┐
│                    SYSTÈME NEXUS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │  PRODUCTEURS │───▶│  BUS MESSAGES   │───▶│   CONSOMMATEUR  │ │
│  │              │    │                 │    │                 │ │
│  │ • Email IMAP │    │ ┌─────────────┐ │    │ Système de      │ │
│  │ • File Watch │    │ │ Event Queue │ │    │ Perception      │ │
│  │ • Scheduled  │    │ │   (PyMQ)    │ │    │                 │ │
│  │ • Calendar   │    │ └─────────────┘ │    │        │        │ │
│  └──────────────┘    └─────────────────┘    └────────▼────────┘ │
│                                                      │          │
│                                               ┌──────▼──────────┐ │
│                                               │ Système de      │ │
│                                               │ Raisonnement    │ │
│                                               │ (LangGraph)     │ │
│                                               └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## STRUCTURE DU PROJET

```
nexus/
├── src/nexus/                    # Code source principal
│   ├── core/                     # Composants centraux
│   │   ├── __init__.py
│   │   ├── events.py             # Schémas d'événements Pydantic
│   │   ├── interfaces.py         # Interfaces ABC pour producteurs/consommateurs
│   │   └── config.py             # Configuration système
│   ├── bus/                      # Bus de messages
│   │   ├── __init__.py
│   │   ├── message_bus.py        # Implémentation PyMQ
│   │   └── router.py             # Routage événements par type
│   ├── producers/                # Producteurs d'événements
│   │   ├── __init__.py
│   │   ├── base.py               # Classe base AbstractProducer
│   │   ├── email_producer.py     # Producteur IMAP
│   │   ├── file_producer.py      # Surveillance fichiers
│   │   ├── scheduled_producer.py # Tâches programmées
│   │   └── registry.py           # Registre producteurs
│   ├── consumers/                # Consommateurs d'événements
│   │   ├── __init__.py
│   │   ├── perception_system.py  # Système de perception principal
│   │   └── event_processor.py    # Traitement événements
│   └── utils/                    # Utilitaires
│       ├── __init__.py
│       ├── logging.py            # Configuration logging structuré
│       ├── health.py             # Health checks
│       └── metrics.py            # Métriques observabilité
├── tests/                        # Tests complets
│   ├── unit/                     # Tests unitaires
│   ├── integration/              # Tests d'intégration
│   └── e2e/                      # Tests end-to-end
├── config/                       # Fichiers configuration
│   ├── default.yaml              # Configuration par défaut
│   ├── development.yaml          # Configuration dev
│   └── production.yaml           # Configuration production
├── docs/                         # Documentation
│   ├── api/                      # Documentation API
│   ├── architecture/             # Docs architecture
│   └── guides/                   # Guides utilisateur
├── scripts/                      # Scripts utilitaires
│   ├── run_nexus.py              # Script de lancement
│   ├── setup_dev.py              # Setup environnement dev
│   └── health_check.py           # Vérification santé système
└── examples/                     # Exemples d'usage
    ├── simple_producer.py        # Exemple producteur simple
    └── custom_consumer.py        # Exemple consommateur custom
```

## DÉVELOPPEMENT

### Conventions de Code

**Standards Python**
- **PEP 8** : Style de code strict
- **Type Hints** : Annotations complètes pour tous paramètres/retours
- **Docstrings** : Format Google style pour toutes classes/méthodes
- **asyncio** : Priorité aux opérations asynchrones

**Architecture**
- **Single Responsibility** : Une classe = une responsabilité
- **Interface Segregation** : Interfaces spécialisées et minimales
- **Dependency Injection** : Configuration via constructeur
- **Error Handling** : Try/except avec logging structuré

### Workflow de Développement

**Phase 1 : Setup & Configuration**
```bash
# Installation dépendances
pip install -r requirements.txt

# Configuration environnement
cp config/default.yaml config/local.yaml

# Tests de base
python -m pytest tests/unit/
```

**Phase 2 : Développement Producteur**
```bash
# Créer nouveau producteur
python scripts/create_producer.py --name MonProducer

# Tests spécifiques
python -m pytest tests/unit/producers/test_mon_producer.py

# Test intégration
python -m pytest tests/integration/test_bus_integration.py
```

**Phase 3 : Validation & Déploiement**
```bash
# Tests complets
python -m pytest tests/

# Linting et type checking
python -m flake8 src/nexus/
python -m mypy src/nexus/

# Performance benchmark
python scripts/benchmark_system.py
```

### Commandes Essentielles

```bash
# Démarrage système complet
python scripts/run_nexus.py --config config/local.yaml

# Mode développement avec hot-reload
python scripts/run_nexus.py --dev --verbose

# Tests avec coverage
python -m pytest tests/ --cov=nexus --cov-report=html

# Génération documentation API
python scripts/generate_docs.py

# Health check système
python scripts/health_check.py --all-components

# Benchmark performance
python scripts/benchmark_system.py --duration 60 --events-per-second 100
```

## MÉTRIQUES DE PERFORMANCE

### KPIs de Succès
- **Latence Événement** : <100ms détection→traitement
- **Débit Système** : 100+ événements/seconde
- **Disponibilité** : 99.9% uptime bus de messages
- **Efficacité** : 90% réduction CPU vs polling traditionnel

### Monitoring en Temps Réel
- **Métriques Bus** : Taille queue, latence messages, taux erreur
- **Métriques Producteurs** : Santé connexions, événements générés, échecs
- **Métriques Système** : CPU, mémoire, I/O réseau
- **Alertes** : Seuils configurables pour intervention automatique

## EXTENSIBILITÉ

### Ajout Nouveau Producteur
1. **Hériter** de `AbstractProducer` dans `producers/base.py`
2. **Implémenter** méthodes abstraites : `start()`, `stop()`, `produce_events()`
3. **Enregistrer** dans `producers/registry.py`
4. **Tester** avec suite tests dédiée
5. **Configurer** dans `config/*.yaml`

### Format Événement Standardisé
```python
class StandardEvent(BaseModel):
    type: str                    # EmailReceived, FileModified, etc.
    timestamp: datetime
    source: str                  # Identifiant producteur
    payload: Dict[str, Any]      # Données spécifiques événement
    correlation_id: Optional[str] = None
    priority: int = 5            # 1=highest, 10=lowest
```

## SÉCURITÉ & RÉSILIENCE

### Stratégies Défensives
- **Circuit Breaker** : Isolation producteurs défaillants
- **Retry Logic** : Tentatives multiples avec backoff exponentiel
- **Health Checks** : Surveillance périodique état composants
- **Graceful Shutdown** : Arrêt propre avec vidange files

### Gestion des Erreurs
- **Validation** : Tous événements validés avant traitement
- **Isolation** : Échec producteur n'affecte pas les autres
- **Logging** : Traçabilité complète sans exposition données sensibles
- **Recovery** : Redémarrage automatique composants défaillants

## ROADMAP

### Phase 1 : Infrastructure (Semaines 1-2)
- [ ] Implémentation bus de messages PyMQ
- [ ] Schémas événements Pydantic
- [ ] Interfaces producteurs/consommateurs
- [ ] Configuration et logging de base

### Phase 2 : Producteurs Core (Semaines 3-4)
- [ ] Producteur email IMAP avec mode IDLE
- [ ] Producteur surveillance fichiers Watchdog
- [ ] Framework producteurs programmés APScheduler
- [ ] Tests intégration producteur→bus→consommateur

### Phase 3 : Système Perception (Semaines 5-6)
- [ ] Consommateur événements unifié
- [ ] Routage événements par type
- [ ] Interface vers système de raisonnement
- [ ] Gestion priorités et back-pressure

### Phase 4 : Production Ready (Semaines 7-8)
- [ ] Circuit breaker et résilience
- [ ] Monitoring et métriques complètes
- [ ] Tests charge et performance
- [ ] Documentation utilisateur finale

## NOTES IMPORTANTES

### Points d'Attention
- **Latence Critique** : Optimiser path critique détection→traitement
- **Memory Management** : Surveiller fuites mémoire sur longues exécutions
- **Connection Health** : Robustesse connexions IMAP et services externes
- **Error Propagation** : Éviter cascade d'erreurs entre composants

### Technologies à Éviter
- **Heavy Message Brokers** : Redis/RabbitMQ trop complexes pour cas local
- **Synchronous I/O** : Privilégier asyncio pour toutes opérations I/O
- **Global State** : Minimiser état partagé entre composants
- **Blocking Operations** : Éviter blocage event loop principal

Ce projet constitue la fondation événementielle du système Mind-Mapper, permettant l'évolution vers un agent véritablement autonome et réactif.