from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="bonk_bot",
    version="1.1.4",
    description="Python API wrapper for bonk.io web game.",
    license="MIT",
    long_description=long_description,
    author="Safizapi",
    packages=find_packages(exclude=["tests"])
)
