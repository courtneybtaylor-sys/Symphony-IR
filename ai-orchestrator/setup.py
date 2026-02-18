"""Package installer for AI Orchestrator."""

from setuptools import setup, find_packages
from pathlib import Path

long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="ai-orchestrator",
    version="0.1.0",
    description="Deterministic multi-agent AI coordination engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kheper Company",
    python_requires=">=3.9",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "config": ["*.yaml"],
    },
    install_requires=[
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.18.0"],
        "ollama": ["requests>=2.31.0"],
        "all": [
            "openai>=1.0.0",
            "anthropic>=0.18.0",
            "requests>=2.31.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "orchestrator=orchestrator:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
