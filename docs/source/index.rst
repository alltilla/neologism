neologism
=========

A dynamically modifiable context-free grammar library for Python.

neologism loads bison-style yacc files directly, exposes the grammar as a
:class:`~neologism.DCFG` object you can mutate (add or remove rules, promote
nonterminals to terminals, substitute symbols, and so on), and enumerates
the sentences the resulting grammar produces.

The mutation-after-load workflow is the distinguishing feature: most
grammar libraries either parse *using* a grammar, or model a CFG as data,
but not both with a path from a real ``.y`` file to programmatic
manipulation.

Install
-------

.. code-block:: bash

   pip install neologism

``bison`` must be available on ``PATH`` to load ``.y`` files. It is
invoked at runtime to convert the yacc file to the XML form neologism
consumes.

A taste
-------

.. code-block:: python

   from neologism import DCFG, Rule

   dcfg = DCFG.from_yacc_file("my-grammar.y")

   # Treat LL_NUMBER as a terminal and substitute a pretty placeholder
   dcfg.make_symbol_terminal("LL_NUMBER")
   dcfg.add_rule(Rule("LL_NUMBER", ("<number>",)))

   # Stream every sentence the transformed grammar produces
   for sentence in dcfg.iter_sentences():
       print(" ".join(sentence))

A walkthrough of this pipeline lives in :doc:`quickstart`.

Real-world consumer
-------------------

`axosyslog-cfg-helper <https://github.com/alltilla/axosyslog-cfg-helper>`_
walks the AxoSyslog bison grammar, applies module-specific
transformations, and enumerates every driver invocation to build a
configuration-option database. It exercises every part of the API and
is the load-bearing consumer driving neologism's roadmap.

Contents
--------

.. toctree::
   :maxdepth: 2

   quickstart
   api/index

Project links
-------------

* `Source on GitHub <https://github.com/alltilla/neologism>`_
* `Changelog <https://github.com/alltilla/neologism/blob/main/CHANGELOG.md>`_
* `Issue tracker <https://github.com/alltilla/neologism/issues>`_
* `PyPI <https://pypi.org/project/neologism/>`_

License
-------

GPL-3.0-or-later.
