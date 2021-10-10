import pytest
from neologism import Rule


def test_constructor():
    lhs = "symbol1"
    rhs = ("symbol2", "symbol3")
    rule = Rule(lhs, rhs)

    assert rule.lhs == lhs
    assert rule.rhs == rhs


def test_constructor_with_rhs_as_list():
    lhs = "symbol1"
    rhs = ["symbol2", "symbol3"]
    rule = Rule(lhs, rhs)

    assert rule.lhs == lhs
    assert rule.rhs == tuple(rhs)


def test_immutability():
    lhs = "symbol1"
    rhs = ["symbol2", "symbol3"]
    rule = Rule(lhs, rhs)

    with pytest.raises(AttributeError):
        rule.lhs = "other_symbol1"
    with pytest.raises(AttributeError):
        rule.rhs = ("other_symbol2", "other_symbol3")

    rhs.append("symbol4")

    assert rule.rhs != tuple(rhs)


def test_eq():
    rule1 = Rule("symbol1", ("symbol2", "symbol3"))
    rule2 = Rule("symbol1", ("symbol2", "symbol3"))

    assert rule1 == rule2


def test_hash():
    rule1 = Rule("symbol1", ("symbol2", "symbol3"))
    rule2 = Rule("symbol1", ("symbol2", "symbol3"))

    assert hash(rule1) == hash(rule2)

    s = set()
    s.add(rule1)
    s.add(rule2)

    assert len(s) == 1


def test_repr():
    rule = Rule("symbol1", ("symbol2", "symbol3"))

    assert repr(rule) == "Rule('symbol1' => 'symbol2' 'symbol3')"
