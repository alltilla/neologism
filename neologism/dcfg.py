import typing

import networkx

from .rule import Rule
from .yacc import parse as yacc_parse
from . import utils

Clause = typing.List[str]  # Part of a sentence
Sentence = Clause


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
        """Returns
        -------
        rules : set of Rule
            The rules, that define the grammar.

        See Also
        --------
        rules_containing : filter rules by symbol

        Examples
        --------
        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.rules
        {Rule(lhs='c', rhs=('x', 'y', 'z')), Rule(lhs='a', rhs=('b', 'c', 'd'))}
        """
        rules = set()

        for rule_id in self.__rule_ids:
            rules.add(self.__get_rule_by_id(rule_id))

        return rules

    def rules_containing(self, symbol: str) -> typing.Set[Rule]:
        """Can be used to filter rules, that contain the given symbol
        (terminal or non-terminal).

        Parameters
        ----------
        symbol : str
            The symbol, which the rules are filtered by.

        Returns
        -------
        rules : set of Rule
            The rules, that define the grammar and contain the given symbol.

        Raises
        ------
        TypeError
            If symbol is not str.

        See Also
        --------
        rules : get all rules

        Examples
        --------
        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.rules_containing("d")
        {Rule(lhs='a', rhs=('b', 'c', 'd'))}
        >>> dcfg.rules_containing("c")
        {Rule(lhs='c', rhs=('x', 'y', 'z')), Rule(lhs='a', rhs=('b', 'c', 'd'))}
        """
        utils.raise_type_error_if_not_type_of(symbol, str)

        rules = set()

        rule_ids = set(self.__graph.predecessors(symbol)) | set(self.__graph.successors(symbol))
        for rule_id in rule_ids:
            rules.add(self.__get_rule_by_id(rule_id))

        return rules

    def add_rule(self, rule: Rule) -> None:
        """Add a new rule to the grammar.

        The symbols in the rule will be automatically added if they are not
        already in the grammar.

        Parameters
        ----------
        rule : Rule
            The new rule to add.

        Raises
        ------
        TypeError
            If rule is not Rule.

        Examples
        --------
        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.rules
        {Rule(lhs='c', rhs=('x', 'y', 'z')), Rule(lhs='a', rhs=('b', 'c', 'd'))}
        """
        utils.raise_type_error_if_not_type_of(rule, Rule)

        if self.__rule_exists(rule):
            return

        rule_id = self.__get_next_rule_id()

        self.__graph.add_edge(rule.lhs, rule_id)
        for index, symbol in enumerate(rule.rhs):
            self.__graph.add_edge(rule_id, symbol, index=index)

    def remove_rule(self, rule: Rule) -> None:
        """Remove a rule from the grammar.

        If there are symbols that are not used by any rule after the removal,
        they are not removed.

        Parameters
        ----------
        rule : Rule
            The rule to remove.

        Raises
        ------
        TypeError
            If rule is not Rule.
        ValueError
            If rule is not in the rules of the grammar.

        See Also
        --------
        ??? : clean up unused symbols, etc...

        Examples
        --------
        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.rules
        {Rule(lhs='c', rhs=('x', 'y', 'z')), Rule(lhs='a', rhs=('b', 'c', 'd'))}
        >>> dcfg.symbols
        {'y', 'a', 'x', 'b', 'c', 'd', 'z'}
        >>> dcfg.remove_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.rules
        {Rule(lhs='a', rhs=('b', 'c', 'd'))}
        >>> dcfg.symbols
        {'y', 'a', 'x', 'b', 'c', 'd', 'z'}
        """
        utils.raise_type_error_if_not_type_of(rule, Rule)

        rule_found = False
        possible_rule_ids = list(self.__graph.successors(rule.lhs))  # cast to list, to make a copy

        for rule_id in possible_rule_ids:
            if self.__get_rhs_by_rule_id(rule_id) == rule.rhs:
                self.__graph.remove_node(rule_id)
                rule_found = True

        if not rule_found:
            raise ValueError("{} not in rules".format(rule))
        # TODO: add cleanup fn for dangling symbols, rules, etc...

    @property
    def symbols(self) -> typing.Set[str]:
        """Returns
        -------
        symbols : set of str
            The symbols that are defined in the grammar.
            It is possible for a symbol to not be used by any of the rules.

        See Also
        --------
        terminals, nonterminals
        ??? : clean up unused symbols, etc...

        Examples
        --------
        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.symbols
        {'y', 'a', 'x', 'b', 'c', 'd', 'z'}
        """
        return set(filter(lambda node: isinstance(node, str), self.__graph.nodes))

    @property
    def terminals(self) -> typing.Set[str]:
        """Returns
        -------
        terminals : set of str
            The terminals that are defined in the grammar.
            It is possible for a terminal to not be used by any of the rules.

        See Also
        --------
        symbols, nonterminals, is_symbol_terminal, make_symbol_terminal
        ??? : clean up unused symbols, etc...

        Examples
        --------
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
        """Returns
        -------
        nonterminals : set of str
            The non-terminals that are defined in the grammar.
            It is possible for a non-terminal to not be used by any of the rules.

        See Also
        --------
        symbols, terminals, is_symbol_terminal, make_symbol_terminal
        ??? : clean up unused symbols, etc...

        Examples
        --------
        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.add_rule(Rule("c", ("1", "2", "3")))
        >>> dcfg.nonterminals
        {'c', 'a'}
        """
        return set(filter(lambda node: isinstance(node, str) and not self.is_symbol_terminal(node), self.__graph.nodes))

    def remove_symbol(self, symbol: str) -> None:
        """Remove a symbol from the grammar.

        If the symbol was used by a rule, it will be removed from the
        rule, too.

        Parameters
        ----------
        symbol : str
            Symbol to remove.

        Raises
        ------
        TypeError
            If symbol is not str.
        ValueError
            If symbol was not in the grammar.

        See Also
        --------
        symbols

        Examples
        --------
        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.rules
        {Rule(lhs='a', rhs=('b', 'c', 'd'))}
        >>> dcfg.symbols
        {'d', 'a', 'c', 'b'}
        >>> dcfg.remove_symbol("c")
        >>> dcfg.rules
        {Rule(lhs='a', rhs=('b', 'd'))}
        >>> dcfg.symbols
        {'d', 'a', 'b'}
        """
        utils.raise_type_error_if_not_type_of(symbol, str)

        self.make_symbol_terminal(symbol)
        try:
            self.__graph.remove_node(symbol)
        except networkx.NetworkXError:
            raise ValueError("{} not in symbols".format(symbol))

    def is_symbol_terminal(self, symbol: str):
        """Checks whether a symbol is terminal in the grammar.

        Parameters
        ----------
        symbol : str
            Symbol to check.

        Raises
        ------
        TypeError
            If symbol is not str.
        ValueError
            If symbol was not in the grammar.

        See Also
        --------
        symbols, terminals, nonterminals, make_symbol_terminal

        Examples
        --------
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
        """Make a symbol terminal in the grammar.

        Rules that expanded the previously non-terminal symbol are removed.
        If there are symbols that are not used by any rule after the
        operation, they are not removed.

        Parameters
        ----------
        symbol : str
            Symbol to be made terminal.

        Raises
        ------
        TypeError
            If symbol is not str.
        ValueError
            If symbol was not in the grammar.

        See Also
        --------
        symbols, terminals, nonterminals, is_symbol_terminal

        Examples
        --------
        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.rules
        {Rule(lhs='c', rhs=('x', 'y', 'z')), Rule(lhs='a', rhs=('b', 'c', 'd'))}
        >>> dcfg.symbols
        {'y', 'a', 'x', 'b', 'c', 'd', 'z'}
        >>> dcfg.make_symbol_terminal("c")
        >>> dcfg.rules
        {Rule(lhs='a', rhs=('b', 'c', 'd'))}
        >>> dcfg.symbols
        {'y', 'a', 'x', 'b', 'c', 'd', 'z'}
        """
        utils.raise_type_error_if_not_type_of(symbol, str)

        try:
            rule_ids = list(self.__graph.successors(symbol))  # cast to list, to make a copy
        except networkx.NetworkXError:
            raise ValueError("{} not in symbols".format(symbol))

        for rule_id in rule_ids:
            self.__graph.remove_node(rule_id)

    @property
    def start_symbol(self) -> str:
        """Start symbol. Needed for forming sentences.

        If it is not explicitly, the first added rule's lhs is used.
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

    def is_finite(self):
        if self.start_symbol is None:
            return True

        return utils.is_multidigraph_finite(self.__graph, self.start_symbol)

    @property
    def sentences(self) -> typing.Set[tuple]:
        """Returns
        -------
        sentences: list of Sentence == list of list of str
            All possible sentences of the grammar. If the grammar is not
            finite, sentences are generated from a copy of the grammar,
            which has been made finite.

        Examples
        --------
        >>> dcfg = DCFG()
        >>> dcfg.add_rule(Rule("a", ("b", "c", "d")))
        >>> dcfg.add_rule(Rule("c", ("x", "y", "z")))
        >>> dcfg.add_rule(Rule("c", ("1", "2", "3")))
        >>> dcfg.sentences
        {('b', 'x', 'y', 'z', 'd'), ('b', '1', '2', '3', 'd')}
        """
        if self.start_symbol is None:
            return []

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

    def copy(self):
        """Returns a copy of the grammar."""
        copied = DCFG()
        copied.__graph = self.__graph.copy()  # Shallow copy, but we do not store containers, so it is okay
        copied.__next_rule_id = self.__next_rule_id
        copied.__start_symbol = self.__start_symbol

        return copied

    def load_yacc_file(self, file_path: str) -> None:
        """Load rules from a yacc file.

        Using this function needs bison to be installed and be on PATH.

        Parameters
        ----------
        file_path : str
            The file path of the yacc file.

        Raises
        ------
        ???
            If bison is not available on the system.
        """
        rules = yacc_parse(file_path)

        for rule in rules:
            self.add_rule(rule)

        self.remove_symbol("$end")
        self.start_symbol = "$accept"
        # TODO: Exception handling from bison

    # Private functions

    @property
    def __rule_ids(self):
        return set(filter(lambda node: isinstance(node, RuleId), self.__graph.nodes))

    def __get_next_rule_id(self):
        next_rule_id = self.__next_rule_id

        self.__next_rule_id += 1

        return RuleId(next_rule_id)

    def __rule_exists(self, rule: Rule):
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

    def __get_lhs_by_rule_id(self, rule_id: RuleId):
        assert isinstance(rule_id, RuleId)

        lhss = list(self.__graph.predecessors(rule_id))
        assert len(lhss) == 1

        return lhss[0]

    def __get_rhs_by_rule_id(self, rule_id: RuleId):
        assert isinstance(rule_id, RuleId)

        symbols = []

        for symbol, arcs in self.__graph[rule_id].items():
            for _, arc in arcs.items():
                symbols.append((arc["index"], symbol))

        rhs = tuple([x[1] for x in sorted(symbols)])

        return rhs

    def __get_rule_by_id(self, rule_id: RuleId):
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
