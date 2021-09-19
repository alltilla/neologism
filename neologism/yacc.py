import xml.etree.ElementTree as xml_parser
from subprocess import DEVNULL, Popen
from tempfile import NamedTemporaryFile

from .rule import Rule


def __run_in_shell(command: list):
    proc = Popen(command, stderr=DEVNULL, stdout=DEVNULL)
    proc.wait()

    return proc.returncode == 0


def __yacc2xml(yacc_file_path: str):
    xml_file = NamedTemporaryFile()

    try:
        if not __run_in_shell(["bison", "--xml=" + xml_file.name, "--output=/dev/null", yacc_file_path]):
            raise Exception("Failed to convert to xml:\n{}\n".format(yacc_file_path))
    except FileNotFoundError:
        raise Exception("bison executable not found")

    return xml_file


def __xml2rules(xml_file):
    rules = set()

    root = xml_parser.parse(xml_file.name).getroot()
    for rule in root.iter("rule"):
        lhs = rule.find("lhs").text
        rhs = [symbol.text for symbol in rule.find("rhs") if symbol.tag != "empty"]
        rules.add(Rule(lhs, rhs))

    return rules


def parse(file_path: str):
    return __xml2rules(__yacc2xml(file_path))
