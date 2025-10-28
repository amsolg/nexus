"""
Tests unitaires pour les schémas d'événements Nexus.
"""

import json
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError

from nexus.core.events import (
    BaseEvent,
    EmailEvent,
    ErrorEvent,
    Event,
    EventType,
    FileEvent,
    Priority,
    ScheduledEvent,
    SystemHealthEvent,
    create_event,
)


class TestBaseEvent:
    """Tests pour la classe BaseEvent."""

    def test_base_event_creation_minimal(self):
        """Test création d'un événement avec paramètres minimaux."""
        event = BaseEvent(
            type=EventType.EMAIL_RECEIVED,
            source="test_producer"
        )

        assert event.type == EventType.EMAIL_RECEIVED
        assert event.source == "test_producer"
        assert event.priority == Priority.NORMAL
        assert event.payload == {}
        assert event.correlation_id is None
        assert isinstance(event.event_id, str)
        assert isinstance(event.timestamp, datetime)

    def test_base_event_creation_complete(self):
        """Test création d'un événement avec tous les paramètres."""
        correlation_id = str(uuid4())
        payload = {"key": "value", "number": 42}
        timestamp = datetime.utcnow()

        event = BaseEvent(
            type=EventType.FILE_CREATED,
            source="file_watcher",
            correlation_id=correlation_id,
            priority=Priority.HIGH,
            payload=payload,
            timestamp=timestamp
        )

        assert event.type == EventType.FILE_CREATED
        assert event.source == "file_watcher"
        assert event.correlation_id == correlation_id
        assert event.priority == Priority.HIGH
        assert event.payload == payload
        assert event.timestamp == timestamp

    def test_event_id_uniqueness(self):
        """Test que chaque événement a un ID unique."""
        event1 = BaseEvent(type=EventType.EMAIL_RECEIVED, source="test")
        event2 = BaseEvent(type=EventType.EMAIL_RECEIVED, source="test")

        assert event1.event_id != event2.event_id

    def test_source_validation_empty(self):
        """Test validation source vide."""
        with pytest.raises(ValidationError, match="Source cannot be empty"):
            BaseEvent(type=EventType.EMAIL_RECEIVED, source="")

    def test_source_validation_whitespace(self):
        """Test validation source avec espaces."""
        with pytest.raises(ValidationError, match="Source cannot be empty"):
            BaseEvent(type=EventType.EMAIL_RECEIVED, source="   ")

    def test_source_trimming(self):
        """Test que la source est automatiquement trimée."""
        event = BaseEvent(type=EventType.EMAIL_RECEIVED, source="  test_source  ")
        assert event.source == "test_source"

    def test_timestamp_validation_future(self):
        """Test validation timestamp futur."""
        future_time = datetime.utcnow() + timedelta(hours=1)
        with pytest.raises(ValidationError, match="Timestamp cannot be in the future"):
            BaseEvent(
                type=EventType.EMAIL_RECEIVED,
                source="test",
                timestamp=future_time
            )

    def test_json_serialization(self):
        """Test sérialisation JSON."""
        event = BaseEvent(
            type=EventType.EMAIL_RECEIVED,
            source="test_producer",
            payload={"test": "data"}
        )

        json_str = event.model_dump_json()
        data = json.loads(json_str)

        assert data["type"] == "email_received"
        assert data["source"] == "test_producer"
        assert data["payload"] == {"test": "data"}
        assert "timestamp" in data
        assert "event_id" in data

    def test_dict_conversion(self):
        """Test conversion en dictionnaire."""
        event = BaseEvent(
            type=EventType.FILE_MODIFIED,
            source="file_watcher"
        )

        event_dict = event.model_dump()

        assert event_dict["type"] == "file_modified"
        assert event_dict["source"] == "file_watcher"
        assert isinstance(event_dict["timestamp"], datetime)


