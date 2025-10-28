"""
Schémas d'événements standardisés pour le système Nexus.

Ce module définit les structures de données pour tous les événements
qui transitent dans le système événementiel Nexus.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Literal, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EventType(str, Enum):
    """Types d'événements supportés par le système."""

    EMAIL_RECEIVED = "email_received"
    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    SCHEDULED_TASK = "scheduled_task"
    CALENDAR_EVENT = "calendar_event"
    SYSTEM_HEALTH = "system_health"
    ERROR_OCCURRED = "error_occurred"


class Priority(int, Enum):
    """Niveaux de priorité des événements."""

    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class BaseEvent(BaseModel):
    """Schéma de base pour tous les événements du système."""

    event_id: str = Field(default_factory=lambda: str(uuid4()), description="Identifiant unique de l'événement")
    type: EventType = Field(..., description="Type de l'événement")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Horodatage UTC de création")
    source: str = Field(..., description="Identifiant du producteur source")
    correlation_id: Optional[str] = Field(None, description="ID de corrélation pour traçage")
    priority: Priority = Field(Priority.NORMAL, description="Niveau de priorité")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Données spécifiques à l'événement")

    model_config = ConfigDict(
        use_enum_values=True,
        ser_json_timedelta='iso8601',
        json_schema_extra={
            "examples": [
                {
                    "event_id": "550e8400-e29b-41d4-a716-446655440000",
                    "type": "email_received",
                    "timestamp": "2023-10-24T10:00:00Z",
                    "source": "imap_producer",
                    "priority": 3,
                    "payload": {"from": "user@example.com", "subject": "Test"}
                }
            ]
        }
    )

    @field_validator('source')
    @classmethod
    def validate_source(cls, v: str) -> str:
        """Valide que la source n'est pas vide."""
        if not v or not v.strip():
            raise ValueError("Source cannot be empty")
        return v.strip()

    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: datetime) -> datetime:
        """Valide que le timestamp n'est pas dans le futur."""
        if v > datetime.utcnow():
            raise ValueError("Timestamp cannot be in the future")
        return v


class EmailEvent(BaseEvent):
    """Événement pour les emails reçus."""

    type: Literal[EventType.EMAIL_RECEIVED] = Field(EventType.EMAIL_RECEIVED)

    def __init__(self, **data):
        super().__init__(**data)
        # Validation spécifique aux emails
        required_fields = ['from', 'subject', 'received_at']
        for field in required_fields:
            if field not in self.payload:
                raise ValueError(f"Email event must contain '{field}' in payload")


class FileEvent(BaseEvent):
    """Événement pour les modifications de fichiers."""

    type: EventType = Field(..., description="Type spécifique de modification fichier")

    def __init__(self, **data):
        super().__init__(**data)
        # Validation du type pour les événements fichier
        file_types = {EventType.FILE_CREATED, EventType.FILE_MODIFIED, EventType.FILE_DELETED}
        if self.type not in file_types:
            raise ValueError(f"FileEvent type must be one of {file_types}")

        # Validation du payload
        if 'file_path' not in self.payload:
            raise ValueError("File event must contain 'file_path' in payload")


class ScheduledEvent(BaseEvent):
    """Événement pour les tâches programmées."""

    type: Literal[EventType.SCHEDULED_TASK] = Field(EventType.SCHEDULED_TASK)

    def __init__(self, **data):
        super().__init__(**data)
        # Validation spécifique aux tâches programmées
        required_fields = ['task_id', 'scheduled_time']
        for field in required_fields:
            if field not in self.payload:
                raise ValueError(f"Scheduled event must contain '{field}' in payload")


class SystemHealthEvent(BaseEvent):
    """Événement pour le monitoring de santé système."""

    type: Literal[EventType.SYSTEM_HEALTH] = Field(EventType.SYSTEM_HEALTH)
    priority: Priority = Field(Priority.BACKGROUND)  # Priorité par défaut mais modifiable

    def __init__(self, **data):
        super().__init__(**data)
        # Validation spécifique au health check
        required_fields = ['component', 'status', 'metrics']
        for field in required_fields:
            if field not in self.payload:
                raise ValueError(f"Health event must contain '{field}' in payload")


class ErrorEvent(BaseEvent):
    """Événement pour les erreurs système."""

    type: Literal[EventType.ERROR_OCCURRED] = Field(EventType.ERROR_OCCURRED)
    priority: Priority = Field(Priority.HIGH)  # Priorité par défaut mais modifiable

    def __init__(self, **data):
        super().__init__(**data)
        # Validation spécifique aux erreurs
        required_fields = ['error_type', 'message', 'component']
        for field in required_fields:
            if field not in self.payload:
                raise ValueError(f"Error event must contain '{field}' in payload")


# Type union pour tous les événements
Event = Union[BaseEvent, EmailEvent, FileEvent, ScheduledEvent, SystemHealthEvent, ErrorEvent]


def create_event(event_type: EventType, source: str, payload: Dict[str, Any], **kwargs) -> Event:
    """
    Factory function pour créer des événements typés.

    Args:
        event_type: Type d'événement à créer
        source: Identifiant du producteur source
        payload: Données spécifiques à l'événement
        **kwargs: Paramètres additionnels (correlation_id, priority, etc.)

    Returns:
        Instance d'événement du type approprié

    Raises:
        ValueError: Si le type d'événement n'est pas supporté
    """
    base_data = {
        'type': event_type,
        'source': source,
        'payload': payload,
        **kwargs
    }

    # Mapping des types vers les classes spécialisées
    event_classes = {
        EventType.EMAIL_RECEIVED: EmailEvent,
        EventType.FILE_CREATED: FileEvent,
        EventType.FILE_MODIFIED: FileEvent,
        EventType.FILE_DELETED: FileEvent,
        EventType.SCHEDULED_TASK: ScheduledEvent,
        EventType.SYSTEM_HEALTH: SystemHealthEvent,
        EventType.ERROR_OCCURRED: ErrorEvent,
        EventType.CALENDAR_EVENT: BaseEvent,  # Utilise BaseEvent pour l'instant
    }

    event_class = event_classes.get(event_type, BaseEvent)
    return event_class(**base_data)