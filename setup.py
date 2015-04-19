#!/usr/bin/env python3

from setuptools import setup

# jump through some hoops to get access to versionstring()
from sys import path
from os.path import abspath, dirname, join
topdir = abspath(dirname(__file__))
exec(open(join(topdir, "mandelbrot/version.py"), "r").read())

# load contents of README.rst
with open("README.rst", "r") as f:
    readme = f.read()

# load requirements
with open("requirements.txt", "r") as f:
    requirements = [requirement for requirement in f.read().split('\n') if requirement]
with open("test_requirements.txt", "r") as f:
    test_requirements = [requirement for requirement in f.read().split('\n') if requirement]

setup(
    # package description
    name = "mandelbrot",
    version = versionstring(),
    description="Mandelbrot distributed monitoring agent and client utilities",
    long_description=readme,
    author="Michael Frank",
    author_email="msfrank@syntaxjockey.com",
    url="https://github.com/msfrank/mandelbrot",
    # installation dependencies
    install_requires=requirements,
    # package classifiers for PyPI
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment "" No Input/Output (Daemon)",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: Other/Proprietary License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.4",
        ],
    # package contents
    packages=[
        'mandelbrot',
        'mandelbrot.agent',
        ],
    entry_points={
        'console_scripts': [
            'mandelbrot=mandelbrot.command:main',
            ],
        'mandelbrot.check': [
            'AlwaysHealthy=mandelbrot.check.dummy:AlwaysHealthy',
            ],
        },
    # test dependencies
    tests_require=test_requirements,
    test_suite="test",
)
