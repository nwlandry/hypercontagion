
.. toctree::
   :maxdepth: 2
   :caption: Home
   :hidden:

   about

.. toctree::
   :maxdepth: 2
   :caption: Tutorials
   :hidden:

   See on GitHub <https://github.com/nwlandry/hypercontagion/tree/main/tutorials>

.. toctree::
   :maxdepth: 2
   :caption: API Reference
   :hidden:

   Simulation <api/simulation.rst>

About
=====

The `HyperContagion <https://github.com/nwlandry/hypercontagion>`_
library provides algorithms for simulating and visualizing contagion processes on complex systems
with group (higher-order) interactions.

- Repository: https://github.com/nwlandry/hypercontagion
- PyPI: https://pypi.org/project/hypercontagion/
- Documentation: https://hypercontagion.readthedocs.io/


Installation
============

To install and use HyperContagion as an end user, execute

.. code:: bash

   pip install hypercontagion

To install for development purposes, first clone the repository and then execute

.. code:: bash

   pip install -e .['all']

If that command does not work, you may try the following instead

.. code:: zsh

   pip install -e .\[all\]

HyperContagion was developed and tested for Python 3.7-3.10 on Mac OS, Windows, and Ubuntu.


Academic References
===================

* `The Why, How, and When of Representations for Complex Systems
  <https://doi.org/10.1137/20M1355896>`_, Leo Torres, Ann S. Blevins, Danielle Bassett,
  and Tina Eliassi-Rad.

* `Networks beyond pairwise interactions: Structure and dynamics
  <https://doi.org/10.1016/j.physrep.2020.05.004>`_, Federico Battiston, Giulia
  Cencetti, Iacopo Iacopini, Vito Latora, Maxime Lucas, Alice Patania, Jean-Gabriel
  Young, and Giovanni Petri.

* `What are higher-order networks? <https://arxiv.org/abs/2104.11329>`_, Christian Bick,
  Elizabeth Gross, Heather A. Harrington, Michael T. Schaub.


Contributing
============

If you want to contribute to this project, please make sure to read the
`code of conduct
<https://github.com/nwlandry/hypercontagion/blob/main/CODE_OF_CONDUCT.md>`_
and the `contributing guidelines
<https://github.com/nwlandry/hypercontagion/blob/main/CONTRIBUTING.md>`_.

The best way to contribute to HyperContagion is by submitting a bug or request a new feature by
opening a `new issue <https://github.com/nwlandry/hypercontagion/issues/new>`_.

To get more actively involved, you are invited to browse the `issues page
<https://github.com/nwlandry/hypercontagion/issues>`_ and choose one that you can
work on.  The core developers will be happy to help you understand the codebase and any
other doubts you may have while working on your contribution.

Contributors
============

The core HyperContagion team members:

* Nicholas Landry
* Joel Miller


License
=======

This project is licensed under the `BSD 3-Clause License
<https://github.com/nwlandry/hypercontagion/blob/main/LICENSE.md>`_.

Copyright (C) 2021 HyperContagion Developers