class TestEmailEvent:
    """Tests pour la classe EmailEvent."""

    def test_email_event_creation_valid(self):
        """Test création d'un événement email valide."""
        payload = {
            "from": "sender@example.com",
            "subject": "Test Subject",
            "received_at": "2023-10-24T10:00:00Z"
        }

        event = EmailEvent(source="imap_producer", payload=payload)

        assert event.type == EventType.EMAIL_RECEIVED
        assert event.source == "imap_producer"
        assert event.payload == payload

    def test_email_event_missing_required_fields(self):
        """Test validation champs requis manquants."""
        # Manque 'from'
        with pytest.raises(ValueError, match="Email event must contain 'from' in payload"):
            EmailEvent(
                source="imap_producer",
                payload={"subject": "Test", "received_at": "2023-10-24T10:00:00Z"}
            )

        # Manque 'subject'
        with pytest.raises(ValueError, match="Email event must contain 'subject' in payload"):
            EmailEvent(
                source="imap_producer",
                payload={"from": "test@example.com", "received_at": "2023-10-24T10:00:00Z"}
            )

        # Manque 'received_at'
        with pytest.raises(ValueError, match="Email event must contain 'received_at' in payload"):
            EmailEvent(
                source="imap_producer",
                payload={"from": "test@example.com", "subject": "Test"}
            )

    def test_email_event_type_immutable(self):
        """Test que le type d'événement email est fixe."""
        payload = {
            "from": "sender@example.com",
            "subject": "Test Subject",
            "received_at": "2023-10-24T10:00:00Z"
        }

        event = EmailEvent(source="imap_producer", payload=payload)
        assert event.type == EventType.EMAIL_RECEIVED


class TestFileEvent:
    """Tests pour la classe FileEvent."""

    def test_file_event_creation_valid(self):
        """Test création d'événements fichier valides."""
        payload = {"file_path": "/path/to/file.txt", "size": 1024}

        for event_type in [EventType.FILE_CREATED, EventType.FILE_MODIFIED, EventType.FILE_DELETED]:
            event = FileEvent(
                type=event_type,
                source="file_watcher",
                payload=payload
            )
            assert event.type == event_type
            assert event.payload == payload

    def test_file_event_invalid_type(self):
        """Test validation type d'événement invalide."""
        payload = {"file_path": "/path/to/file.txt"}

        with pytest.raises(ValueError, match="FileEvent type must be one of"):
            FileEvent(
                type=EventType.EMAIL_RECEIVED,  # Type invalide pour FileEvent
                source="file_watcher",
                payload=payload
            )

    def test_file_event_missing_file_path(self):
        """Test validation file_path manquant."""
        with pytest.raises(ValueError, match="File event must contain 'file_path' in payload"):
            FileEvent(
                type=EventType.FILE_CREATED,
                source="file_watcher",
                payload={"size": 1024}  # Manque file_path
            )


class TestScheduledEvent:
    """Tests pour la classe ScheduledEvent."""

    def test_scheduled_event_creation_valid(self):
        """Test création d'un événement programmé valide."""
        payload = {
            "task_id": "backup_task_001",
            "scheduled_time": "2023-10-24T15:00:00Z"
        }

        event = ScheduledEvent(source="scheduler", payload=payload)

        assert event.type == EventType.SCHEDULED_TASK
        assert event.payload == payload

    def test_scheduled_event_missing_required_fields(self):
        """Test validation champs requis manquants."""
        # Manque 'task_id'
        with pytest.raises(ValueError, match="Scheduled event must contain 'task_id' in payload"):
            ScheduledEvent(
                source="scheduler",
                payload={"scheduled_time": "2023-10-24T15:00:00Z"}
            )

        # Manque 'scheduled_time'
        with pytest.raises(ValueError, match="Scheduled event must contain 'scheduled_time' in payload"):
            ScheduledEvent(
                source="scheduler",
                payload={"task_id": "backup_task_001"}
            )


