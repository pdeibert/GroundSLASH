from typing import Optional, TYPE_CHECKING

from aspy.program.literals import PredicateLiteral
from aspy.program.symbol_table import SpecialChar

if TYPE_CHECKING:
    from aspy.program.terms import Variable
    #from aspy.program.literals import Guard


class AlphaLiteral(PredicateLiteral):
    """TODO."""
    def __init__(self, aggr_id: int, *global_vars: "Variable", naf: bool=False) -> None:
        super().__init__(f"{SpecialChar.ALPHA}{aggr_id}", *global_vars, naf=naf)
        self.aggr_id = aggr_id
        self.global_vars = global_vars

        #if lguard == rguard == None:
        #    raise ValueError(f"{type(self)} requires at least one guard to be specified.")
        #self.guards = (lguard, rguard)