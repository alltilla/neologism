import subprocess
import xml.etree.ElementTree as xml_parser
from os import environ
from tempfile import NamedTemporaryFile
from typing import Optional

from .rule import Rule


class YaccDecodeError(Exception):
    pass


def __run_bison(command: list, custom_path: Optional[str] = None) -> subprocess.CompletedProcess:
    env = environ.copy()
    if custom_path is not None:
        env["PATH"] = custom_path

    return subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )


def __yacc2xml(yacc_file_path: str, custom_path: Optional[str] = None):
    xml_file = NamedTemporaryFile()

    try:
        result = __run_bison(
            ["bison", "--xml=" + xml_file.name, "--output=/dev/null", yacc_file_path],
            custom_path,
        )
    except FileNotFoundError:
        raise ChildProcessError("bison executable not found. PATH: {}".format(environ.get("PATH", "")))

    if result.returncode != 0:
        message = "Failed to parse yacc file: {}".format(yacc_file_path)
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        if stderr:
            message = "{}\n{}".format(message, stderr)
        raise YaccDecodeError(message)

    return xml_file


def __unescape(keyword: str) -> str:
    if len(keyword) == 3 and keyword[0] == "'" and keyword[-1] == "'":
        return keyword.strip("'")
    return keyword


def __xml2rules(xml_file):
    rules = set()

    root = xml_parser.parse(xml_file.name).getroot()
    for rule in root.iter("rule"):
        lhs = __unescape(rule.find("lhs").text)
        rhs = [__unescape(symbol.text) for symbol in rule.find("rhs") if symbol.tag != "empty"]
        rules.add(Rule(lhs, rhs))

    return rules


def parse(file_path: str, custom_path: Optional[str] = None):
    return __xml2rules(__yacc2xml(file_path, custom_path))
