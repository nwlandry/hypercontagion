from setuptools import setup
import setuptools
import sys

__version__ = "0.1"

if sys.version_info < (3, 7):
    sys.exit("hypercontagion requires Python 3.7 or later.")

name = "hypercontagion"

version = __version__

authors = "Nicholas Landry"

author_email = "nicholas.landry@colorado.edu"

url = "https://github.com/nwlandry/hypercontagion"

description = "HyperContagion is a Python library for the simulation of contagion on complex systems with group (higher-order) interactions."

def parse_requirements_file(filename):
    with open(filename) as fid:
        requires = [l.strip() for l in fid.readlines() if not l.startswith("#")]
    return requires

extras_require = {
    dep: parse_requirements_file("requirements/" + dep + ".txt")
    for dep in ["developer", "documentation", "release", "test", "demos"]
}

install_requires = parse_requirements_file("requirements/default.txt")

license = "3-Clause BSD license"

setup(
    name=name,
    packages=setuptools.find_packages(),
    version=version,
    author=authors,
    author_email=author_email,
    url=url,
    description=description,
    install_requires=install_requires,
    extras_require=extras_require,
)