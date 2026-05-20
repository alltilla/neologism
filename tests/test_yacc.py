from os import environ
from subprocess import CompletedProcess
from tempfile import NamedTemporaryFile
from unittest.mock import patch

import pytest
from neologism import Rule
from neologism.yacc import YaccDecodeError, parse


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
    yacc_file = __create_temp_file_with_content("invalid yacc string")
    with pytest.raises(YaccDecodeError) as excinfo:
        parse(yacc_file.name)

    message = str(excinfo.value)
    assert yacc_file.name in message
    # Bison should have something to say about an invalid yacc input; surface it.
    assert "\n" in message, f"expected bison stderr in error message, got: {message!r}"


def test_no_bison(yacc_file):
    with pytest.raises(ChildProcessError):
        parse(yacc_file.name, custom_path="")


def test_failed_parse_without_stderr(yacc_file):
    # In practice bison always emits stderr on failure, so this case is
    # exercised via a mock to lock in the message-without-newline contract.
    fake = CompletedProcess(args=[], returncode=1, stderr=b"")

    with patch("neologism.yacc.subprocess.run", return_value=fake):
        with pytest.raises(YaccDecodeError) as excinfo:
            parse(yacc_file.name)

    message = str(excinfo.value)
    assert yacc_file.name in message
    assert "\n" not in message


def test_parse_yacc(yacc_file):
    expected = {
        Rule("$accept", ("start", "$end")),
        Rule("start", ("test",)),
        Rule("test", ("test1", "test1next", "test1next")),
        Rule("test", ("test2", "test2next", "test")),
        Rule("test", ("KW_TEST", "(", "test_opts", ")")),
        Rule("test", ()),
        Rule("test_opts", ("number",)),
        Rule("test_opts", ("string",)),
    }

    assert parse(yacc_file.name) == expected
