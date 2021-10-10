from tempfile import NamedTemporaryFile
import pytest

from neologism.yacc import parse, YaccDecodeError
from neologism import Rule


def __create_temp_file_with_content(content):
    file = NamedTemporaryFile(mode="w")
    file.write(content)
    file.flush()
    return file


@pytest.fixture
def yacc_file():
    test_string = r"""
%token test1
%token test1next
%token test2
%token test2next
%token KW_TEST
%token number
%token string
%%
start
    : test
    ;
test
    : test1 test1next test1next
    | test2 test2next test
    | KW_TEST '(' test_opts ')'
      {
        int foo = 1337;
        bar(foo);
      }
    |
    ;
test_opts
    : number
    | string
    ;
%%
"""
    return __create_temp_file_with_content(test_string)


def test_failed_parse():
    with pytest.raises(YaccDecodeError):
        yacc_file = __create_temp_file_with_content("invalid yacc string")
        parse(yacc_file.name)


def test_parse_yacc(yacc_file):
    expected = {
        Rule("$accept", ("start", "$end")),
        Rule("start", ("test",)),
        Rule("test", ("test1", "test1next", "test1next")),
        Rule("test", ("test2", "test2next", "test")),
        Rule("test", ("KW_TEST", "'('", "test_opts", "')'")),
        Rule("test", ()),
        Rule("test_opts", ("number",)),
        Rule("test_opts", ("string",)),
    }

    assert parse(yacc_file.name) == expected
