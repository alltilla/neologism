Rule
====

.. currentmodule:: neologism

.. autoclass:: Rule
   :members:
   :special-members: __init__, __eq__, __hash__, __repr__

A :class:`Rule` is the atomic production: one left-hand-side
non-terminal expanding to a tuple of zero or more symbols on the
right-hand side. Rules are immutable, hashable, and value-equal --
two ``Rule`` objects with the same LHS and RHS compare equal regardless
of construction order.
