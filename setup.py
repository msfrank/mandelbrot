#!/usr/bin/env python

from setuptools import setup

# jump through some hoops to get access to versionstring()
from sys import path
from os.path import abspath, dirname
path.insert(0, abspath(dirname(__file__)))
from mandelbrot import versionstring

setup(
    # package description
    name = "mandelbrot",
    version = versionstring(),
    description="Mandelbrot distributed monitoring agent and client utilities",
    author="Michael Frank",
    author_email="msfrank@syntaxockey.com",
    # installation dependencies
    install_requires=[
        'twisted >= 13.2.0',
        ],
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
        "Programming Language :: Python :: 2.7",
        ],
    # package contents
    packages=[
        'mandelbrot',
        'mandelbrot.command',
        'mandelbrot.client',
        ],
    entry_points={
        'console_scripts': [
            'mandelbrot-agent=mandelbrot.command.agent:main',
            ],
        'io.mandelbrot.probe': [
            'io.mandelbrot.probe.SystemLoadLinux=mandelbrot.probes.system.SystemLoadLinux',
            ],
        },
    test_suite="test",
    tests_require=["nose >= 1.3.1"]
)
