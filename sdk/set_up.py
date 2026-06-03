from setuptools import setup, find_packages

setup(
    name="maas-py",
    version="0.1.0",
    description="Python SDK for Memory-as-a-Service — persistent memory for AI agents",
    long_description=open("sdk/README.md").read(),
    long_description_content_type="text/markdown",
    author="Victor Sunday",
    author_email="sunvictor567@gmail.com",
    url="https://github.com/yourusername/maas",
    packages=find_packages(where="sdk"),
    package_dir={"": "sdk"},
    install_requires=["httpx>=0.27.0"],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="ai agent memory vector search langchain langgraph",
)