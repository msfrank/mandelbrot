mandelbrot
==========

Agent and client utilities for interacting with Mandelbrot monitoring system.

Prerequisite Software
---------------------

 * python 2.6, 2.7
 * twisted 13.2.0 or greater
 * pesky-settings 0.0.4 or greater
 * pesky-defaults 0.0.2 or greater
 * PyYAML 3.11 or greater
 * psutil 2.1.0 or greater
 * pyparsing 2.0.2 or greater
 * tabulate 0.7.2 or greater
 * python-daemon 1.5.5 or greater
 * python-dateutil 2.2 or greater
 * setproctitle 1.1.8 or greater
 * setuptools
 * zope.interface

Agent Quickstart
----------------

The easiest way to try out mandelbrot is to install the agent and client
utilities in a `virtualenv` environment.  Assuming you already have cloned
the mandelbrot git repository and virtualenv is installed, create a new
env and install mandelbrot using `setuptools`::

  $ virtualenv mandelbrot-env
  $ source mandelbrot-env/bin/activate
  $ python mandelbrot-src/setup.py install

Create the necessary directories within the env, and configure the
application defaults::

  $ export VENV=$PWD/mandelbrot-env
  $ mkdir -p $VENV/etc
  $ python mandelbrot-src/setup.py pesky_default --command set --key SYSCONF_DIR $VENV/etc
  $ mkdir -p $VENV/var/lib/agent $VENV/var/lib/systems
  $ python mandelbrot-src/setup.py pesky_default --command set --key LOCALSTATE_DIR $VENV/var/lib
  $ mkdir -p $VENV/var/run/
  $ python mandelbrot-src/setup.py pesky_default --command set --key RUN_DIR $VENV/var/run

Copy the example configuration file and system file into place::

  $ cp mandelbrot-src/doc/mandelbrot.conf.example $VENV/etc/mandelbrot.conf
  $ cp mandelbrot-src/doc/system.yaml.example $VENV/var/lib/systems/system.yaml

Now the agent is ready to be started.  Run it in the foreground with verbose
debugging::

  $ mandelbrot-agent -d -f

Client Usage
------------


Copyright/License
-----------------

Mandelbrot is licensed under the GPL version 3 or later.
