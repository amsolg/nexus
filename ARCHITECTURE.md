# ARCHITECTURE - NEXUS

## Vue d'Ensemble
Nexus est un système de traitement événementiel centralisé utilisant une architecture event-driven pour transformer des agents IA passifs en systèmes proactifs et réactifs. Le système utilise un pattern de hub centralisé avec des producteurs d'événements découplés et des processeurs spécialisés, suivant une approche "contract-first" pour garantir la stabilité et la sécurité des intégrations.

## Spécifications Techniques

### Stack Technologique Core
- **Runtime** : Python 3.11+ avec support asyncio optimisé pour performances maximales
- **Validation** : Pydantic pour contrats de données stricts et validation automatique
- **Logging** : structlog pour observabilité structurée et traçabilité complète
- **Queue** : asyncio.Queue native pour traitement FIFO séquentiel garanti
- **Transport** : HTTP/WebSocket pour réception d'événements des systèmes externes
- **Sérialisation** : JSON pour format standardisé d'interopérabilité

### Patterns Architecturaux Implémentés

#### Pattern Principal : Centralized Event Processing
- **Hub centralisé** : Point d'entrée unique pour tous les événements systèmes
- **Contrats stricts** : Validation automatique Pydantic avec gestion des versions
- **Traitement personnalisé** : Processeurs spécialisés par type d'événement et système source
- **Isolation des erreurs** : Échec d'un composant n'affecte pas les autres

#### Patterns Secondaires
- **Strategy Pattern** : Processeurs spécialisés enregistrés dans un registre centralisé
- **Circuit Breaker** : Isolation automatique des intégrations externes défaillantes
- **Contract-First Integration** : Définition et validation des contrats avant implémentation
- **Queue Processing** : Traitement FIFO avec gestion de la back-pressure
- **Factory Pattern** : Création dynamique des processeurs selon le type d'événement

### Architecture des Composants

```
┌─────────────────────────────────────────────────────────────────────┐
│                           SYSTÈMES EXTERNES                         │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   PARROT    │  │  OUTLOOK    │  │  DROPBOX    │  │   AUTRES    │ │
│  │(Notifications│  │  (Email)    │  │  (Files)    │  │  SYSTÈMES   │ │
│  │  Windows)   │  │             │  │             │  │             │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │
└─────────┼─────────────────┼─────────────────┼─────────────────┼─────┘
          │                 │                 │                 │
          │        ┌────────▼─────────────────▼─────────────────▼──┐
          │        │            API RECEIVER LAYER                │
          └────────┤  • HTTP/WebSocket endpoints                  │
                   │  • Validation middleware                     │
                   │  • Security & authentication                 │
                   │  • Request routing                           │
                   └─────────────────┬────────────────────────────┘
                                     │
                   ┌─────────────────▼────────────────────────────┐
                   │           VALIDATION LAYER                   │
                   │  • Contract validation (Pydantic)           │
                   │  • Business rules validation                │
                   │  • Rate limiting                             │
                   │  • Payload sanitization                     │
                   └─────────────────┬────────────────────────────┘
                                     │
                   ┌─────────────────▼────────────────────────────┐
                   │            EVENT QUEUE LAYER                 │
                   │  • FIFO queue (asyncio.Queue)               │
                   │  • Event persistence                        │
                   │  • Priority handling                        │
                   │  • Back-pressure management                 │
                   └─────────────────┬────────────────────────────┘
                                     │
                   ┌─────────────────▼────────────────────────────┐
                   │          PROCESSING LAYER                    │
                   │  • Processor registry                       │
                   │  • Event type routing                       │
                   │  • Specialized processors                   │
                   │  • Error isolation                          │
                   └─────────────────┬────────────────────────────┘
                                     │
┌─────────────────────────────────────▼─────────────────────────────────────┐
│                       INTEGRATION LAYER                                   │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   TOASTY    │  │  LANGGRAPH  │  │   FUTURE    │  │   FUTURE    │      │
│  │(Notifications│  │ (Reasoning) │  │INTEGRATION 1│  │INTEGRATION 2│      │
│  │  Windows)   │  │             │  │             │  │             │      │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
```

## Interfaces et Contrats

### Contrat Événement Standard (BaseEvent)
```python
class BaseEvent(BaseModel):
    """Événement de base pour tous les événements Nexus."""

    # Identification unique
    event_id: str = Field(default_factory=lambda: str(uuid4()))

    # Métadonnées obligatoires
    type: str = Field(..., description="Type de l'événement")
    source: str = Field(..., description="Système source de l'événement")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Priorité et corrélation
    priority: Priority = Field(Priority.NORMAL)
    correlation_id: Optional[str] = Field(None)

    # Données spécifiques (à définir dans les classes dérivées)
    payload: Dict[str, Any] = Field(..., description="Données spécifiques à l'événement")
```

### Interface Processeur Abstrait
```python
class AbstractProcessor(ABC):
    """Interface de base pour tous les processeurs d'événements."""

    @abstractmethod
    async def process_event(self, event: BaseEvent) -> ProcessingResult:
        """Traite un événement spécifique."""
        pass

    @abstractmethod
    def can_handle(self, event_type: str) -> bool:
        """Détermine si le processeur peut traiter ce type d'événement."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Vérifie la santé du processeur."""
        pass
```

