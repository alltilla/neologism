DCFG
====

.. currentmodule:: neologism

.. autoclass:: DCFG

   The grammar object. Build one from rules directly, or load one from
   a bison yacc file via :meth:`from_yacc_file`. Mutate it freely; the
   :attr:`sentences` view always reflects the current state.

   Construction
   ------------

   .. automethod:: from_yacc_file
   .. automethod:: copy
   .. automethod:: load_dcfg

   Rules
   -----

   .. autoproperty:: rules
   .. automethod:: rules_containing
   .. automethod:: add_rule
   .. automethod:: remove_rule

   Symbols
   -------

   .. autoproperty:: symbols
   .. autoproperty:: terminals
   .. autoproperty:: nonterminals
   .. automethod:: is_symbol_terminal
   .. automethod:: make_symbol_terminal
   .. automethod:: remove_symbol

   Start symbol
   ------------

   .. autoproperty:: start_symbol

   Sentence enumeration
   --------------------

   .. autoproperty:: sentences
   .. automethod:: iter_sentences
   .. automethod:: is_finite
