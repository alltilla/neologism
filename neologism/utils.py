from networkx import MultiDiGraph
import copy
import typing


def raise_type_error_if_not_type_of(variable: typing.Any, type: type) -> None:
    if not isinstance(variable, type):
        raise TypeError()


def raise_type_error_if_not_type_of_multiple(variable: typing.Any, types: typing.List[type]) -> None:
    match = False

    for type in types:
        if not isinstance(variable, type):
            continue
        match = True
        break

    if not match:
        raise TypeError()


def is_multidigraph_finite(graph: MultiDiGraph, start_node) -> bool:
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
    def __remove_loops(_graph: MultiDiGraph, node, nodes_traversed: set):
        nodes_traversed.add(node)

        for next_node in list(_graph.successors(node)):
            if next_node in nodes_traversed:
                _graph.remove_edge(node, next_node)

        for next_node in list(_graph.successors(node)):
            __remove_loops(_graph, next_node, nodes_traversed)

        nodes_traversed.remove(node)

    __remove_loops(graph, start_node, set())


def get_all_combinations(
    possibilites_in_each_position: typing.List[typing.List[typing.List]],
) -> typing.List[typing.List]:

    combinations = [[]]

    for possibilities_in_position in possibilites_in_each_position:
        combinations_orig_len = len(combinations)
        for _ in range(len(possibilities_in_position) - 1):
            combinations.extend(copy.deepcopy(combinations[:combinations_orig_len]))

        idx = 0
        for possibility in possibilities_in_position:
            for _ in range(combinations_orig_len):
                combinations[idx].extend(possibility)
                idx += 1

    return combinations
