#!/usr/bin/env python

from setuptools import setup

# jump through some hoops to get access to versionstring()
from sys import path
from os.path import abspath, dirname, join
topdir = abspath(dirname(__file__))
exec(open(join(topdir, "mandelbrot/version.py"), "r").read())

# load contents of README.rst
readme = open("README.rst", "r").read()

#load requirement contents from requirements.txt
requirements = filter(None, open("requirements.txt", "r").read().split('\n'))

setup(
    # package description
    name = "mandelbrot",
    version = versionstring(),
    description="Mandelbrot distributed monitoring agent and client utilities",
    long_description=readme,
    author="Michael Frank",
    author_email="syntaxockey@gmail.com",
    url="https://github.com/msfrank/mandelbrot",
    # for defaults setup options
    setup_requires=[
        'pesky-defaults >= 0.0.2',
        ],
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
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        ],
    # package contents
    packages=[
        'mandelbrot',
        'mandelbrot.agent',
        'mandelbrot.client',
        'mandelbrot.endpoints',
        'mandelbrot.probes',
        'mandelbrot.systems',
        ],
    entry_points={
        'console_scripts': [
            'mandelbrot=mandelbrot.client:main',
            'mandelbrot-agent=mandelbrot.agent:main',
            ],
        'io.mandelbrot.endpoint': [
            'io.mandelbrot.endpoint.DummyEndpoint=mandelbrot.endpoints.dummy:DummyEndpoint',
            'io.mandelbrot.endpoint.HTTPEndpoint=mandelbrot.endpoints.http:HTTPEndpoint',
            ],
        'io.mandelbrot.endpoint.scheme': [
            'dummy=mandelbrot.endpoints.dummy:DummyEndpoint',
            'http=mandelbrot.endpoints.http:HTTPEndpoint',
            'https=mandelbrot.endpoints.http:HTTPEndpoint',
            ],
        'io.mandelbrot.probe': [
            'io.mandelbrot.probe.SystemLoad=mandelbrot.probes.system:SystemLoad',
            'io.mandelbrot.probe.SystemCPU=mandelbrot.probes.system:SystemCPU',
            'io.mandelbrot.probe.SystemMemory=mandelbrot.probes.system:SystemMemory',
            'io.mandelbrot.probe.SystemDiskUsage=mandelbrot.probes.system:SystemDiskUsage',
            'io.mandelbrot.probe.SystemDiskPerformance=mandelbrot.probes.system:SystemDiskPerformance',
            'io.mandelbrot.probe.SystemNetPerformance=mandelbrot.probes.system:SystemNetPerformance',
            'io.mandelbrot.probe.Aggregate=mandelbrot.probes.container:Aggregate',
            'io.mandelbrot.probe.MetricsEvaluation=mandelbrot.probes.metrics:MetricsEvaluation',
            ],
        'io.mandelbrot.system': [
            'io.mandelbrot.system.GenericHost=mandelbrot.systems.generic:GenericHost',
            ],
        },
    test_suite="test",
    tests_require=["nose >= 1.3.1"]
)
