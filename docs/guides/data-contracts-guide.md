# 📋 Guide des Contrats de Données Nexus

## Vue d'Ensemble

Ce guide définit les standards et bonnes pratiques pour la création et la gestion des **contrats de données** dans le système Nexus. Un contrat de données est un accord formel sur la structure, le format et la validation des événements échangés entre systèmes externes et Nexus.

## Table des Matières

1. [Philosophie des Contrats de Données](#philosophie-des-contrats-de-données)
2. [Architecture des Contrats](#architecture-des-contrats)
3. [Standards de Définition](#standards-de-définition)
4. [Validation et Sécurité](#validation-et-sécurité)
5. [Gestion des Versions](#gestion-des-versions)
6. [Cas d'Usage Pratiques](#cas-dusage-pratiques)
7. [Intégrations Système](#intégrations-système)
8. [Bonnes Pratiques](#bonnes-pratiques)

---

## 🎯 Philosophie des Contrats de Données

### Principe Fondamental : "Contract-First Integration"

Nexus adopte une approche **"contract-first"** où les contrats de données sont définis **avant** l'implémentation, garantissant :

- ✅ **Stabilité** : Les interfaces ne changent pas de manière imprévisible
- ✅ **Sécurité** : Validation stricte de toutes les données entrantes
- ✅ **Documentation** : Les contrats servent de documentation vivante
- ✅ **Évolutivité** : Changements contrôlés avec gestion de versions
- ✅ **Fiabilité** : Détection précoce des erreurs d'intégration

### Concepts Clés

```python
# Chaque système externe a son propre namespace de contrats
from nexus.core.contracts.parrot import ParrotNotificationEvent
from nexus.core.contracts.outlook import OutlookEmailEvent
from nexus.core.contracts.dropbox import DropboxFileEvent

# Validation automatique à la réception
event = ParrotNotificationEvent(**incoming_data)  # ✅ Valide ou lève une exception
```

---

## 🏗️ Architecture des Contrats

### Structure Hiérarchique

```
nexus/src/nexus/core/contracts/
├── __init__.py                 # Exports publics
├── base.py                     # Contrats de base et interfaces
├── parrot.py                   # Contrats système Parrot (Windows Notifications)
├── outlook.py                  # Contrats système Outlook (à venir)
├── dropbox.py                  # Contrats système Dropbox (à venir)
└── validation/                 # Validateurs personnalisés
    ├── __init__.py
    ├── email_validators.py     # Validateurs email spécialisés
    └── file_validators.py      # Validateurs fichiers spécialisés
```

### Héritage des Contrats

```python
# Hiérarchie des contrats
BaseEvent                      # Événement de base universel
├── SystemEvent                # Événement lié à un système spécifique
│   ├── ParrotEvent           # Événements système Parrot
│   │   ├── ParrotNotificationEvent
│   │   └── ParrotSystemEvent
│   ├── OutlookEvent          # Événements système Outlook
│   │   ├── OutlookEmailEvent
│   │   └── OutlookCalendarEvent
│   └── DropboxEvent          # Événements système Dropbox
│       ├── DropboxFileEvent
│       └── DropboxSyncEvent
└── InternalEvent             # Événements internes Nexus
    ├── SystemHealthEvent
    └── ErrorEvent
```

---

## 📝 Standards de Définition

### Template de Contrat Standard

```python
"""
Contrats de données pour le système [SYSTEM_NAME].

Ce module définit tous les formats d'événements que le système [SYSTEM_NAME]
peut envoyer à Nexus, avec validation automatique des payloads.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Literal, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from nexus.core.events import BaseEvent, EventType, Priority


class [SystemName]EventType(str, Enum):
    """Types d'événements spécifiques au système [SYSTEM_NAME]."""

    EVENT_TYPE_1 = "system_event_type_1"
    EVENT_TYPE_2 = "system_event_type_2"


class [SystemName]BaseEvent(BaseEvent):
    """Événement de base pour le système [SYSTEM_NAME]."""

    # Source fixe pour ce système
    source: Literal["[system_name]"] = Field("[system_name]")

    # Métadonnées système
    system_version: Optional[str] = Field(None, description="Version du système source")
    system_instance: Optional[str] = Field(None, description="Instance du système source")

    model_config = ConfigDict(
        extra='forbid',  # Rejeter les champs non définis
        str_strip_whitespace=True,
        validate_assignment=True
    )


class [SpecificEvent]Event([SystemName]BaseEvent):
    """Événement spécifique pour [SPECIFIC_PURPOSE]."""

    type: Literal[[SystemName]EventType.EVENT_TYPE_1] = Field([SystemName]EventType.EVENT_TYPE_1)

    # Payload typé et validé
    payload: [SpecificEventPayload] = Field(..., description="Données spécifiques à l'événement")

    @field_validator('payload')
    @classmethod
    def validate_payload(cls, v: [SpecificEventPayload]) -> [SpecificEventPayload]:
        """Validation personnalisée du payload."""
        # Logique de validation spécifique
        return v


class [SpecificEventPayload](BaseModel):
    """Structure du payload pour [SPECIFIC_PURPOSE]."""

    # Champs requis
    required_field: str = Field(..., min_length=1, description="Champ obligatoire")

    # Champs optionnels
    optional_field: Optional[str] = Field(None, description="Champ optionnel")

    # Validations personnalisées
    @field_validator('required_field')
    @classmethod
    def validate_required_field(cls, v: str) -> str:
        """Validation personnalisée."""
        if not v.strip():
            raise ValueError("Le champ ne peut pas être vide")
        return v.strip()

    model_config = ConfigDict(extra='forbid')
```

### Exemple Concret : Système Parrot

```python
"""
Contrats de données pour le système Parrot (Windows Notifications).

Parrot capture les notifications du Action Center de Windows et les transmet
à Nexus pour traitement selon leur type et contenu.
"""

from datetime import datetime
from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from nexus.core.events import BaseEvent, Priority


class ParrotNotificationType(str, Enum):
    """Types de notifications Windows capturées par Parrot."""

    EMAIL = "email"
    CALENDAR = "calendar"
    SYSTEM = "system"
    APP = "app"
    UNKNOWN = "unknown"


class ParrotNotificationEvent(BaseEvent):
    """Événement de notification Windows capturé par Parrot."""

    type: Literal["parrot_notification"] = Field("parrot_notification")
    source: Literal["parrot"] = Field("parrot")
    priority: Priority = Field(Priority.NORMAL)

    payload: ParrotNotificationPayload = Field(..., description="Données de la notification Windows")


class ParrotNotificationPayload(BaseModel):
    """Structure du payload pour les notifications Parrot."""

    # Données de base de la notification Windows
    notification_id: str = Field(..., description="ID unique de la notification Windows")
    app_name: str = Field(..., min_length=1, description="Nom de l'application source")
    title: str = Field(..., min_length=1, description="Titre de la notification")
    content: str = Field(..., description="Contenu de la notification")

    # Métadonnées de classification
    notification_type: ParrotNotificationType = Field(..., description="Type classifié de notification")
    captured_at: datetime = Field(..., description="Timestamp de capture par Parrot")

    # Données optionnelles
    app_icon: Optional[str] = Field(None, description="Chemin vers l'icône de l'app")
    action_buttons: Optional[list[str]] = Field(None, description="Boutons d'action disponibles")

    # Données spécialisées par type
    email_data: Optional[ParrotEmailData] = Field(None, description="Données spécifiques email si applicable")

    @field_validator('app_name', 'title')
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        """Validation que les champs importants ne sont pas vides."""
        if not v.strip():
            raise ValueError("Le champ ne peut pas être vide")
        return v.strip()

    @field_validator('email_data')
    @classmethod
    def validate_email_data_consistency(cls, v: Optional[ParrotEmailData], info) -> Optional[ParrotEmailData]:
        """Validation que email_data est cohérent avec notification_type."""
        notification_type = info.data.get('notification_type')

        if notification_type == ParrotNotificationType.EMAIL and v is None:
            raise ValueError("email_data requis pour les notifications email")

        if notification_type != ParrotNotificationType.EMAIL and v is not None:
            raise ValueError("email_data ne devrait pas être présent pour les notifications non-email")

        return v

    model_config = ConfigDict(
        extra='forbid',
        str_strip_whitespace=True
    )


class ParrotEmailData(BaseModel):
    """Données spécialisées pour les notifications email."""

    sender: str = Field(..., min_length=1, description="Expéditeur du email")
    subject: str = Field(..., min_length=1, description="Sujet du email")
    preview: Optional[str] = Field(None, description="Aperçu du contenu")

    @field_validator('sender')
    @classmethod
    def validate_sender_format(cls, v: str) -> str:
        """Validation basique du format expéditeur."""
        v = v.strip()
        if '@' not in v and '<' not in v:
            # Permettre les noms sans email (ex: "Microsoft Teams")
            pass
        return v

    model_config = ConfigDict(extra='forbid')
```

---

## 🔒 Validation et Sécurité

### Niveaux de Validation

#### 1. Validation Structurelle (Pydantic)
```python
# Automatique via les modèles Pydantic
class SecureEventPayload(BaseModel):
    # Types stricts
    user_id: int = Field(..., gt=0, description="ID utilisateur positif")
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$', description="Email valide")
    content: str = Field(..., min_length=1, max_length=1000, description="Contenu limité")

    # Prévention injection
    @field_validator('content')
    @classmethod
    def sanitize_content(cls, v: str) -> str:
        """Sanitise le contenu pour prévenir les injections."""
        # Supprimer caractères dangereux
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
        for char in dangerous_chars:
            v = v.replace(char, '')
        return v.strip()
```

#### 2. Validation Métier
```python
class BusinessValidatedEvent(BaseEvent):
    """Événement avec validation métier."""

    @field_validator('payload')
    @classmethod
    def validate_business_rules(cls, v: Dict[str, Any], info) -> Dict[str, Any]:
        """Validation des règles métier spécifiques."""

        # Exemple : validation cohérence temporelle
        if 'start_date' in v and 'end_date' in v:
            start = datetime.fromisoformat(v['start_date'])
            end = datetime.fromisoformat(v['end_date'])
            if start >= end:
                raise ValueError("La date de fin doit être postérieure à la date de début")

        # Exemple : validation droits d'accès
        if 'user_id' in v and 'resource_id' in v:
            # Vérification permissions (simulation)
            if not has_permission(v['user_id'], v['resource_id']):
                raise ValueError("Utilisateur non autorisé pour cette ressource")

        return v
```

#### 3. Validation Système
```python
class SystemValidation:
    """Validations au niveau système."""

    @staticmethod
    def validate_rate_limit(source: str, event_count: int) -> bool:
        """Validation du rate limiting par source."""
        limits = {
            'parrot': 1000,      # 1000 événements/minute max
            'outlook': 500,      # 500 événements/minute max
            'dropbox': 200       # 200 événements/minute max
        }
        return event_count <= limits.get(source, 100)

    @staticmethod
    def validate_source_authenticity(source: str, headers: Dict[str, str]) -> bool:
        """Validation de l'authenticité de la source."""
        # Vérification token API, signature, etc.
        expected_token = get_source_token(source)
        return headers.get('Authorization') == f'Bearer {expected_token}'
```

### Standards de Sécurité

```python
# Exemple de contrat sécurisé complet
class SecureParrotEvent(BaseEvent):
    """Événement Parrot avec sécurité renforcée."""

    # Champs avec validation stricte
    source: Literal["parrot"] = Field("parrot")
    payload: SecureParrotPayload = Field(...)

    # Métadonnées de sécurité
    client_ip: Optional[str] = Field(None, description="IP du client source")
    timestamp_received: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('payload')
    @classmethod
    def validate_security(cls, v: SecureParrotPayload, info) -> SecureParrotPayload:
        """Validation sécuritaire globale."""

        # Vérification taille totale payload
        payload_size = len(str(v.model_dump_json()))
        if payload_size > 10000:  # 10KB max
            raise ValueError("Payload trop volumineux")

        # Vérification patterns suspects
        content = str(v.model_dump())
        suspicious_patterns = ['javascript:', 'data:', 'vbscript:', '<script']
        for pattern in suspicious_patterns:
            if pattern.lower() in content.lower():
                raise ValueError(f"Pattern suspect détecté: {pattern}")

        return v
```

---

## 📈 Gestion des Versions

### Strategy de Versioning

#### 1. Versioning Sémantique
```python
# Version 1.0.0 - Version initiale
class ParrotNotificationEventV1(BaseEvent):
    version: Literal["1.0.0"] = Field("1.0.0")
    payload: ParrotNotificationPayloadV1


# Version 1.1.0 - Ajout champ optionnel (compatible)
class ParrotNotificationEventV1_1(BaseEvent):
    version: Literal["1.1.0"] = Field("1.1.0")
    payload: ParrotNotificationPayloadV1_1  # Hérite de V1 + nouveaux champs optionnels


# Version 2.0.0 - Changement breaking (incompatible)
class ParrotNotificationEventV2(BaseEvent):
    version: Literal["2.0.0"] = Field("2.0.0")
    payload: ParrotNotificationPayloadV2    # Structure complètement différente
```

#### 2. Support Multi-Versions
```python
# Union type pour support simultané
from typing import Union

ParrotNotificationEvent = Union[
    ParrotNotificationEventV1,
    ParrotNotificationEventV1_1,
    ParrotNotificationEventV2
]

def parse_parrot_event(data: Dict[str, Any]) -> ParrotNotificationEvent:
    """Parse automatique selon la version."""
    version = data.get('version', '1.0.0')

    version_map = {
        '1.0.0': ParrotNotificationEventV1,
        '1.1.0': ParrotNotificationEventV1_1,
        '2.0.0': ParrotNotificationEventV2
    }

    event_class = version_map.get(version)
    if not event_class:
        raise ValueError(f"Version non supportée: {version}")

    return event_class(**data)
```

#### 3. Migration Automatique
```python
class EventMigrator:
    """Migrateur automatique entre versions."""

    @staticmethod
    def migrate_v1_to_v1_1(v1_event: ParrotNotificationEventV1) -> ParrotNotificationEventV1_1:
        """Migration de v1.0.0 vers v1.1.0."""
        data = v1_event.model_dump()
        data['version'] = '1.1.0'

        # Ajout de champs par défaut pour nouveaux champs optionnels
        if 'payload' in data:
            data['payload']['new_optional_field'] = None

        return ParrotNotificationEventV1_1(**data)

    @staticmethod
    def migrate_v1_to_v2(v1_event: ParrotNotificationEventV1) -> ParrotNotificationEventV2:
        """Migration breaking de v1.x vers v2.0.0."""
        # Transformation structurelle complète
        old_data = v1_event.model_dump()

        new_data = {
            'version': '2.0.0',
            'type': 'parrot_notification_v2',
            'source': 'parrot',
            'payload': {
                # Restructuration complète des données
                'notification_info': {
                    'id': old_data['payload']['notification_id'],
                    'title': old_data['payload']['title'],
                    'content': old_data['payload']['content']
                },
                'app_info': {
                    'name': old_data['payload']['app_name'],
                    'type': old_data['payload']['notification_type']
                }
            }
        }

        return ParrotNotificationEventV2(**new_data)
```

---

## 💼 Cas d'Usage Pratiques

### Cas 1 : Notification Email Outlook via Parrot

```python
# Données reçues de Parrot
incoming_data = {
    "type": "parrot_notification",
    "source": "parrot",
    "payload": {
        "notification_id": "win_notif_12345",
        "app_name": "Microsoft Outlook",
        "title": "Nouveau message",
        "content": "De: jean.dupont@company.com\nSujet: Réunion importante demain",
        "notification_type": "email",
        "captured_at": "2024-10-25T14:30:00Z",
        "email_data": {
            "sender": "jean.dupont@company.com",
            "subject": "Réunion importante demain",
            "preview": "Bonjour, je souhaite organiser une réunion..."
        }
    }
}

# Validation automatique
try:
    event = ParrotNotificationEvent(**incoming_data)
    print("✅ Événement valide")

    # Extraction des données email pour Toasty
    if event.payload.email_data:
        toasty_title = f"📧 Email de {event.payload.email_data.sender}"
        toasty_message = event.payload.email_data.subject

        # Envoi à Toasty
        send_toasty_notification(toasty_title, toasty_message, level=0)

except ValidationError as e:
    print(f"❌ Événement invalide: {e}")
```

### Cas 2 : Notification Système Windows

```python
# Notification système (ex: mise à jour Windows)
system_notification = {
    "type": "parrot_notification",
    "source": "parrot",
    "payload": {
        "notification_id": "win_system_67890",
        "app_name": "Windows Update",
        "title": "Redémarrage requis",
        "content": "Un redémarrage est nécessaire pour terminer l'installation des mises à jour.",
        "notification_type": "system",
        "captured_at": "2024-10-25T15:45:00Z",
        "action_buttons": ["Redémarrer maintenant", "Programmer"]
    }
}

# Traitement spécialisé pour notifications système
event = ParrotNotificationEvent(**system_notification)

if event.payload.notification_type == ParrotNotificationType.SYSTEM:
    # Notification prioritaire pour événements système
    toasty_title = "🔧 Notification Système"
    toasty_message = f"{event.payload.app_name}: {event.payload.title}"

    # Niveau WARNING pour les notifications système
    send_toasty_notification(toasty_title, toasty_message, level=1)
```

### Cas 3 : Gestion d'Erreur de Contrat

```python
# Données malformées (champ manquant)
invalid_data = {
    "type": "parrot_notification",
    "source": "parrot",
    "payload": {
        "notification_id": "win_notif_invalid",
        # "app_name": manquant - ERREUR
        "title": "Test",
        "content": "Contenu test",
        "notification_type": "app",
        "captured_at": "2024-10-25T16:00:00Z"
    }
}

try:
    event = ParrotNotificationEvent(**invalid_data)
except ValidationError as e:
    # Log détaillé de l'erreur de contrat
    logger.error(f"Violation de contrat Parrot: {e}")

    # Notification d'erreur via Toasty
    send_toasty_notification(
        "❌ Erreur de Contrat",
        f"Événement Parrot invalide: {e.errors()[0]['msg']}",
        level=2
    )

    # Stockage pour analyse
    store_invalid_event("parrot", invalid_data, str(e))
```

---

## 🔗 Intégrations Système

### Intégration Toasty

```python
"""
Intégration avec le système Toasty pour notifications Windows.

Basé sur le guide C:\\repos\\toasty\\USAGE_GUIDE.md
"""

import grpc
import sys
import os
from typing import Optional

# Import des stubs Toasty (générer avec protoc)
sys.path.append('C:/repos/toasty/gen')
import notifier_pb2
import notifier_pb2_grpc


class ToastyIntegration:
    """Intégration Nexus vers Toasty."""

    def __init__(self, host: str = 'localhost', port: int = 50053):
        self.address = f'{host}:{port}'

    def send_notification(self, title: str, message: str, level: int = 0) -> bool:
        """
        Envoie une notification via Toasty.

        Args:
            title: Titre de la notification
            message: Contenu de la notification
            level: Niveau (0=INFO, 1=WARNING, 2=ERROR)

        Returns:
            True si succès, False sinon
        """
        try:
            with grpc.insecure_channel(self.address) as channel:
                stub = notifier_pb2_grpc.NotifierStub(channel)

                request = notifier_pb2.NotificationRequest(
                    title=title,
                    message=message,
                    level=level
                )

                response = stub.SendNotification(request)

                if response.success:
                    logger.info(f"Notification Toasty envoyée: {title}")
                    return True
                else:
                    logger.error(f"Erreur Toasty: {response.error_message}")
                    return False

        except Exception as e:
            logger.error(f"Erreur connexion Toasty: {e}")
            return False


# Processeur spécialisé pour événements Parrot → Toasty
class ParrotToToastyProcessor:
    """Processeur qui convertit les événements Parrot en notifications Toasty."""

    def __init__(self):
        self.toasty = ToastyIntegration()

    def process(self, event: ParrotNotificationEvent) -> bool:
        """
        Traite un événement Parrot et envoie une notification Toasty.

        Args:
            event: Événement Parrot validé

        Returns:
            True si traitement réussi
        """
        try:
            # Extraction et formatage des données
            title, message, level = self._format_notification(event)

            # Envoi via Toasty
            success = self.toasty.send_notification(title, message, level)

            if success:
                logger.info(f"Événement Parrot traité: {event.payload.notification_id}")

            return success

        except Exception as e:
            logger.error(f"Erreur traitement événement Parrot: {e}")
            return False

    def _format_notification(self, event: ParrotNotificationEvent) -> tuple[str, str, int]:
        """
        Formate un événement Parrot en notification Toasty.

        Returns:
            (title, message, level) pour Toasty
        """
        payload = event.payload

        # Formatage selon le type de notification
        if payload.notification_type == ParrotNotificationType.EMAIL:
            if payload.email_data:
                title = f"📧 {payload.email_data.sender}"
                message = payload.email_data.subject
                level = 0  # INFO pour emails
            else:
                title = f"📧 {payload.app_name}"
                message = payload.title
                level = 0

        elif payload.notification_type == ParrotNotificationType.CALENDAR:
            title = f"📅 {payload.app_name}"
            message = payload.title
            level = 1  # WARNING pour événements calendrier

        elif payload.notification_type == ParrotNotificationType.SYSTEM:
            title = f"🔧 {payload.app_name}"
            message = payload.title
            level = 1  # WARNING pour notifications système

        else:  # APP ou UNKNOWN
            title = f"📱 {payload.app_name}"
            message = payload.title
            level = 0  # INFO par défaut

        # Limitation des longueurs pour Toasty
        title = title[:80] if len(title) > 80 else title
        message = message[:200] if len(message) > 200 else message

        return title, message, level
```

### Factory de Processeurs

```python
"""
Factory pattern pour la gestion des processeurs par type d'événement.
"""

class ProcessorFactory:
    """Factory pour créer les processeurs appropriés selon l'événement."""

    _processors = {
        'parrot_notification': ParrotToToastyProcessor,
        # Futurs processeurs
        'outlook_email': OutlookEmailProcessor,
        'dropbox_file': DropboxFileProcessor,
    }

    @classmethod
    def get_processor(cls, event_type: str):
        """Retourne le processeur approprié pour un type d'événement."""
        processor_class = cls._processors.get(event_type)
        if not processor_class:
            raise ValueError(f"Aucun processeur défini pour le type: {event_type}")

        return processor_class()

    @classmethod
    def register_processor(cls, event_type: str, processor_class):
        """Enregistre un nouveau processeur pour un type d'événement."""
        cls._processors[event_type] = processor_class
```

---

## ✨ Bonnes Pratiques

### 1. Conception des Contrats

#### ✅ À Faire
```python
# Contrats spécifiques et typés
class EmailNotificationPayload(BaseModel):
    sender: str = Field(..., min_length=1, description="Expéditeur du email")
    subject: str = Field(..., min_length=1, description="Sujet du email")
    received_at: datetime = Field(..., description="Date de réception")

# Validation métier
@field_validator('sender')
@classmethod
def validate_sender(cls, v: str) -> str:
    if '@' not in v and '<' not in v:
        # Autoriser noms d'affichage sans email
        pass
    return v.strip()
```

#### ❌ À Éviter
```python
# Contrats trop génériques
class GenericPayload(BaseModel):
    data: Dict[str, Any]  # ❌ Trop vague
    info: Optional[str]   # ❌ Nom non descriptif

# Pas de validation
class UnsafePayload(BaseModel):
    content: str  # ❌ Pas de limites de taille, pas de sanitisation
```

### 2. Gestion d'Erreurs

#### ✅ Stratégie Robuste
```python
def process_event_safely(raw_data: Dict[str, Any]) -> bool:
    """Traitement sécurisé avec gestion d'erreurs complète."""

    try:
        # 1. Validation du contrat
        event = parse_event_by_type(raw_data)

        # 2. Validation métier supplémentaire
        validate_business_rules(event)

        # 3. Traitement
        processor = ProcessorFactory.get_processor(event.type)
        success = processor.process(event)

        # 4. Logging de succès
        logger.info(f"Événement traité: {event.event_id}")
        return success

    except ValidationError as e:
        # Erreur de contrat - critique
        logger.error(f"Violation de contrat: {e}")
        metrics.increment('contract_violations', tags={'source': raw_data.get('source')})
        return False

    except BusinessRuleError as e:
        # Erreur métier - important mais pas critique
        logger.warning(f"Règle métier violée: {e}")
        metrics.increment('business_rule_violations')
        return False

    except Exception as e:
        # Erreur système - critique
        logger.error(f"Erreur système: {e}", exc_info=True)
        metrics.increment('system_errors')
        return False
```

### 3. Performance et Optimisation

#### Validation Asynchrone
```python
import asyncio
from typing import List

async def validate_events_batch(events: List[Dict[str, Any]]) -> List[BaseEvent]:
    """Validation asynchrone par batch pour performance."""

    async def validate_single(event_data: Dict[str, Any]) -> Optional[BaseEvent]:
        try:
            # Validation dans une tâche asynchrone
            return await asyncio.to_thread(parse_event_by_type, event_data)
        except ValidationError:
            return None

    # Validation en parallèle
    tasks = [validate_single(event) for event in events]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filtrer les événements valides
    valid_events = [event for event in results if isinstance(event, BaseEvent)]

    return valid_events
```

#### Cache de Validation
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def get_cached_validator(event_type: str, schema_hash: str):
    """Cache des validateurs pour éviter la recompilation."""
    return ProcessorFactory.get_processor(event_type)

def get_schema_hash(event_data: Dict[str, Any]) -> str:
    """Hash du schéma pour mise en cache."""
    schema_keys = sorted(event_data.keys())
    return hashlib.md5(str(schema_keys).encode()).hexdigest()
```

### 4. Testing des Contrats

```python
import pytest
from nexus.core.contracts.parrot import ParrotNotificationEvent

class TestParrotContracts:
    """Tests complets des contrats Parrot."""

    def test_valid_email_notification(self):
        """Test événement email valide."""
        data = {
            "type": "parrot_notification",
            "source": "parrot",
            "payload": {
                "notification_id": "test_123",
                "app_name": "Outlook",
                "title": "Nouveau message",
                "content": "Vous avez un nouveau message",
                "notification_type": "email",
                "captured_at": "2024-10-25T10:00:00Z",
                "email_data": {
                    "sender": "test@example.com",
                    "subject": "Test Subject",
                    "preview": "Test preview"
                }
            }
        }

        event = ParrotNotificationEvent(**data)
        assert event.payload.notification_type == "email"
        assert event.payload.email_data.sender == "test@example.com"

    def test_invalid_missing_field(self):
        """Test gestion champ manquant."""
        data = {
            "type": "parrot_notification",
            "source": "parrot",
            "payload": {
                # "notification_id" manquant
                "app_name": "Outlook",
                "title": "Test",
                "content": "Test content",
                "notification_type": "email",
                "captured_at": "2024-10-25T10:00:00Z"
            }
        }

        with pytest.raises(ValidationError) as exc_info:
            ParrotNotificationEvent(**data)

        assert "notification_id" in str(exc_info.value)

    def test_email_data_consistency(self):
        """Test cohérence email_data avec notification_type."""
        data = {
            "type": "parrot_notification",
            "source": "parrot",
            "payload": {
                "notification_id": "test_456",
                "app_name": "Outlook",
                "title": "Email notification",
                "content": "Content",
                "notification_type": "email",  # Type email
                "captured_at": "2024-10-25T10:00:00Z"
                # email_data manquant - devrait échouer
            }
        }

        with pytest.raises(ValidationError) as exc_info:
            ParrotNotificationEvent(**data)

        assert "email_data requis" in str(exc_info.value)
```

### 5. Documentation Automatique

```python
def generate_contract_documentation():
    """Génère la documentation des contrats à partir des modèles Pydantic."""

    contracts = [
        ParrotNotificationEvent,
        # Autres contrats...
    ]

    for contract in contracts:
        schema = contract.model_json_schema()

        # Génération documentation markdown
        doc = f"""
# {contract.__name__}

## Description
{contract.__doc__}

## Schema JSON
```json
{json.dumps(schema, indent=2)}
```

## Exemple
```python
{generate_example(contract)}
```
        """

        # Sauvegarde
        with open(f'docs/contracts/{contract.__name__.lower()}.md', 'w') as f:
            f.write(doc)
```

---

## 📞 Support et Évolution

### Processus de Modification des Contrats

1. **Proposition** : Issue GitHub avec spécification détaillée
2. **Review** : Validation par l'équipe architecture
3. **Implementation** : Développement avec tests complets
4. **Migration** : Plan de migration pour versions existantes
5. **Documentation** : Mise à jour guides et exemples

### Contact

- **Repository** : [https://github.com/amsolg/nexus](https://github.com/amsolg/nexus)
- **Documentation** : `docs/guides/` dans le repository
- **Issues** : GitHub Issues pour bugs et améliorations

---

**Guide des Contrats de Données Nexus** - Version 1.0.0
Système de traitement événementiel centralisé avec validation stricte et intégrations sécurisées.