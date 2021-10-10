class Rule:
    """A class that is used to create and modify the context-free grammar.

    The API uses str for symbols.
    """

    def __init__(self, lhs: str, rhs: tuple) -> None:
        #  TODO: assert rhs is list or tuple
        self.__lhs = lhs
        self.__rhs = tuple(rhs)

    @property
    def lhs(self) -> str:
        return self.__lhs

    @property
    def rhs(self) -> tuple:
        return self.__rhs

    def __repr__(self) -> str:
        return "Rule({} => {})".format(repr(self.lhs), " ".join([repr(symbol) for symbol in self.rhs]))

    def __eq__(self, other) -> bool:
        return self.lhs == other.lhs and self.rhs == other.rhs

    def __hash__(self) -> int:
        return hash((self.lhs, self.rhs))
