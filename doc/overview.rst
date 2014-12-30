Overview
========

Mandelbrot is a system for large-scale monitoring of hosts, services, and
applications.  It is designed specifically for highly dynamic environments where
systems come and go or are repurposed frequently.  Mandelbrot monitoring is
agent-based, meaning that data acquisition and analysis is split into
two separate components:

 * The *agent*, called ``mandelbrot-agent``, which executes probes and publishes
   the results.
 * The *server*, called ``mandelbrot-core``, which consumes and evaluates the
   results from agents and performs actions.

Given a set of probes to execute, the agent essentially operates like a process
or job scheduler.  However, ``mandelbrot-agent`` also provides additional functionality:

 * Creates a secure transport for communication between the agent and server.
 * Provides server fault tolerance and transparently manages failover.
 * Splays probe scheduling in order to reduce local load hotspots.
 * Provides a persistence layer for probes to store local history.
 * Buffers probe results for batch sending to the server, in order to reduce
   protocol overhead.


Probes
------

A probe is a piece of code used for measuring or testing a property of a host,
service, or application.  Invoking the piece of code yields a result, which
consists of a status code representing overall health, a short textual description,
and zero or more metric values.

A probe is implemented as a Python plugin that is loaded by the agent.  Probes can
be written in languages other than Python, as long as they can be invoked by a
runtime bridge; for example, using the Exec probe you can call an executable
binary or script.

Systems
-------


