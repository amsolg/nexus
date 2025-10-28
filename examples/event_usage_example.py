#!/usr/bin/env python3
"""
Exemple d'utilisation des schémas d'événements Nexus.

Démontre la création, validation et sérialisation des différents types d'événements.
"""

import json
from datetime import datetime
from uuid import uuid4

from nexus.core.events import (
    EmailEvent,
    ErrorEvent,
    EventType,
    FileEvent,
    Priority,
    ScheduledEvent,
    SystemHealthEvent,
    create_event,
)


def demo_basic_events():
    """Démonstration des événements de base."""
    print("=== Démonstration des Événements de Base ===\n")

    # 1. Événement Email
    print("1. Événement Email:")
    email_event = EmailEvent(
        source="imap_producer",
        payload={
            "from": "user@example.com",
            "to": ["recipient@example.com"],
            "subject": "Important: Nouvelle notification",
            "received_at": "2023-10-24T10:30:00Z",
            "message_id": "12345@example.com"
        },
        correlation_id=str(uuid4()),
        priority=Priority.HIGH
    )
    print(f"  - ID: {email_event.event_id}")
    print(f"  - Type: {email_event.type}")
    print(f"  - Source: {email_event.source}")
    print(f"  - Priorité: {email_event.priority}")
    print(f"  - Expéditeur: {email_event.payload['from']}")
    print(f"  - Sujet: {email_event.payload['subject']}")
    print()

    # 2. Événement Fichier
    print("2. Événement Fichier:")
    file_event = FileEvent(
        type=EventType.FILE_MODIFIED,
        source="file_watcher",
        payload={
            "file_path": "/home/user/documents/important.docx",
            "size": 15680,
            "last_modified": "2023-10-24T10:25:30Z",
            "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }
    )
    print(f"  - Type: {file_event.type}")
    print(f"  - Fichier: {file_event.payload['file_path']}")
    print(f"  - Taille: {file_event.payload['size']} bytes")
    print()

    # 3. Événement Programmé
    print("3. Événement Programmé:")
    scheduled_event = ScheduledEvent(
        source="task_scheduler",
        payload={
            "task_id": "backup_weekly_001",
            "scheduled_time": "2023-10-24T02:00:00Z",
            "task_type": "backup",
            "config": {"target_dir": "/backups", "compress": True}
        }
    )
    print(f"  - Tâche: {scheduled_event.payload['task_id']}")
    print(f"  - Planifiée: {scheduled_event.payload['scheduled_time']}")
    print(f"  - Type: {scheduled_event.payload['task_type']}")
    print()


def demo_specialized_events():
    """Démonstration des événements spécialisés."""
    print("=== Événements Spécialisés ===\n")

    # 1. Événement de Santé Système
    print("1. Monitoring de Santé:")
    health_event = SystemHealthEvent(
        source="health_monitor",
        payload={
            "component": "database_primary",
            "status": "healthy",
            "metrics": {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "disk_io": 1250,
                "active_connections": 23,
                "response_time_avg": 125.5
            },
            "last_check": "2023-10-24T10:35:00Z"
        }
    )
    print(f"  - Composant: {health_event.payload['component']}")
    print(f"  - Statut: {health_event.payload['status']}")
    print(f"  - CPU: {health_event.payload['metrics']['cpu_usage']}%")
    print(f"  - Mémoire: {health_event.payload['metrics']['memory_usage']}%")
    print()

    # 2. Événement d'Erreur
    print("2. Gestion d'Erreur:")
    error_event = ErrorEvent(
        source="api_gateway",
        payload={
            "error_type": "DatabaseConnectionTimeout",
            "message": "Connection to primary database timed out after 30 seconds",
            "component": "database_connector",
            "stack_trace": "Traceback (most recent call last): ...",
            "request_id": "req_789abc123",
            "user_id": "user_456def",
            "timestamp": "2023-10-24T10:40:15Z"
        },
        priority=Priority.CRITICAL
    )
    print(f"  - Type d'erreur: {error_event.payload['error_type']}")
    print(f"  - Composant: {error_event.payload['component']}")
    print(f"  - Message: {error_event.payload['message']}")
    print(f"  - Priorité: {error_event.priority}")
    print()


def demo_factory_usage():
    """Démonstration de l'usage de la factory."""
    print("=== Utilisation de la Factory ===\n")

    events = []

    # Création via factory
    events.append(create_event(
        event_type=EventType.CALENDAR_EVENT,
        source="google_calendar",
        payload={
            "event_id": "cal_meeting_001",
            "title": "Réunion équipe développement",
            "start_time": "2023-10-24T14:00:00Z",
            "end_time": "2023-10-24T15:30:00Z",
            "attendees": ["dev1@company.com", "dev2@company.com"],
            "location": "Salle de réunion A"
        },
        priority=Priority.NORMAL
    ))

    events.append(create_event(
        event_type=EventType.FILE_CREATED,
        source="document_scanner",
        payload={
            "file_path": "/uploads/scanned_documents/invoice_2023_001.pdf",
            "size": 2_456_789,
            "content_type": "application/pdf",
            "scan_quality": "high",
            "ocr_processed": True
        }
    ))

    for i, event in enumerate(events, 1):
        print(f"{i}. {event.__class__.__name__}:")
        print(f"   - Type: {event.type}")
        print(f"   - Source: {event.source}")
        print(f"   - Payload keys: {list(event.payload.keys())}")
        print()


def demo_serialization():
    """Démonstration de la sérialisation."""
    print("=== Sérialisation et Validation ===\n")

    # Créer un événement complexe
    event = EmailEvent(
        source="outlook_connector",
        payload={
            "from": "client@important-company.com",
            "to": ["support@mycompany.com"],
            "cc": ["manager@mycompany.com"],
            "subject": "URGENT: Problème de production",
            "body_preview": "Nous rencontrons un problème critique...",
            "received_at": "2023-10-24T09:15:30Z",
            "attachments": [
                {"name": "error_log.txt", "size": 15234},
                {"name": "screenshot.png", "size": 456789}
            ],
            "importance": "high"
        },
        priority=Priority.CRITICAL,
        correlation_id="incident_789"
    )

    # Sérialisation JSON
    print("1. Sérialisation JSON:")
    json_data = event.model_dump_json(indent=2)
    print(json_data)
    print()

    # Désérialisation
    print("2. Désérialisation:")
    parsed_data = json.loads(json_data)
    recreated_event = EmailEvent(**parsed_data)
    print(f"   - Événement recréé avec succès")
    print(f"   - ID identique: {recreated_event.event_id == event.event_id}")
    print(f"   - Payload identique: {recreated_event.payload == event.payload}")
    print()

    # Dictionnaire Python
    print("3. Conversion dictionnaire:")
    event_dict = event.model_dump()
    print(f"   - Clés disponibles: {list(event_dict.keys())}")
    print(f"   - Timestamp type: {type(event_dict['timestamp'])}")
    print()


def demo_validation_errors():
    """Démonstration de la validation et gestion d'erreurs."""
    print("=== Validation et Gestion d'Erreurs ===\n")

    print("1. Tests de validation:")

    # Test source vide
    try:
        EmailEvent(
            source="",  # Source vide - devrait échouer
            payload={"from": "test@example.com", "subject": "Test", "received_at": "2023-10-24T10:00:00Z"}
        )
    except Exception as e:
        print(f"   > Source vide détectée: {type(e).__name__}")

    # Test payload manquant
    try:
        EmailEvent(
            source="test_source",
            payload={"subject": "Test"}  # Manque 'from' et 'received_at'
        )
    except Exception as e:
        print(f"   > Champs manquants détectés: {type(e).__name__}")

    # Test type d'événement invalide pour FileEvent
    try:
        FileEvent(
            type=EventType.EMAIL_RECEIVED,  # Type invalide pour FileEvent
            source="file_watcher",
            payload={"file_path": "/test/file.txt"}
        )
    except Exception as e:
        print(f"   > Type incompatible détecté: {type(e).__name__}")

    print()


if __name__ == "__main__":
    """Point d'entrée principal."""
    print("NEXUS - Démonstration du Système d'Événements\n")
    print("=" * 60)
    print()

    demo_basic_events()
    demo_specialized_events()
    demo_factory_usage()
    demo_serialization()
    demo_validation_errors()

    print("=" * 60)
    print(">>> Démonstration terminée avec succès!")
    print()
    print("Points clés démontrés:")
    print("- Création d'événements typés avec validation automatique")
    print("- Sérialisation/désérialisation JSON robuste")
    print("- Factory pattern pour création flexible")
    print("- Gestion d'erreurs et validation des données")
    print("- Support complet des types d'événements système")