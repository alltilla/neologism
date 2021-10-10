import xml.etree.ElementTree as xml_parser
from os import environ
from subprocess import DEVNULL, Popen
from tempfile import NamedTemporaryFile

from .rule import Rule


class YaccDecodeError(Exception):
    pass


def __run_in_shell(command: list, custom_path: str = None):
    env = environ.copy()
    if custom_path is not None:
        env["PATH"] = custom_path

    proc = Popen(command, stderr=DEVNULL, stdout=DEVNULL, env=env)
    proc.wait()

    return proc.returncode == 0


def __yacc2xml(yacc_file_path: str, custom_path: str = None):
    xml_file = NamedTemporaryFile()

    try:
        if not __run_in_shell(["bison", "--xml=" + xml_file.name, "--output=/dev/null", yacc_file_path], custom_path):
            raise YaccDecodeError("Failed to parse yacc file: {}".format(yacc_file_path))
    except FileNotFoundError:
        raise ChildProcessError("bison executable not found. PATH: {}".format(environ.get("PATH", "")))

    return xml_file


def __xml2rules(xml_file):
    rules = set()

    root = xml_parser.parse(xml_file.name).getroot()
    for rule in root.iter("rule"):
        lhs = rule.find("lhs").text
        rhs = [symbol.text for symbol in rule.find("rhs") if symbol.tag != "empty"]
        rules.add(Rule(lhs, rhs))

    return rules


def parse(file_path: str, custom_path: str = None):
    return __xml2rules(__yacc2xml(file_path, custom_path))
