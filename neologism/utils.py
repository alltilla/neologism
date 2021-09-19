from networkx import MultiDiGraph
import copy


def raise_type_error_if_not_type_of(variable, type) -> None:
    if not isinstance(variable, type):
        raise TypeError()


def is_multidigraph_finite(graph: MultiDiGraph, start_node) -> bool:
    # TODO: add unit test
    def __is_finite(_graph: MultiDiGraph, node, nodes_traversed: set):
        if node in nodes_traversed:
            return False

        nodes_traversed.add(node)

        for next_node in _graph.successors(node):
            if not __is_finite(_graph, next_node, nodes_traversed):
                return False

        return True

    return __is_finite(graph, start_node, set())


def remove_loops_from_multidigraph(graph: MultiDiGraph, start_node) -> None:
    # TODO: add unit test
    def __remove_loops(_graph: MultiDiGraph, node, nodes_traversed: set):
        nodes_traversed.add(node)

        for next_node in list(_graph.successors(node)):
            if next_node in nodes_traversed:
                _graph.remove_edge(node, next_node)

        for next_node in list(_graph.successors(node)):
            __remove_loops(_graph, next_node, nodes_traversed)

        nodes_traversed.remove(node)

    __remove_loops(graph, start_node, set())


def merge_expansions(expansions_of_each_symbol):
    # TODO: add unit test
    # TODO: generalize variables and function name
    # TODO: add signature hint
    clauses = [[]]

    for expansions_of_symbol in expansions_of_each_symbol:
        clauses_orig_len = len(clauses)
        for _ in range(len(expansions_of_symbol) - 1):
            clauses.extend(copy.deepcopy(clauses[:clauses_orig_len]))

        clause_index = 0
        for element in expansions_of_symbol:
            for _ in range(clauses_orig_len):
                clauses[clause_index].extend(element)
                clause_index += 1

    return clauses
