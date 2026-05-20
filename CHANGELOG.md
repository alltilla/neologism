# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- `DCFG.is_finite()` now correctly returns `True` on diamond grammars
  (where a nonterminal is reachable from the start symbol via more
  than one path without any cycle). The previous implementation
  tracked "ever-visited" nodes instead of nodes currently on the DFS
  stack, so any shared subgraph was misreported as a cycle. Sentence
  enumeration was already correct -- the actual cycle-removal pass
  uses a proper stack -- so the visible effect of the bug was an
  unnecessary copy + traversal in `iter_sentences` on grammars with
  shared subgraphs, plus any consumer call to `is_finite()` returning
  the wrong answer.

## [1.0.0] - 2026-05-20

First stable release. The library has been in use through 0.0.x; this
release commits to a public API surface and a documented semver contract.

### Added

- `DCFG.from_yacc_file(path, bison_path=None)` classmethod, the canonical
  ingest entry point. Accepts `os.PathLike` in addition to `str`.
- `DCFG.iter_sentences()`, a generator that yields sentences one at a
  time so callers can stream large languages without materializing the
  full cartesian product.
- `YaccDecodeError` messages now include bison's stderr, so a syntax
  error in a yacc file reports the file, line, column, and source span
  instead of just "failed to parse".
- Test suite now collects doctests in `neologism/*.py`. The docstring
  examples are part of the test suite, not just documentation.
- Branch coverage is now tracked. `pytest` invokes coverage by default
  via `pyproject.toml`; CI enforces `--cov-fail-under=100`.

### Changed

- `Rule(rhs=...)` now accepts any `Iterable[str]`, not only `tuple` or
  `list`. Generators and list-comprehensions work directly.
- `DCFG.copy()` is now a deep copy. Previously a shallow copy that
  relied on the implicit invariant "we never attach container-valued
  node or edge attributes". Future additions to the graph cannot break
  copy isolation as a result.
- `Rule.__eq__` returns `NotImplemented` for non-`Rule` operands instead
  of comparing on duck-typed `lhs`/`rhs` attributes. Eliminates spurious
  equality with tuples and other look-alike objects.
- Sentence expansion is now driven by `itertools.product` rather than a
  hand-rolled cartesian-product loop with `copy.deepcopy` in the hot
  path. Significantly lower memory and faster on large grammars.
- Packaging migrated to a Poetry-managed `pyproject.toml`. Single source
  of truth for project metadata; `setup.py`, `VERSION`,
  `requirements.txt`, and `MANIFEST.in` removed.
- Minimum Python version raised to 3.9 (was 3.7). Python 3.7 and 3.8 are
  long EOL.

### Removed

- `DCFG.load_yacc_file()`. Use `DCFG.from_yacc_file()` instead. The old
  shape mutated an existing DCFG, applied bison-specific cleanup
  in-place, and conflated three concerns. The classmethod is clearer.
- `neologism.utils.raise_type_error_if_not_type_of` and its `_multiple`
  variant. The library ships `py.typed`; static type checkers handle
  this without runtime guards, and the bare `TypeError()` they raised
  was less informative than letting downstream operations fail
  meaningfully.
- `neologism.utils.get_all_combinations`. Superseded by `itertools.product`.

### Fixed

- `yacc.parse()` and helpers now annotate `custom_path` as
  `Optional[str]` instead of `str` (the default was `None`).

## Earlier versions

Releases prior to 1.0.0 (0.0.1 -- 0.0.8) were exploratory and do not
have detailed changelog entries. See `git log` for the full history.

[Unreleased]: https://github.com/alltilla/neologism/compare/1.0.0...HEAD
[1.0.0]: https://github.com/alltilla/neologism/releases/tag/1.0.0
