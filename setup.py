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
        'zope.interface',
        'twisted >= 13.2.0',
        'pesky-settings >= 0.0.1',
        'psutil >= 2.1.0',
        'tabulate >= 0.7.2',
        'python-daemon >= 1.5.5',
        'setuptools',
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
        'mandelbrot.client',
        'mandelbrot.command',
        'mandelbrot.endpoints',
        'mandelbrot.probes',
        'mandelbrot.systems',
        ],
    entry_points={
        'console_scripts': [
            'mandelbrot-agent=mandelbrot.command.agent:main',
            'mandelbrot-client=mandelbrot.command.client:main',
            ],
        'io.mandelbrot.endpoint': [
            'io.mandelbrot.endpoint.DummyEndpoint=mandelbrot.endpoints.dummy:DummyEndpoint',
            'io.mandelbrot.endpoint.HTTPEndpoint=mandelbrot.endpoints.http:HTTPEndpoint',
            ],
        'io.mandelbrot.probe': [
            'io.mandelbrot.probe.SystemLoad=mandelbrot.probes.system:SystemLoad',
            'io.mandelbrot.probe.SystemCPU=mandelbrot.probes.system:SystemCPU',
            'io.mandelbrot.probe.SystemMemory=mandelbrot.probes.system:SystemMemory',
            ],
        'io.mandelbrot.system': [
            'io.mandelbrot.system.GenericHost=mandelbrot.systems.generic:GenericHost',
            ],
        },
    test_suite="test",
    tests_require=["nose >= 1.3.1"]
)
