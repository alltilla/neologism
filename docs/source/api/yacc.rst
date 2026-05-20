YaccDecodeError
===============

.. currentmodule:: neologism

.. autoexception:: YaccDecodeError

Raised from :meth:`DCFG.from_yacc_file` when ``bison`` fails to parse
the input ``.y`` file. The exception message includes the file path
and, when available, the stderr output from ``bison`` (file, line,
column, and source span of the syntactic error).

If ``bison`` itself is missing from ``PATH``, the call raises a plain
:exc:`ChildProcessError` instead -- it is an environment problem, not
a decode failure of well-formed input.
