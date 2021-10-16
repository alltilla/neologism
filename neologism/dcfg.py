from __future__ import annotations

import typing

import networkx

from . import utils
from .rule import Rule
from .yacc import parse as yacc_parse

Clause = typing.List[str]  # Part of a sentence


class RuleId(int):
    pass


class DCFG:
    """A class that represents dynamically modifiable context-free grammar.

    The API uses str for symbols and Rule for rules.
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
        >>> dcfg.rules
        {Rule('c' => 'x' 'y' 'z'), Rule('a' => 'b' 'c' 'd')}
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

        :raise TypeError: If :attr:`symbol` is not an instance of :class:`str`.

        .. seealso:: :attr:`rules`

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.rules_containing("d")
        {Rule('a' => 'b' 'c' 'd')}
        >>> dcfg.rules_containing("c")
        {Rule('c' => 'x' 'y' 'z'), Rule('a' => 'b' 'c' 'd')}
        """
        utils.raise_type_error_if_not_type_of(symbol, str)

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

        :raise TypeError: If :attr:`rule` is not an instance of :class:`Rule`.

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.rules
        {Rule('c' => 'x' 'y' 'z'), Rule('a' => 'b' 'c' 'd')}
        """
        utils.raise_type_error_if_not_type_of(rule, Rule)

        if self.__rule_exists(rule):
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

        :raise TypeError: If :attr:`rule` is not an instance of :class:`Rule`.
        :raise ValueError: If :attr:`rule` is not in the rules of the grammar.

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.rules
        {Rule('c' => 'x' 'y' 'z'), Rule('a' => 'b' 'c' 'd')}
        >>> dcfg.symbols
        {'y', 'a', 'x', 'b', 'c', 'd', 'z'}
        >>> dcfg.remove_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.rules
        {Rule('a' => 'b' 'c' 'd')}
        >>> dcfg.symbols
        {'y', 'a', 'x', 'b', 'c', 'd', 'z'}
        """
        utils.raise_type_error_if_not_type_of(rule, Rule)

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

        .. note:: It is possible for a symbol to not be used by any of the rules.

        .. seealso:: :attr:`terminals`, :attr:`nonterminals`

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.symbols
        {'y', 'a', 'x', 'b', 'c', 'd', 'z'}
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
        >>> dcfg.terminals
        {'b', 'x', 'z', '1', '3', 'y', '2', 'd'}
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
        >>> dcfg.nonterminals
        {'c', 'a'}
        """
        return set(filter(lambda node: isinstance(node, str) and not self.is_symbol_terminal(node), self.__graph.nodes))

    def remove_symbol(self, symbol: str) -> None:
        """
        Removes a symbol from the grammar.

        :param symbol: Symbol to remove.
        :type symbol: str

        :raise TypeError: If :attr:`symbol` is not an instance of :class:`str`.
        :raise ValueError: If :attr:`symbol` was not in the grammar.

        .. note:: If :attr:`symbol` was used by a rule in the grammar, it will be removed from the rule, too.
        .. note:: If :attr:`symbol` was a nonterminal, the rules which have :attr:`symbol`
                  as their :attr:`lhs` are also removed.
        .. note:: If there are symbols that are not used by any rule after the removal, they are removed.

        .. seealso:: :attr:`symbols`

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.rules
        {Rule('a' => 'b' 'c' 'd')}
        >>> dcfg.symbols
        {'d', 'a', 'c', 'b'}
        >>> dcfg.remove_symbol("c")
        >>> dcfg.rules
        {Rule('a' => 'b' 'd')}
        >>> dcfg.symbols
        {'d', 'a', 'b'}
        """
        utils.raise_type_error_if_not_type_of(symbol, str)

        self.make_symbol_terminal(symbol)
        self.__graph.remove_node(symbol)

    def is_symbol_terminal(self, symbol: str) -> bool:
        """
        Checks whether a symbol is terminal in the grammar.

        :param symbol: The symbol to check.
        :type symbol: str

        :raise TypeError: If :attr:`symbol` is not an instance of :class:`str`.
        :raise ValueError: If :attr:`symbol` was not in the grammar.

        .. seealso:: :attr:`symbols`, :attr:`terminals`, :attr:`nonterminals`, :func:`make_symbol_terminal`

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.terminals
        {'b', 'z', 'y', 'x', 'd'}
        >>> dcfg.nonterminals
        {'c', 'a'}
        >>> dcfg.is_symbol_terminal("a")
        False
        >>> dcfg.is_symbol_terminal("b")
        True
        """
        utils.raise_type_error_if_not_type_of(symbol, str)

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

        :raise TypeError: If :attr:`symbol` is not an instance of :class:`str`.
        :raise ValueError: If :attr:`symbol` was not in the grammar.

        .. seealso:: :attr:`symbols`, :attr:`terminals`, :attr:`nonterminals`, :func:`is_symbol_terminal`

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.rules
        {Rule('c' => 'x' 'y' 'z'), Rule('a' => 'b' 'c' 'd')}
        >>> dcfg.symbols
        {'y', 'a', 'x', 'b', 'c', 'd', 'z'}
        >>> dcfg.make_symbol_terminal("c")
        >>> dcfg.rules
        {Rule('a' => 'b' 'c' 'd')}
        >>> dcfg.symbols
        {'y', 'a', 'x', 'b', 'c', 'd', 'z'}
        """
        utils.raise_type_error_if_not_type_of(symbol, str)

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

        .. note:: If it is not explicitly, the first added rule's :attr:`lhs` is used.

        .. seealso:: :attr:`sentences`
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
        utils.raise_type_error_if_not_type_of(symbol, str)

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

    @property
    def sentences(self) -> typing.Set[tuple]:
        """
        :getter: Returns all possible sentences of the grammar, starting with :attr:`start_symbol`.
        :type: set[tuple]

        .. note:: If the grammar is not finite, sentences are generated from a copy of the grammar,
                  which has been made finite.

        .. seealso:: :func:`is_finite`, :attr:`start_symbol`

        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.add_rule(Rule("c", ("1", "2", "3")))
        >>> dcfg.sentences
        {('b', 'x', 'y', 'z', 'd'), ('b', '1', '2', '3', 'd')}
        """
        if self.start_symbol is None:
            return set()

        dcfg = self

        if not self.is_finite():
            dcfg = self.copy()
            utils.remove_loops_from_multidigraph(dcfg.__graph, dcfg.start_symbol)

        sentences_as_list = dcfg.__expand_symbol(dcfg.start_symbol)

        sentences = set()
        for sentence in sentences_as_list:
            sentences.add(tuple(sentence))

        return sentences

    # Misc

    def copy(self) -> DCFG:
        """
        :return: A copy of the grammar.
        :rtype: DCFG
        """
        copied = DCFG()
        copied.__graph = self.__graph.copy()  # Shallow copy, but we do not store containers, so it is okay
        copied.__next_rule_id = self.__next_rule_id
        copied.__start_symbol = self.__start_symbol

        return copied

    def load_yacc_file(self, file_path: str) -> None:
        """
        Loads rules from a yacc file.

        .. note:: Using this function needs ``bison`` to be installed and be on ``PATH``.

        :param file_path: The path of the yacc file.
        :type file_path: str

        :raise ChildProcessError: If ``bison`` is not available on the system.
        """
        rules = yacc_parse(file_path)

        for rule in rules:
            self.add_rule(rule)

        self.remove_symbol("$end")
        self.start_symbol = "$accept"

    # Private functions

    @property
    def __rule_ids(self) -> typing.Set:
        return set(filter(lambda node: isinstance(node, RuleId), self.__graph.nodes))

    def __get_next_rule_id(self) -> RuleId:
        next_rule_id = self.__next_rule_id

        self.__next_rule_id += 1

        return RuleId(next_rule_id)

    def __rule_exists(self, rule: Rule) -> bool:
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

    def __expand_rhs_of_rule_by_id(self, rule_id: RuleId) -> typing.List[Clause]:
        assert isinstance(rule_id, RuleId)

        expansions_of_each_rhs_symbol: typing.List[Clause] = []

        rhs = self.__get_rhs_by_rule_id(rule_id)
        for symbol in rhs:
            expansions_of_each_rhs_symbol.append(self.__expand_symbol(symbol))

        return utils.merge_expansions(expansions_of_each_rhs_symbol)

    def __expand_symbol(self, symbol: str) -> typing.List[Clause]:
        assert isinstance(symbol, str)

        expansions: typing.List[Clause] = []

        if self.is_symbol_terminal(symbol):
            expansion: Clause = [symbol]
            expansions.append(expansion)

            return expansions

        rule_ids = self.__graph.successors(symbol)
        for rule_id in rule_ids:
            expansions.extend(self.__expand_rhs_of_rule_by_id(rule_id))

        return expansions

    def __remove_rule_by_id(self, rule_id: RuleId) -> None:
        related_symbols = set()
        related_symbols.add(self.__get_lhs_by_rule_id(rule_id))
        for symbol in self.__get_rhs_by_rule_id(rule_id):
            related_symbols.add(symbol)

        self.__graph.remove_node(rule_id)

        for symbol in related_symbols:
            if len(list(self.__graph.predecessors(symbol))) == 0 and len(list(self.__graph.successors(symbol))) == 0:
                self.__graph.remove_node(symbol)
