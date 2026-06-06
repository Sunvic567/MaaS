from setuptools import setup, find_packages
from pathlib import Path

long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="memlayer-py",
    version="0.1.0",
    description="Persistent memory for AI agents — one API key, your agent remembers everything.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Victor Sunday",
    author_email="sunvictor567@gmail.com",
    url="https://github.com/yourusername/memlayer",
    project_urls={
        "Documentation": "https://memlayer.online/docs",
        "Bug Tracker":   "https://github.com/yourusername/memlayer/issues",
        "Homepage":      "https://memlayer.online",
    },
    license="MIT",
    packages=find_packages(where="sdk"),
    package_dir={"": "sdk"},
    install_requires=["httpx>=0.27.0"],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
    ],
    keywords="ai agent memory vector search langchain langgraph memlayer persistent memory",
)