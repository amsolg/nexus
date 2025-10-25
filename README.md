# Nexus - Event-Driven Trigger System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Nexus is a high-performance event-driven trigger system that transforms passive AI agents into proactive, reactive systems capable of responding to environmental changes in real-time.

## 🚀 Key Features

- **Real-time Reactivity**: <100ms latency from event detection to processing
- **Decoupled Architecture**: Independent producers and consumers via message bus
- **Extensible Design**: Add new event producers without modifying core code
- **Robust & Resilient**: Circuit breaker, retry logic, and automatic recovery
- **High Performance**: Support for 100+ events/second with minimal resource usage

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEXUS SYSTEM                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │  PRODUCERS   │───▶│  MESSAGE BUS    │───▶│   CONSUMERS     │ │
│  │              │    │                 │    │                 │ │
│  │ • Email IMAP │    │ ┌─────────────┐ │    │ Perception      │ │
│  │ • File Watch │    │ │ Event Queue │ │    │ System          │ │
│  │ • Scheduled  │    │ │   (PyMQ)    │ │    │                 │ │
│  │ • Custom     │    │ └─────────────┘ │    │        │        │ │
│  └──────────────┘    └─────────────────┘    └────────▼────────┘ │
│                                                      │          │
│                                               ┌──────▼──────────┐ │
│                                               │ Reasoning       │ │
│                                               │ System          │ │
│                                               │ (LangGraph)     │ │
│                                               └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/amsolg/nexus.git
cd nexus

# Install dependencies
pip install -r requirements.txt

# Copy default configuration
cp config/default.yaml config/local.yaml
```

### Basic Usage

```bash
# Start the complete Nexus system
python scripts/run_nexus.py --config config/local.yaml

# Development mode with hot-reload
python scripts/run_nexus.py --dev --verbose

# Run health checks
python scripts/health_check.py --all-components
```

### Create a Custom Producer

```python
from nexus.producers.base import AbstractProducer
from nexus.core.events import StandardEvent
from typing import AsyncGenerator
import asyncio

class CustomProducer(AbstractProducer):
    async def start(self) -> None:
        """Start the producer"""
        self.running = True

    async def stop(self) -> None:
        """Stop the producer"""
        self.running = False

    async def produce_events(self) -> AsyncGenerator[StandardEvent, None]:
        """Generate events"""
        while self.running:
            # Your custom logic here
            event = StandardEvent(
                type="CustomEvent",
                source="custom-producer",
                payload={"message": "Hello from custom producer"}
            )
            yield event
            await asyncio.sleep(5)  # Wait 5 seconds
```

## 📚 Documentation

- [Architecture Guide](docs/architecture/README.md)
- [API Reference](docs/api/README.md)
- [Development Guide](docs/guides/development.md)
- [Configuration Reference](docs/guides/configuration.md)

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=nexus --cov-report=html

# Run specific test suite
python -m pytest tests/unit/producers/
python -m pytest tests/integration/
python -m pytest tests/e2e/
```

## 📊 Performance Benchmarks

```bash
# Run performance benchmarks
python scripts/benchmark_system.py --duration 60 --events-per-second 100

# Monitor system metrics
python scripts/monitor_metrics.py --real-time
```

## 🔧 Configuration

Nexus uses YAML configuration files. Key settings:

```yaml
# config/local.yaml
message_bus:
  backend: "memory"
  max_queue_size: 1000
  consumer_timeout: 30.0

producers:
  email:
    enabled: true
    imap_server: "imap.gmail.com"
    # credentials in environment variables

  file_watcher:
    enabled: true
    watch_paths:
      - "/path/to/watch"

logging:
  level: "INFO"
  format: "structured"
```

## 🚀 Deployment

### Local Development
```bash
python scripts/run_nexus.py --dev
```

### Production
```bash
python scripts/run_nexus.py --config config/production.yaml
```

### Docker (Coming Soon)
```bash
docker build -t nexus .
docker run -d --name nexus-system nexus
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`python -m pytest tests/`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Run linting
python -m flake8 src/nexus/
python -m mypy src/nexus/
```

## 📈 Roadmap

- [x] Core event-driven architecture
- [x] Email IMAP producer
- [x] File system watcher producer
- [ ] Scheduled task framework
- [ ] Web API producer
- [ ] Calendar integration
- [ ] Distributed deployment support
- [ ] Advanced monitoring dashboard

## 🔒 Security

- All external connections are authenticated and encrypted
- Event validation prevents malicious payloads
- Component isolation prevents cascade failures
- Structured logging without sensitive data exposure

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built as part of the Mind-Mapper autonomous AI agent ecosystem
- Inspired by event-driven architecture patterns
- Powered by Python's asyncio for high-performance async operations