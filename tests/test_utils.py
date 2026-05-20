import pytest
from neologism.utils import (
    is_multidigraph_finite,
    remove_loops_from_multidigraph,
)
from networkx import MultiDiGraph


@pytest.fixture
def finite_multidigraph():
    graph = MultiDiGraph()
    graph.add_edge("a", "b")
    graph.add_edge("b", "c")
    graph.add_edge("c", "d")
    return graph


@pytest.fixture
def infinite_multidigraph():
    graph = MultiDiGraph()
    graph.add_edge("a", "b")
    graph.add_edge("b", "c")
    graph.add_edge("c", "d")
    graph.add_edge("d", "a")
    return graph


def test_is_multidigraph_finite(finite_multidigraph: MultiDiGraph, infinite_multidigraph: MultiDiGraph):
    assert is_multidigraph_finite(finite_multidigraph, "a")
    assert not is_multidigraph_finite(infinite_multidigraph, "a")


def test_remove_loops_from_multidigraph(infinite_multidigraph: MultiDiGraph):
    remove_loops_from_multidigraph(infinite_multidigraph, "a")
    assert is_multidigraph_finite(infinite_multidigraph, "a")
    assert not infinite_multidigraph.has_edge("d", "a")
