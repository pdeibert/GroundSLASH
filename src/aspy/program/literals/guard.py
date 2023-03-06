from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.expression import Expr
    from aspy.program.operators import RelOp
    from aspy.program.substitution import Substitution
    from aspy.program.terms import Term
    from aspy.program.variable_table import VariableTable


class Guard(NamedTuple):
    op: "RelOp"
    bound: "Term"
    right: bool

    def __str__(self) -> str:
        if self.right:
            return f"({str(self.op)} {str(self.bound)})"
        else:
            return f"({str(self.bound)} {str(self.op)})"

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, Guard) and self.right == other.right and self.op == other.op and self.bound == other.bound
        )

    def __hash__(self) -> int:
        return hash(("guard", self.op, self.bound, self.right))

    def to_left(self) -> "Guard":
        if self.right:
            return Guard(-self.op, self.term, False)
        return self.copy()

    def to_right(self) -> "Guard":
        if not self.right:
            return Guard(-self.op, self.term, True)
        return self.copy()

    def ground(self) -> bool:
        return self.bound.ground

    def substitute(self, subst: "Substitution") -> "Guard":
        return Guard(self.op, self.bound.substitute(subst), self.right)

    def replace_arith(self, var_table: "VariableTable") -> "Guard":
        return Guard(self.op, self.bound.replace_arith(var_table), self.right)
