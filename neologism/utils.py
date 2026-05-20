from networkx import MultiDiGraph


def is_multidigraph_finite(graph: MultiDiGraph, start_node) -> bool:
    on_stack: set = set()
    done: set = set()

    def __is_finite(node) -> bool:
        # A node already on the DFS stack closes a cycle.
        if node in on_stack:
            return False
        # A node whose subtree was fully validated is reusable: this is what
        # makes the check correct (and not exponential) on diamond patterns
        # where two ancestors both reach the same shared subgraph.
        if node in done:
            return True

        on_stack.add(node)
        for next_node in graph.successors(node):
            if not __is_finite(next_node):
                return False
        on_stack.remove(node)
        done.add(node)
        return True

    return __is_finite(start_node)


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
