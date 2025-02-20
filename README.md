# picoquic_ns

This project builds a simple network simulator based on [`picoquic`[(https://github.com/private-octopus/picoquic)],
which we call `pico_sim`. The goal of this simulator are:

1. Simulate variety of congestion algorithms for QUIC connections, in a variety of network configurations.
2. Execute the actual picoquic code when running a simulation, but execute in "virtual time"
   so that a connection that would last several minutes can be performed in a fraction of second.

The `pico_sim` code wraps the `picoquic_ns` function in the picoquic test suite.
The function takes as parameter a "simulation specification". The `pico_sim` code can parse
a textual description of the simulation and execute it. This project contains a list
of such specifications, in the folder `sim_specs`. We hope that this list will grow
as researchers add more scenario descriptions.

The simulation produce a set of qlog traces for the different connections. A simple
simulation will create just two traces, one at the client and one at the server.
More complex simulations will manage several connections, for example to measure
how different algorithms behave when competing on the same path. The existing
qlog tool, [qvis](https://qvis.quictools.info/), can analyze a single connection.
We complement it with a python script that provides a graphical representation
of the competition between sveral connections -- see `scripts/qlogparse.py`.

## Building pico_sim

The code is organized as a cmake project. It has dependencies on `picoquic`,
[`picotls`](https://github.com/h2o/picotls) and OpenSSL. The test action
`.github/workflows/test-suite.yml` provides an example on how to build
and use `pico_sim`

The code also includes a Visual Studio project for use on Windows.
