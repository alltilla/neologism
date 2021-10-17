import pytest
from neologism.utils import (
    is_multidigraph_finite,
    get_all_combinations,
    raise_type_error_if_not_type_of,
    raise_type_error_if_not_type_of_multiple,
    remove_loops_from_multidigraph,
)
from networkx import MultiDiGraph


def test_raise_type_error_if_not_type_of():
    test_str = "test"

    raise_type_error_if_not_type_of(test_str, str)
    with pytest.raises(TypeError):
        raise_type_error_if_not_type_of(test_str, list)


def test_raise_type_error_if_not_type_of_multiple():
    test_str = "test"
    test_int = 1337

    raise_type_error_if_not_type_of_multiple(test_str, [str, int])
    raise_type_error_if_not_type_of_multiple(test_int, [str, int])
    with pytest.raises(TypeError):
        raise_type_error_if_not_type_of(test_str, [list, set])


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


def test_get_all_combinations():
    possibilites_in_each_position = [
        [["00"], ["01"]],
        [["10"], ["11"], ["120", "121"]],
        [],
        [["30"]],
    ]
    expected = [
        ["00", "10", "30"],
        ["01", "10", "30"],
        ["00", "11", "30"],
        ["01", "11", "30"],
        ["00", "120", "121", "30"],
        ["01", "120", "121", "30"],
    ]

    assert get_all_combinations(possibilites_in_each_position) == expected
