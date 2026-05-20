from __future__ import annotations

import copy as _copy
import itertools
import os
import typing

import networkx

from . import utils
from .rule import Rule
from .yacc import parse as yacc_parse


class RuleId(int):
    pass


class DCFG:
    """
    A class that represents dynamically modifiable context-free grammar.

    The API uses :class:`str` for symbols and :class:`Rule` for rules.
    """

    def __init__(self):
        self.__graph = networkx.MultiDiGraph()
        self.__next_rule_id = 0
        self.__start_symbol = None

    @property
    def rules(self) -> typing.Set[Rule]:
        """
        :return: The rules, that define the grammar.
        :rtype: set[Rule]

        .. seealso:: :func:`rules_containing`

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> sorted(dcfg.rules, key=repr)
        [Rule('a' => 'b' 'c' 'd'), Rule('c' => 'x' 'y' 'z')]
        """
        rules = set()

        for rule_id in self.__rule_ids:
            rules.add(self.__get_rule_by_id(rule_id))

        return rules

    def rules_containing(self, symbol: str) -> typing.Set[Rule]:
        """
        Can be used to filter rules, that contain the given symbol (terminal or nonterminal).

        :param symbol: The symbol, which the rules are filtered by.
        :type symbol: str

        :return: The rules, that define the grammar and contain the given symbol.
        :rtype: set[Rule]

        .. seealso:: :attr:`rules`

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> sorted(dcfg.rules_containing("d"), key=repr)
        [Rule('a' => 'b' 'c' 'd')]
        >>> sorted(dcfg.rules_containing("c"), key=repr)
        [Rule('a' => 'b' 'c' 'd'), Rule('c' => 'x' 'y' 'z')]
        """
        rules = set()

        rule_ids = set(self.__graph.predecessors(symbol)) | set(self.__graph.successors(symbol))
        for rule_id in rule_ids:
            rules.add(self.__get_rule_by_id(rule_id))

        return rules

    def add_rule(self, rule: Rule) -> None:
        """
        Add a new rule to the grammar.

        .. note:: The symbols in the rule will be automatically added if they are not already in the grammar.

        :param rule: The new rule to add.
        :type rule: Rule

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> sorted(dcfg.rules, key=repr)
        [Rule('a' => 'b' 'c' 'd'), Rule('c' => 'x' 'y' 'z')]
        """
        if self._rule_exists(rule):
            return

        rule_id = self.__get_next_rule_id()

        self.__graph.add_edge(rule.lhs, rule_id)
        for index, symbol in enumerate(rule.rhs):
            self.__graph.add_edge(rule_id, symbol, index=index)

    def remove_rule(self, rule: Rule) -> None:
        """
        Remove a rule from the grammar.

        .. note:: If there are symbols that are not used by any rule after the removal, they are removed.

        :param rule: The rule to remove.
        :type rule: Rule

        :raise ValueError: If :attr:`rule` is not in the rules of the grammar.

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> sorted(dcfg.rules, key=repr)
        [Rule('a' => 'b' 'c' 'd'), Rule('c' => 'x' 'y' 'z')]
        >>> sorted(dcfg.symbols)
        ['a', 'b', 'c', 'd', 'x', 'y', 'z']
        >>> dcfg.remove_rule(Rule("c", ("x", "y", "z")))
        >>> sorted(dcfg.rules, key=repr)
        [Rule('a' => 'b' 'c' 'd')]
        >>> sorted(dcfg.symbols)
        ['a', 'b', 'c', 'd']
        """
        rule_found = False
        possible_rule_ids = list(self.__graph.successors(rule.lhs))  # cast to list, to make a copy

        for rule_id in possible_rule_ids:
            if self.__get_rhs_by_rule_id(rule_id) == rule.rhs:
                rule_found = True
                self.__remove_rule_by_id(rule_id)

        if not rule_found:
            raise ValueError("{} not in rules".format(rule))

    @property
    def symbols(self) -> typing.Set[str]:
        """
        :getter: The symbols that are defined in the grammar.
        :type: set[str]

        .. seealso:: :attr:`terminals`, :attr:`nonterminals`

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> sorted(dcfg.symbols)
        ['a', 'b', 'c', 'd', 'x', 'y', 'z']
        """
        return set(filter(lambda node: isinstance(node, str), self.__graph.nodes))

    @property
    def terminals(self) -> typing.Set[str]:
        """
        :getter: The terminals that are defined in the grammar.
        :type: set[str]

        .. note:: It is possible for a terminal to not be used by any of the rules.

        .. seealso:: :attr:`symbols`, :attr:`nonterminals`, :func:`is_symbol_terminal`, :func:`make_symbol_terminal`

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.add_rule(Rule("c", ("1", "2", "3")))
        >>> sorted(dcfg.terminals)
        ['1', '2', '3', 'b', 'd', 'x', 'y', 'z']
        """
        return set(filter(lambda node: isinstance(node, str) and self.is_symbol_terminal(node), self.__graph.nodes))

    @property
    def nonterminals(self) -> typing.Set[str]:
        """
        :getter: The nonterminals that are defined in the grammar.
        :type: set[str]

        .. note:: It is possible for a nonterminal to not be used by any of the rules.

        .. seealso:: :attr:`symbols`, :attr:`terminals`, :func:`is_symbol_terminal`, :func:`make_symbol_terminal`

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.add_rule(Rule("c", ("1", "2", "3")))
        >>> sorted(dcfg.nonterminals)
        ['a', 'c']
        """
        return set(filter(lambda node: isinstance(node, str) and not self.is_symbol_terminal(node), self.__graph.nodes))

    def remove_symbol(self, symbol: str) -> None:
        """
        Removes a symbol from the grammar.

        :param symbol: Symbol to remove.
        :type symbol: str

        :raise ValueError: If :attr:`symbol` was not in the grammar.

        .. note:: If :attr:`symbol` was used by a rule in the grammar, it will be removed from the rule, too.
        .. note:: If :attr:`symbol` was a nonterminal, the rules which have :attr:`symbol`
                  as their :attr:`lhs` are also removed.
        .. note:: If there are symbols that are not used by any rule after the removal, they are removed.

        .. seealso:: :attr:`symbols`

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> sorted(dcfg.rules, key=repr)
        [Rule('a' => 'b' 'c' 'd')]
        >>> sorted(dcfg.symbols)
        ['a', 'b', 'c', 'd']
        >>> dcfg.remove_symbol("c")
        >>> sorted(dcfg.rules, key=repr)
        [Rule('a' => 'b' 'd')]
        >>> sorted(dcfg.symbols)
        ['a', 'b', 'd']
        """
        self.make_symbol_terminal(symbol)
        self.__graph.remove_node(symbol)

    def is_symbol_terminal(self, symbol: str) -> bool:
        """
        Checks whether a symbol is terminal in the grammar.

        :param symbol: The symbol to check.
        :type symbol: str

        :raise ValueError: If :attr:`symbol` was not in the grammar.

        .. seealso:: :attr:`symbols`, :attr:`terminals`, :attr:`nonterminals`, :func:`make_symbol_terminal`

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> sorted(dcfg.terminals)
        ['b', 'd', 'x', 'y', 'z']
        >>> sorted(dcfg.nonterminals)
        ['a', 'c']
        >>> dcfg.is_symbol_terminal("a")
        False
        >>> dcfg.is_symbol_terminal("b")
        True
        """
        try:
            return len(list(self.__graph.successors(symbol))) == 0
        except networkx.NetworkXError:
            raise ValueError("{} not in symbols".format(symbol))

    def make_symbol_terminal(self, symbol: str) -> None:
        """
        Make a symbol terminal in the grammar.

        .. note: Rules that expanded the previously nonterminal symbol are removed.
        .. note: If there are symbols that are not used by any rule after the operation, they are not removed.

        :param symbol: The symbol to be made terminal.
        :type symbol: str

        :raise ValueError: If :attr:`symbol` was not in the grammar.

        .. seealso:: :attr:`symbols`, :attr:`terminals`, :attr:`nonterminals`, :func:`is_symbol_terminal`

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> sorted(dcfg.rules, key=repr)
        [Rule('a' => 'b' 'c' 'd'), Rule('c' => 'x' 'y' 'z')]
        >>> sorted(dcfg.symbols)
        ['a', 'b', 'c', 'd', 'x', 'y', 'z']
        >>> dcfg.make_symbol_terminal("c")
        >>> sorted(dcfg.rules, key=repr)
        [Rule('a' => 'b' 'c' 'd')]
        >>> sorted(dcfg.symbols)
        ['a', 'b', 'c', 'd']
        """
        try:
            rule_ids = list(self.__graph.successors(symbol))  # cast to list, to make a copy
        except networkx.NetworkXError:
            raise ValueError("{} not in symbols".format(symbol))

        for rule_id in rule_ids:
            self.__remove_rule_by_id(rule_id)

    @property
    def start_symbol(self) -> str:
        """
        :getter: Returns the start symbol.
        :setter: Sets the start symbol.
        :type: str

        .. note:: If it is not explicitly set, the first added rule's :attr:`lhs` is used.

        :raise ValueError: (setter only) If the new start symbol is not in the grammar.

        .. seealso:: :attr:`sentences`, :func:`iter_sentences`

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b",)))
        >>> dcfg.add_rule(Rule("c", ("d",)))
        >>> dcfg.start_symbol
        'a'
        >>> dcfg.start_symbol = "c"
        >>> dcfg.start_symbol
        'c'
        """
        if self.__start_symbol is None or self.__start_symbol not in self.symbols:
            if len(self.__rule_ids) != 0:
                lowest_rule_id = min(self.__rule_ids)
                self.__start_symbol = self.__get_lhs_by_rule_id(lowest_rule_id)
            else:
                self.__start_symbol = None

        return self.__start_symbol

    @start_symbol.setter
    def start_symbol(self, symbol: str) -> None:
        if symbol not in self.__graph.nodes:
            raise ValueError("{} not in symbols".format(symbol))

        self.__start_symbol = symbol

    # Sentences

    def is_finite(self) -> bool:
        """
        :return: Returns whether there is at least one loop in the resolutions of the nonterminals.
        :rtype: bool
        """
        if self.start_symbol is None:
            return True

        return utils.is_multidigraph_finite(self.__graph, self.start_symbol)

    def iter_sentences(self) -> typing.Iterator[typing.Tuple[str, ...]]:
        """
        Yields all possible sentences of the grammar one at a time, starting
        with :attr:`start_symbol`.

        .. note:: If the grammar is not finite, sentences are generated from a copy of the grammar,
                  which has been made finite.

        .. note:: Unlike :attr:`sentences`, the stream is not deduplicated. Ambiguous grammars may
                  yield the same sentence more than once. Wrap in :class:`set` if uniqueness matters.

        .. seealso:: :attr:`sentences`, :func:`is_finite`, :attr:`start_symbol`

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.add_rule(Rule("c", ("1", "2", "3")))
        >>> sorted(dcfg.iter_sentences())
        [('b', '1', '2', '3', 'd'), ('b', 'x', 'y', 'z', 'd')]
        """
        if self.start_symbol is None:
            return

        dcfg = self

        if not self.is_finite():
            dcfg = self.copy()
            utils.remove_loops_from_multidigraph(dcfg.__graph, dcfg.start_symbol)

        yield from dcfg.__iter_expand_symbol(dcfg.start_symbol)

    @property
    def sentences(self) -> typing.Set[typing.Tuple[str, ...]]:
        """
        :getter: Returns all possible sentences of the grammar, starting with :attr:`start_symbol`.
        :type: set[tuple]

        .. note:: If the grammar is not finite, sentences are generated from a copy of the grammar,
                  which has been made finite.

        .. seealso:: :func:`iter_sentences`, :func:`is_finite`, :attr:`start_symbol`

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.add_rule(Rule("c", ("1", "2", "3")))
        >>> sorted(dcfg.sentences)
        [('b', '1', '2', '3', 'd'), ('b', 'x', 'y', 'z', 'd')]
        """
        return set(self.iter_sentences())

    # Misc

    def copy(self) -> DCFG:
        """
        :return: A fully independent copy of the grammar.
        :rtype: DCFG

        .. note:: Mutations on the returned :class:`DCFG` -- including future
                  changes to node or edge attributes on the underlying graph --
                  never affect the original.
        """
        copied = DCFG()
        copied.__graph = _copy.deepcopy(self.__graph)
        copied.__next_rule_id = self.__next_rule_id
        copied.__start_symbol = self.__start_symbol

        return copied

    @classmethod
    def from_yacc_file(
        cls,
        file_path: str | os.PathLike[str],
        bison_path: str | None = None,
    ) -> DCFG:
        """
        Construct a :class:`DCFG` by loading rules from a bison-style yacc file.

        Bison-specific cleanup is applied: the ``$end`` terminal is removed and
        :attr:`start_symbol` is set to ``$accept``.

        .. note:: This function needs ``bison`` to be installed and on ``PATH``
                  (or located via :attr:`bison_path`).

        :param file_path: The path of the yacc file.
        :type file_path: str | os.PathLike[str]

        :param bison_path: Optional ``PATH`` override used to locate ``bison``.
        :type bison_path: str | None

        :raise ChildProcessError: If ``bison`` is not available on the system.
        :raise YaccDecodeError: If ``bison`` fails to parse the yacc file.
        """
        dcfg = cls()
        for rule in yacc_parse(os.fspath(file_path), bison_path):
            dcfg.add_rule(rule)

        dcfg.remove_symbol("$end")
        dcfg.start_symbol = "$accept"

        return dcfg

    def load_dcfg(self, dcfg: DCFG) -> None:
        """
        Loads rules from another DCFG.

        :param dcfg: The other :class:`DCFG` instance to load the rules from.
        :type dcfg: DCFG
        """
        for rule in dcfg.rules:
            self.add_rule(rule)

    # Private functions

    @property
    def __rule_ids(self) -> typing.Set:
        return set(filter(lambda node: isinstance(node, RuleId), self.__graph.nodes))

    def __get_next_rule_id(self) -> RuleId:
        next_rule_id = self.__next_rule_id

        self.__next_rule_id += 1

        return RuleId(next_rule_id)

    def _rule_exists(self, rule: Rule) -> bool:
        assert isinstance(rule, Rule)

        try:
            rule_ids = self.__graph.successors(rule.lhs)
        except networkx.NetworkXError:
            return False

        for rule_id in rule_ids:
            rhs = self.__get_rhs_by_rule_id(rule_id)
            if rhs == rule.rhs:
                return True

        return False

    def __get_lhs_by_rule_id(self, rule_id: RuleId) -> str:
        assert isinstance(rule_id, RuleId)

        lhss = list(self.__graph.predecessors(rule_id))
        assert len(lhss) == 1

        lhs = lhss[0]
        assert isinstance(lhs, str)

        return lhs

    def __get_rhs_by_rule_id(self, rule_id: RuleId) -> tuple:
        assert isinstance(rule_id, RuleId)

        symbols = []

        for symbol, arcs in self.__graph[rule_id].items():
            for _, arc in arcs.items():
                symbols.append((arc["index"], symbol))

        rhs = tuple([x[1] for x in sorted(symbols)])

        return rhs

    def __get_rule_by_id(self, rule_id: RuleId) -> Rule:
        assert isinstance(rule_id, RuleId)

        lhs = self.__get_lhs_by_rule_id(rule_id)
        rhs = self.__get_rhs_by_rule_id(rule_id)

        return Rule(lhs, rhs)

    def __iter_expand_rhs_of_rule_by_id(self, rule_id: RuleId) -> typing.Iterator[typing.Tuple[str, ...]]:
        assert isinstance(rule_id, RuleId)

        rhs = self.__get_rhs_by_rule_id(rule_id)
        per_position = [list(self.__iter_expand_symbol(symbol)) for symbol in rhs]

        for combo in itertools.product(*per_position):
            yield tuple(itertools.chain.from_iterable(combo))

    def __iter_expand_symbol(self, symbol: str) -> typing.Iterator[typing.Tuple[str, ...]]:
        assert isinstance(symbol, str)

        if self.is_symbol_terminal(symbol):
            yield (symbol,)
            return

        for rule_id in self.__graph.successors(symbol):
            yield from self.__iter_expand_rhs_of_rule_by_id(rule_id)

    def __remove_rule_by_id(self, rule_id: RuleId) -> None:
        related_symbols = set()
        related_symbols.add(self.__get_lhs_by_rule_id(rule_id))
        for symbol in self.__get_rhs_by_rule_id(rule_id):
            related_symbols.add(symbol)

        self.__graph.remove_node(rule_id)

        for symbol in related_symbols:
            if len(list(self.__graph.predecessors(symbol))) == 0 and len(list(self.__graph.successors(symbol))) == 0:
                self.__graph.remove_node(symbol)
