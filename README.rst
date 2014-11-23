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

First things first, clone the `mandelbrot` git repository::

  $ git clone https://github.com/msfrank/mandelbrot.git mandelbrot-src

Next, you'll need to ensure that build tools, libraries and headers are
available on your host system.  This is operating-system dependent.  For
Ubuntu, run the following::

  $ sudo apt-get install build-essential python-dev python-virtualenv

If you are using a RedHat-based system (RHEL, CentOS, Fedora), run the
following::

  $ sudo yum install @"Development Tools" python-devel python-virtualenv

The easiest way to try out mandelbrot is to install the agent and client
utilities in a `virtualenv` environment.  Create a new env and install
mandelbrot using `setuptools`::

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

The example system.yaml file is a basic system definition and should work
without modification.  If you are running the mandelbrot server with a default
configuration, the mandelbrot.conf file should not need to be modified either;
however if you are running the server on a address or port other than the
default localhost:8080, you will need to update the [supervisor] section of
mandelbrot.conf to specify the correct supervisor url.

Now the agent is ready to be started.  Run it in the foreground with verbose
debugging::

  $ mandelbrot-agent -d -f -c $VENV/etc/mandelbrot.conf

You should see registration complete, and within a few seconds probes will
begin submitting data.

Client Usage
------------

Once the agent is running and submitting probe results to the server, the
client can be used to query that data.  First get a list of systems::

  $ mandelbrot server systems
  uri                         joinedOn                  lastUpdate
  --------------------------  ------------------------  ------------------------
  fqdn:localhost.localdomain  Sat Oct 25 15:56:17 2014  Sun Oct 26 09:43:57 2014

On my local host the mandelbrot-agent registered a new system named
'fqdn:localhost.localdomain'.  Let's get the current status::

  $ mandelbrot system status fqdn:localhost.localdomain
  probeRef                           lifecycle    health      acknowledged  summary                                                                              lastChange                lastUpdate                squelched
  ---------------------------------  -----------  --------  --------------  -----------------------------------------------------------------------------------  ------------------------  ------------------------  -----------
  fqdn:localhost.localdomain/cpu     known        healthy                   CPU utilization is 96.9% idle, 1.5% system, 1.6% user                                Sat Oct 25 15:56:21 2014  Sun Oct 26 11:55:16 2014
  fqdn:localhost.localdomain/load    known        healthy                   load average is 2.5 1.8 1.6, detected 8 cores                                        Sun Oct 26 11:53:53 2014  Sun Oct 26 11:55:13 2014
  fqdn:localhost.localdomain/memory  known        healthy                   47.2% used of 16.0 gigabytes of physical memory; 0.0% used of 1.0 gigabytes of swap  Sat Oct 25 15:56:19 2014  Sun Oct 26 11:55:13 2014

Copyright/License
-----------------

Mandelbrot is licensed under the GPL version 3 or later.
