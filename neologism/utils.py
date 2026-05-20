from networkx import MultiDiGraph


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
