# Neologism

A dynamically modifiable context-free grammar library for Python.

Neologism loads bison-style yacc files directly, exposes the grammar as a
`DCFG` object you can mutate (add or remove rules, promote nonterminals to
terminals, substitute symbols, and so on), and enumerates the sentences the
resulting grammar produces.

## When to reach for it

The need that motivated neologism: you have a real bison grammar, one that
is partly machine-generated, or whose canonical form is a `.y` file, and
you want to programmatically transform it and then enumerate every sentence
the transformed grammar accepts.

Existing libraries cover one or two of those three pieces:

- **ply / lark / parsimonious / ANTLR** parse input *using* a grammar; the
  grammar itself is not a mutable object you can manipulate after loading.
- **NLTK** models CFGs as data, including sentence generation, but does not
  ingest bison.
- **bison itself** generates a parser, not a manipulable model.

Neologism is the cross-section.

## Installing

```
pip install neologism
```

Bison must be available on `PATH`. It is invoked at runtime to convert
`.y` files to the XML form neologism consumes.

## Example

```python
from neologism import DCFG, Rule

dcfg = DCFG.from_yacc_file("my-grammar.y")

# Substitute the opaque terminal LL_NUMBER with a pretty placeholder
dcfg.make_symbol_terminal("LL_NUMBER")
dcfg.add_rule(Rule("LL_NUMBER", ("<number>",)))

# Stream every sentence the transformed grammar produces
for sentence in dcfg.iter_sentences():
    print(" ".join(sentence))
```

The mutation-after-load workflow is the distinguishing feature.
[axosyslog-cfg-helper](https://github.com/alltilla/axosyslog-cfg-helper)
is a substantial real-world consumer: it walks the AxoSyslog bison grammar,
applies module-specific transformations, and enumerates every driver
invocation to build a configuration-option database.

## Documentation

Full API reference: https://neologism.readthedocs.io/

## License

GPL-3.0-or-later