class TestSystemHealthEvent:
    """Tests pour la classe SystemHealthEvent."""

    def test_health_event_creation_valid(self):
        """Test création d'un événement de santé valide."""
        payload = {
            "component": "database",
            "status": "healthy",
            "metrics": {"cpu": 45.2, "memory": 67.8}
        }

        event = SystemHealthEvent(source="health_monitor", payload=payload)

        assert event.type == EventType.SYSTEM_HEALTH
        assert event.priority == Priority.BACKGROUND
        assert event.payload == payload

    def test_health_event_missing_required_fields(self):
        """Test validation champs requis manquants."""
        # Manque 'component'
        with pytest.raises(ValueError, match="Health event must contain 'component' in payload"):
            SystemHealthEvent(
                source="health_monitor",
                payload={"status": "healthy", "metrics": {}}
            )


class TestErrorEvent:
    """Tests pour la classe ErrorEvent."""

    def test_error_event_creation_valid(self):
        """Test création d'un événement d'erreur valide."""
        payload = {
            "error_type": "ConnectionError",
            "message": "Failed to connect to database",
            "component": "database_connector"
        }

        event = ErrorEvent(source="error_handler", payload=payload)

        assert event.type == EventType.ERROR_OCCURRED
        assert event.priority == Priority.HIGH
        assert event.payload == payload

    def test_error_event_missing_required_fields(self):
        """Test validation champs requis manquants."""
        # Manque 'error_type'
        with pytest.raises(ValueError, match="Error event must contain 'error_type' in payload"):
            ErrorEvent(
                source="error_handler",
                payload={"message": "Error occurred", "component": "test"}
            )


class TestCreateEventFactory:
    """Tests pour la fonction factory create_event."""

    def test_create_base_event(self):
        """Test création d'événement de base."""
        event = create_event(
            event_type=EventType.CALENDAR_EVENT,
            source="calendar_sync",
            payload={"event_id": "cal_123"}
        )

        assert isinstance(event, BaseEvent)
        assert event.type == EventType.CALENDAR_EVENT
        assert event.source == "calendar_sync"

    def test_create_specialized_event(self):
        """Test création d'événements spécialisés."""
        # Email event
        email_event = create_event(
            event_type=EventType.EMAIL_RECEIVED,
            source="imap_producer",
            payload={
                "from": "test@example.com",
                "subject": "Test",
                "received_at": "2023-10-24T10:00:00Z"
            }
        )
        assert isinstance(email_event, EmailEvent)

        # File event
        file_event = create_event(
            event_type=EventType.FILE_CREATED,
            source="file_watcher",
            payload={"file_path": "/test/file.txt"}
        )
        assert isinstance(file_event, FileEvent)

    def test_create_event_with_kwargs(self):
        """Test création d'événement avec paramètres additionnels."""
        correlation_id = str(uuid4())

        event = create_event(
            event_type=EventType.SYSTEM_HEALTH,
            source="health_monitor",
            payload={
                "component": "api_server",
                "status": "healthy",
                "metrics": {"uptime": 3600}
            },
            correlation_id=correlation_id,
            priority=Priority.LOW
        )

        assert isinstance(event, SystemHealthEvent)
        assert event.correlation_id == correlation_id
        assert event.priority == Priority.LOW


class TestEnumValues:
    """Tests pour les énumérations."""

    def test_event_type_values(self):
        """Test valeurs EventType."""
        assert EventType.EMAIL_RECEIVED == "email_received"
        assert EventType.FILE_CREATED == "file_created"
        assert EventType.ERROR_OCCURRED == "error_occurred"

    def test_priority_values(self):
        """Test valeurs Priority."""
        assert Priority.CRITICAL == 1
        assert Priority.HIGH == 2
        assert Priority.NORMAL == 3
        assert Priority.LOW == 4
        assert Priority.BACKGROUND == 5

    def test_priority_ordering(self):
        """Test ordre des priorités."""
        assert Priority.CRITICAL < Priority.HIGH
        assert Priority.HIGH < Priority.NORMAL
        assert Priority.NORMAL < Priority.LOW
        assert Priority.LOW < Priority.BACKGROUND