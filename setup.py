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
        'pesky-settings >= 0.0.1',
        'python-daemon >= 1.5.5',
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
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        ],
    # package contents
    packages=[
        'mandelbrot',
        'mandelbrot.agent',
        'mandelbrot.command',
        'mandelbrot.endpoints',
        'mandelbrot.probes',
        ],
    entry_points={
        'console_scripts': [
            'mandelbrot-agent=mandelbrot.command.agent:main',
            ],
        'io.mandelbrot.endpoint': [
            'io.mandelbrot.endpoint.ZeromqEndpoint=mandelbrot.endpoints.zeromq:ZeromqEndpoint',
            ],
        'io.mandelbrot.probe': [
            'io.mandelbrot.probe.SystemLoadLinux=mandelbrot.probes.system:SystemLoadLinux',
            ],
        },
    test_suite="test",
    tests_require=["nose >= 1.3.1"]
)