### Interface Intégration Externe
```python
class AbstractIntegration(ABC):
    """Interface de base pour les intégrations externes."""

    @abstractmethod
    async def send_notification(self, payload: Dict[str, Any]) -> IntegrationResult:
        """Envoie une notification via l'intégration."""
        pass

    @abstractmethod
    async def health_check(self) -> HealthStatus:
        """Vérifie la santé de l'intégration."""
        pass

    @abstractmethod
    async def circuit_breaker_status(self) -> CircuitBreakerStatus:
        """Retourne l'état du circuit breaker."""
        pass
```

## Flux de Données et Traitement

### 1. Réception d'Événement
```
Système Externe → API Receiver → Middleware Sécurité → Validation Contrat → Event Queue
     |                |               |                    |                |
   (JSON)        (HTTP/WS)      (Auth/Rate)         (Pydantic)      (asyncio.Queue)
```

### 2. Traitement Événement
```
Event Queue → Processor Registry → Processeur Spécialisé → Intégration → Système Cible
     |              |                      |                   |           |
  (BaseEvent)   (Type Routing)        (Business Logic)    (API Call)   (Toasty/etc)
```

### 3. Gestion d'Erreurs
```
Erreur → Circuit Breaker → Retry Logic → Dead Letter Queue → Alert System
  |           |              |              |                  |
(Exception) (Isolation)   (Backoff)    (Storage)         (Monitoring)
```

## Contraintes Système et Exigences de Performance

### Contraintes de Performance
- **Latence Critique** : <100ms de réception à traitement complet
- **Débit Système** : Support minimum de 100 événements/seconde
- **Disponibilité** : 99.9% uptime pour le bus de messages
- **Efficacité** : 90% réduction CPU vs polling traditionnel

### Contraintes de Ressources
- **Mémoire Queue** : Limite configurable pour éviter l'overflow (défaut : 1000 événements)
- **CPU Usage** : Utilisation asyncio pour opérations non-bloquantes
- **Network I/O** : Connexions persistantes avec pool de connexions
- **Storage** : Persistence optionnelle avec rotation automatique

### Contraintes de Résilience
- **Circuit Breaker** : Isolation automatique des composants défaillants (seuil : 5 échecs/minute)
- **Retry Logic** : Maximum 3 tentatives avec backoff exponentiel (1s, 2s, 4s)
- **Graceful Shutdown** : Arrêt propre avec vidange complète des files (timeout : 30s)
- **Health Monitoring** : Surveillance continue avec alertes automatiques

## Sécurité et Validation

### Niveaux de Validation
1. **Structurelle** : Validation automatique Pydantic des types et formats
2. **Métier** : Règles de validation spécifiques au domaine
3. **Sécurité** : Sanitisation, limites de taille, patterns suspects
4. **Système** : Rate limiting, authentification, autorisation

### Stratégies de Sécurité
- **Validation Stricte** : Tous les événements validés avant traitement (mode `extra='forbid'`)
- **Isolation Composants** : Échec d'un producteur n'affecte pas les autres
- **Logging Sécurisé** : Traçabilité complète sans exposition de données sensibles
- **Recovery Automatique** : Redémarrage automatique des composants défaillants

## Dépendances et Intégrations

### Dépendances Internes
- **src/nexus/core/** : Schémas d'événements et configuration centralisée
- **src/nexus/api/** : Interface de réception et middleware
- **src/nexus/queue/** : Système de queue et gestionnaire
- **src/nexus/processors/** : Logique de traitement et registre
- **src/nexus/integrations/** : Connecteurs vers systèmes externes

### Dépendances Externes Principales
- **Toasty** : Système de notifications Windows (c:/repos/toasty/) via gRPC
- **Systèmes Producteurs** : Parrot, Outlook, Dropbox, autres sources d'événements
- **Configuration** : Fichiers YAML dans config/ pour paramétrage environnement

### Dépendances Technologiques Critiques
- **Python 3.11+** : Runtime principal avec optimisations asyncio
- **Pydantic v2** : Validation ultra-rapide et sérialisation
- **structlog** : Logging structuré JSON pour observabilité
- **asyncio** : Boucle d'événements pour programmation asynchrone
- **YAML** : Configuration déclarative et environnements multiples
- **gRPC** : Communication haute performance avec Toasty

## Extensibilité et Évolution

### Ajout de Nouveaux Producteurs
1. **Définir contrats** : Créer schemas Pydantic dans `contracts/`
2. **Implémenter processeur** : Hériter de `AbstractProcessor`
3. **Enregistrer dans factory** : Ajouter au `ProcessorRegistry`
4. **Tester intégration** : Suite de tests complète
5. **Configurer environnement** : Mise à jour fichiers YAML

### Versioning des Contrats
- **Sémantique** : Versions compatibles (1.x.x) vs breaking (2.0.0)
- **Support Multi-versions** : Union types pour rétrocompatibilité
- **Migration Automatique** : Transformateurs entre versions
- **Dépréciation Progressive** : Cycle de vie planifié des anciennes versions

### Monitoring et Observabilité
- **Métriques Système** : Latence, débit, taux d'erreur, santé composants
- **Traces Distribuées** : Corrélation des événements bout-en-bout
- **Alertes Intelligentes** : Seuils adaptatifs et escalade automatique
- **Dashboards Temps Réel** : Visualisation de l'état système