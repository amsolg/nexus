"""
Setup script pour le projet Nexus.
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nexus",
    version="0.1.0",
    author="Nexus Team",
    description="Système de déclenchement événementiel pour agents IA autonomes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "pydantic>=2.0.0",
        "structlog>=23.0.0",
        "pyyaml>=6.0.0",
        "click>=8.0.0",
        "aioimaplib>=1.0.0",
        "pymq>=0.4.0",
        "watchdog>=3.0.0",
        "APScheduler>=3.10.0",
        "aiohttp>=3.8.0",
        "aiofiles>=23.0.0",
        "python-dotenv>=1.0.0",
        "prometheus-client>=0.17.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
)