from setuptools import setup
import sys

__version__ = "0.0"

if sys.version_info < (3, 7):
    sys.exit("hypercontagion requires Python 3.7 or later.")

name = "hypercontagion"

packages = ["hypercontagion", "hypercontagion.simulation"]

version = "0.0"

authors = "Nicholas Landry"

author_email = "nicholas.landry@colorado.edu"

url = "https://github.com/nwlandry/hypercontagion"

description = "HyperContagion is a Python library for the simulation of contagion on complex systems with group (higher-order) interactions."

install_requires = [
    "xgi>=0.1",
    "numpy>=1.15.0,<2.0",
    "pyglet>=1.5.15,<1.6",
    "matplotlib>=3.0.0",
]

license = "3-Clause BSD license"

extras_require = {
    "testing": ["pytest>=4.0"],
    "tutorials": ["jupyter>=1.0"],
    "documentation": ["sphinx>=1.8.2", "sphinx-rtd-theme>=0.4.2"],
    "all": [
        "sphinx>=1.8.2",
        "sphinx-rtd-theme>=0.4.2",
        "pytest>=4.0",
        "jupyter>=1.0",
    ],
}

setup(
    name=name,
    packages=packages,
    version=version,
    author=authors,
    author_email=author_email,
    url=url,
    description=description,
    install_requires=install_requires,
    extras_require=extras_require,
)
