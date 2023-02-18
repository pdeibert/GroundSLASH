from typing import Set, Union, Optional, TYPE_CHECKING

from .expression import Expr

if TYPE_CHECKING:
    from aspy.program.terms import Variable
    
    from .safety_characterization import SafetyTriplet
    from .literals import PredicateLiteral
    from .statements import Statement


class Query(Expr):
    """Query."""
    def __init__(self, atom: "PredicateLiteral") -> None:
        self.atom = atom
        self.ground = atom.ground

    def __str__(self) -> str:
        return f"{str(self.atom)} ?"

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return self.atom.vars()

    def safety(self, rule: Optional[Union["Statement","Query"]]=None, global_vars: Optional[Set["Variable"]]=None) -> "SafetyTriplet":
        return self.atom.safety()