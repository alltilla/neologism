import pytest
from tempfile import NamedTemporaryFile

from neologism import DCFG
from neologism import Rule


@pytest.fixture
def dcfg() -> DCFG:
    rules = [
        Rule("start", ("NT_1",)),
        Rule("NT_1", ("t_1", "t_2", "t_2")),
        Rule("NT_1", ("t_3", "t_4", "NT_1")),
        Rule("NT_1", ("t_5", "NT_2")),
        Rule("NT_1", ()),
        Rule("NT_2", ("t_6",)),
        Rule("NT_2", ("t_7",)),
    ]

    dcfg = DCFG()

    for rule in rules:
        dcfg.add_rule(rule)

    return dcfg


def test_load_yacc_file():
    test_yacc = r"""
        %token t_1
        %token t_2
        %token t_3
        %token t_4
        %token t_5
        %token t_6
        %token t_7
        %%
        start
            : NT_1
            ;
        NT_1
            : t_1 t_2 t_2
            | t_3 t_4 NT_1
            | t_5 NT_2
            {
                int foo = 1337;
                bar(foo);
            }
            |
            ;
        NT_2
            : t_6
            | t_7
            ;
        %%
"""
    with NamedTemporaryFile(mode="w") as f:
        f.write(test_yacc)
        f.flush()
        dcfg = DCFG()
        dcfg.load_yacc_file(f.name)

    expected_symbols = {
        "$accept",
        "start",
        "NT_1",
        "NT_2",
        "t_1",
        "t_2",
        "t_3",
        "t_4",
        "t_5",
        "t_6",
        "t_7",
    }

    expected_rules = {
        Rule("$accept", ("start",)),
        Rule("start", ("NT_1",)),
        Rule("NT_1", ("t_1", "t_2", "t_2")),
        Rule("NT_1", ("t_3", "t_4", "NT_1")),
        Rule("NT_1", ("t_5", "NT_2")),
        Rule("NT_1", ()),
        Rule("NT_2", ("t_6",)),
        Rule("NT_2", ("t_7",)),
    }

    assert dcfg.symbols == expected_symbols
    assert dcfg.rules == expected_rules
    assert dcfg.start_symbol == "$accept"


def test_get_all_symbols(dcfg: DCFG):
    expected = {
        "start",
        "NT_1",
        "NT_2",
        "t_1",
        "t_2",
        "t_3",
        "t_4",
        "t_5",
        "t_6",
        "t_7",
    }
    assert dcfg.symbols == expected


def test_rules_getter(dcfg: DCFG):
    expected = {
        Rule("start", ("NT_1",)),
        Rule("NT_1", ("t_1", "t_2", "t_2")),
        Rule("NT_1", ("t_3", "t_4", "NT_1")),
        Rule("NT_1", ("t_5", "NT_2")),
        Rule("NT_1", ()),
        Rule("NT_2", ("t_6",)),
        Rule("NT_2", ("t_7",)),
    }
    assert dcfg.rules == expected


def test_rules_containing(dcfg: DCFG):
    expected = {
        Rule("start", ("NT_1",)),
        Rule("NT_1", ("t_1", "t_2", "t_2")),
        Rule("NT_1", ("t_3", "t_4", "NT_1")),
        Rule("NT_1", ("t_5", "NT_2")),
        Rule("NT_1", ()),
    }
    assert dcfg.rules_containing("NT_1") == expected


def test_add_rule(dcfg: DCFG):
    dcfg.add_rule(Rule("NT_1", ("foo",)))

    assert Rule("NT_1", ("foo",)) in dcfg.rules


def test_private_rule_exists(dcfg: DCFG):
    assert dcfg._DCFG__rule_exists(Rule("NT_1", ("t_3", "t_4", "NT_1")))
    assert not dcfg._DCFG__rule_exists(Rule("NT_1", ("foo",)))


def test_remove_rule(dcfg: DCFG):
    expected = {
        Rule("start", ("NT_1",)),
        Rule("NT_1", ("t_1", "t_2", "t_2")),
        Rule("NT_1", ("t_3", "t_4", "NT_1")),
        Rule("NT_1", ()),
        Rule("NT_2", ("t_6",)),
        Rule("NT_2", ("t_7",)),
    }

    dcfg.remove_rule(Rule("NT_1", ("t_5", "NT_2")))

    assert dcfg.rules == expected


def test_remove_rule_not_present(dcfg: DCFG):
    with pytest.raises(ValueError):
        dcfg.remove_rule(Rule("NT_2", ()))


def test_remove_symbol(dcfg: DCFG):
    expected_symbols = {
        "start",
        "NT_1",
        "t_1",
        "t_2",
        "t_3",
        "t_4",
        "t_5",
        "t_6",
        "t_7",
    }
    expected_rules = {
        Rule("start", ("NT_1",)),
        Rule("NT_1", ("t_1", "t_2", "t_2")),
        Rule("NT_1", ("t_3", "t_4", "NT_1")),
        Rule("NT_1", ("t_5",)),
        Rule("NT_1", ()),
    }

    dcfg.remove_symbol("NT_2")

    assert dcfg.symbols == expected_symbols
    assert dcfg.rules == expected_rules


def test_remove_symbol_not_present(dcfg: DCFG):
    with pytest.raises(ValueError):
        dcfg.remove_symbol("NT_99")


def test_make_symbol_terminal(dcfg: DCFG):
    expected_symbols = {
        "start",
        "NT_1",
        "NT_2",
        "t_1",
        "t_2",
        "t_3",
        "t_4",
        "t_5",
        "t_6",
        "t_7",
    }
    expected_rules = {
        Rule("start", ("NT_1",)),
        Rule("NT_2", ("t_6",)),
        Rule("NT_2", ("t_7",)),
    }

    dcfg.make_symbol_terminal("NT_1")

    assert dcfg.symbols == expected_symbols
    assert dcfg.rules == expected_rules


def test_make_symbol_terminal_not_present(dcfg: DCFG):
    with pytest.raises(ValueError):
        dcfg.make_symbol_terminal("NT_99")


def test_start_symbol(dcfg: DCFG):
    dcfg.start_symbol = "NT_1"
    assert dcfg.start_symbol == "NT_1"


def test_start_symbol_not_present(dcfg: DCFG):
    with pytest.raises(ValueError):
        dcfg.start_symbol = "NT_99"


def test_is_finite_false(dcfg: DCFG):
    assert not dcfg.is_finite()


def test_is_finite_true(dcfg: DCFG):
    dcfg.remove_rule(Rule("NT_1", ("t_3", "t_4", "NT_1")))
    assert dcfg.is_finite()


def test_get_all_sentences(dcfg: DCFG):
    expected = {
        ("t_1", "t_2", "t_2"),
        ("t_3", "t_4"),
        ("t_5", "t_6"),
        ("t_5", "t_7"),
        (),
    }

    assert dcfg.sentences == expected


def test_copy(dcfg: DCFG):
    copied = dcfg.copy()

    assert copied.rules == dcfg.rules
    assert copied.symbols == dcfg.symbols
    assert copied.start_symbol == dcfg.start_symbol

    new_rule = Rule("NT_1", ("foo",))
    dcfg.add_rule(new_rule)

    assert new_rule in dcfg.rules
    assert new_rule not in copied.rules
