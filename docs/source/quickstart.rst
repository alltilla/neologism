Quickstart
==========

.. testsetup::

   from neologism import DCFG, Rule

This page walks through the three things neologism is built for:

1. Load a grammar.
2. Transform it.
3. Enumerate the sentences it produces.

The whole API surface is :class:`~neologism.DCFG` and :class:`~neologism.Rule`.

A first DCFG from scratch
-------------------------

You don't need a ``.y`` file to play with the API. Build a grammar by
adding :class:`~neologism.Rule` instances:

.. doctest::

   >>> from neologism import DCFG, Rule
   >>> dcfg = DCFG()
   >>> dcfg.add_rule(Rule("greeting", ("hello", "name")))
   >>> dcfg.add_rule(Rule("name", ("world",)))
   >>> dcfg.add_rule(Rule("name", ("there",)))
   >>> sorted(dcfg.sentences)
   [('hello', 'there'), ('hello', 'world')]

The first rule's left-hand side becomes the implicit
:attr:`~neologism.DCFG.start_symbol`. Override it with
``dcfg.start_symbol = "other"`` when needed.

Terminals vs nonterminals
-------------------------

Any symbol that does not appear on the left-hand side of a rule is a
*terminal* -- it stays in the output verbatim. Symbols that do appear on
an LHS are *nonterminals* and get expanded recursively.

.. doctest::

   >>> sorted(dcfg.terminals)
   ['hello', 'there', 'world']
   >>> sorted(dcfg.nonterminals)
   ['greeting', 'name']

:meth:`~neologism.DCFG.make_symbol_terminal` is the workhorse mutation:
it strips a nonterminal of all its expansion rules, so subsequent
sentence enumeration leaves it as an opaque terminal. This is how you
"freeze" pieces of a grammar that you don't want to expand:

.. doctest::

   >>> dcfg.make_symbol_terminal("name")
   >>> sorted(dcfg.terminals)
   ['hello', 'name']
   >>> sorted(dcfg.sentences)
   [('hello', 'name')]

Loading a real yacc file
------------------------

:meth:`~neologism.DCFG.from_yacc_file` is the canonical entry point.
Behind the scenes it shells out to ``bison`` (which must be on
``PATH``), reads the XML form, and constructs the DCFG.

.. code-block:: python

   from neologism import DCFG
   dcfg = DCFG.from_yacc_file("my-grammar.y")

Two pieces of bison-specific cleanup are applied automatically:

* The synthetic ``$end`` terminal that bison adds is removed.
* :attr:`~neologism.DCFG.start_symbol` is set to ``$accept`` (bison's
  augmenting production).

If ``bison`` fails to parse the file, a
:exc:`~neologism.YaccDecodeError` is raised with bison's stderr
appended; if ``bison`` itself is not on ``PATH``, the call raises
:exc:`ChildProcessError`. Pass ``bison_path=...`` to override the
``PATH`` used to locate it.

Transforming a loaded grammar
-----------------------------

The interesting workflow is mutating an as-loaded grammar before
enumeration. Typical moves:

* :meth:`~neologism.DCFG.make_symbol_terminal` to freeze an opaque
  terminal (e.g. a lexer-level token like ``LL_NUMBER``) and substitute
  a pretty placeholder.
* :meth:`~neologism.DCFG.remove_symbol` to amputate an entire branch of
  the grammar you don't care about.
* :meth:`~neologism.DCFG.add_rule` to inject synthetic productions
  (e.g. inline a documentation alias).
* :meth:`~neologism.DCFG.remove_rule` to drop a specific production
  while keeping the symbol around.

Worked example: replace the opaque ``LL_NUMBER`` terminal that bison
emits with a documentation-friendly placeholder.

.. code-block:: python

   from neologism import DCFG, Rule

   dcfg = DCFG.from_yacc_file("my-grammar.y")

   dcfg.make_symbol_terminal("LL_NUMBER")
   dcfg.add_rule(Rule("LL_NUMBER", ("<number>",)))

   for sentence in dcfg.iter_sentences():
       print(" ".join(sentence))

Enumerating sentences
---------------------

Two flavors:

* :attr:`~neologism.DCFG.sentences` returns a deduplicated
  :class:`set` of all sentences. Fine for small grammars.
* :meth:`~neologism.DCFG.iter_sentences` is a generator that streams
  sentences one at a time. Use this for large grammars where the
  cartesian product is too big to materialize, or when you want to
  short-circuit on the first match. Ambiguous grammars may yield the
  same sentence more than once -- wrap in :class:`set` if uniqueness
  matters.

If the grammar is not finite (contains a recursive cycle), neologism
will silently work off a copy of the grammar with loops broken. Check
:meth:`~neologism.DCFG.is_finite` upfront if that matters to you.

A bigger consumer
-----------------

For a worked end-to-end example against a real bison grammar, see
`axosyslog-cfg-helper
<https://github.com/alltilla/axosyslog-cfg-helper>`_, which uses
neologism to extract every valid AxoSyslog configuration construct from
the upstream ``.y`` file.
