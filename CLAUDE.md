# CONTEXTE SPÉCIFIQUE DU PROJET : NEXUS

Je dois hériter de l'intégralité de ma personnalité de base définie dans le profil maître de Sam. Ce document ajoute uniquement le contexte local suivant.

## Objectif Principal
Nexus est un système de traitement événementiel centralisé qui transforme des agents IA passifs en systèmes proactifs et réactifs. Il centralise la réception, validation et traitement d'événements provenant de systèmes externes selon des contrats de données stricts, avec une latence <100ms et un débit de 100+ événements/seconde.

## Technologies Clés
- **Python 3.11+ avec asyncio** : Runtime principal optimisé pour performance asynchrone
- **Pydantic v2** : Validation ultra-rapide des contrats de données avec core Rust
- **structlog** : Logging structuré JSON pour observabilité moderne
- **asyncio.Queue** : Message bus FIFO native pour traitement séquentiel
- **gRPC** : Communication haute performance avec systèmes intégrés (Toasty)
- **YAML** : Configuration multi-environnements avec override par contexte

## Parties Prenantes
- **Système Toasty** : Intégration notifications Windows via gRPC (c:/repos/toasty/)
- **Système Parrot** : Producteur événements notifications Windows capturées
- **Systèmes Futurs** : Outlook (email), Dropbox (fichiers), Teams (collaboration)
- **Écosystème Sam** : Coordination avec architecture globale et standards
- **Mind-Mapper** : Système de raisonnement consommateur final des événements

## Priorités Actuelles
1. **Circuit Breaker & Retry Logic** : Finaliser résilience avec isolation automatique des composants défaillants
2. **Dead Letter Queue** : Implémenter gestion événements échoués avec reprocessing automatique
3. **Rate Limiting** : Protection configurable contre spam par système source
4. **Health Monitoring** : Surveillance continue avec dashboard observabilité temps réel
5. **Performance Optimization** : Atteindre objectif stable 100+ événements/seconde