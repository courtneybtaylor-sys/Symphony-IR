"""Package installer for Symphony-IR."""

from setuptools import setup, find_packages
from pathlib import Path

long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="symphony-ir",
    version="1.0.0a1",
    description="Compiler-grade runtime for multi-model AI orchestration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kheper Company",
    url="https://github.com/kheper-company/symphony-ir",
    project_urls={
        "Documentation": "https://github.com/kheper-company/symphony-ir#readme",
        "Source": "https://github.com/kheper-company/symphony-ir",
        "Issues": "https://github.com/kheper-company/symphony-ir/issues",
        "Changelog": "https://github.com/kheper-company/symphony-ir/blob/main/CHANGELOG.md",
    },
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
            "symphony=orchestrator:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Compilers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords=[
        "ai",
        "orchestration",
        "llm",
        "compiler",
        "multi-agent",
        "prompt-engineering",
        "intermediate-representation",
    ],
)
