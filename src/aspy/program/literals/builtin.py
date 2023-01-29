from typing import Optional, Set, Dict, TYPE_CHECKING
from abc import abstractmethod

from aspy.program.expression import Substitution, MatchError, AssignmentError
from aspy.program.safety import Safety, SafetyRule

from .literal import Literal

if TYPE_CHECKING:
    from aspy.program.expression import Expr
    from aspy.program.terms import Term, Variable


class BuiltinLiteral(Literal):
    def __init__(self, loperand: "Term", roperand: "Term") -> None:
        # built-in literals are always positive
        super().__init__(naf=False)

        self.loperand = loperand
        self.roperand = roperand

    @abstractmethod
    def evaluate(self) -> bool:
        pass

    def vars(self) -> Set["Variable"]:
        return self.loperand.vars().union(self.roperand.vars())

    def safety(self) -> Safety:
        # global variables are irrelevant
        return Safety(set(),self.vars(),set())


class Equal(BuiltinLiteral):
    def __repr__(self) -> str:
        return f"Equal({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}={str(self.roperand)}"

    def safety(self) -> Safety:
        # overrides inherited safety method

        # get variables in both terms
        lvars = self.loperand.vars()
        rvars = self.roperand.vars()

        rules = set([SafetyRule(var, lvars) for var in rvars] + [SafetyRule(var, rvars) for var in lvars])

        return Safety.normalize(set(), self.vars(), rules)

    def evaluate(self) -> bool:
        # TODO: evaluate recursively?
        return self.loperand == self.roperand  

    def substitute(self, subst: Dict[str, "Term"]) -> "Equal":
        return Equal(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst)
        )

    def match(self, other: "Expr", subst: Optional[Substitution]=None) -> Substitution:
        if subst is None:
            subst = Substitution()

        # 'other' is an equality built-in atom
        if isinstance(other, Equal):

            # create a copy of the original substitution
            subst_copy = subst.copy()
            
            # try to match in order
            try:
                # match left operand
                term_subst = self.loperand.match(other.loperand)

                # combine substitutions
                subst.merge(term_subst)

                # match right operand
                term_subst = self.roperand.match(other.roperand)

                # combine substitutions
                subst.merge(term_subst)

                # return final substitution
                return subst
            except (MatchError, AssignmentError):
                # restore original substitution
                subst = subst_copy
                # try to match in switched order
                try:
                    # match left operand to right operand
                    term_subst = self.loperand.match(other.roperand)

                    # combine substitutions
                    subst.merge(term_subst)

                    # match right operand to left operand
                    term_subst = self.roperand.match(other.loperand)

                    # combine substitutions
                    subst.merge(term_subst)

                    # return final substitution
                    return subst
                except (MatchError, AssignmentError):
                    raise MatchError(self, other)
        else:
            # cannot be matched
            raise MatchError(self, other)


class Unequal(BuiltinLiteral):
    def __repr__(self) -> str:
        return f"Unequal({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}!={str(self.roperand)}"

    def evaluate(self) -> bool:
        # TODO: evaluate recursively?
        return self.loperand != self.roperand

    def substitute(self, subst: Dict[str, "Term"]) -> "Unequal":
        return Unequal(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst)
        )

    def match(self, other: "Expr", subst: Optional[Substitution]=None) -> Substitution:
        if subst is None:
            subst = Substitution()

        # 'other' is an unequality built-in atom
        if isinstance(other, Unequal):

            # create a copy of the original substitution
            subst_copy = subst.copy()
            
            # try to match in order
            try:
                # match left operand
                term_subst = self.loperand.match(other.loperand)

                # combine substitutions
                subst.merge(term_subst)

                # match right operand
                term_subst = self.roperand.match(other.roperand)

                # combine substitutions
                subst.merge(term_subst)

                # return final substitution
                return subst
            except (MatchError, AssignmentError):
                # restore original substitution
                subst = subst_copy
                # try to match in switched order
                try:
                    # match left operand to right operand
                    term_subst = self.loperand.match(other.roperand)

                    # combine substitutions
                    subst.merge(term_subst)

                    # match right operand to left operand
                    term_subst = self.roperand.match(other.loperand)

                    # combine substitutions
                    subst.merge(term_subst)

                    # return final substitution
                    return subst
                except (MatchError, AssignmentError):
                    raise MatchError(self, other)
        else:
            # cannot be matched
            raise MatchError(self, other)


class Less(BuiltinLiteral):
    def __repr__(self) -> str:
        return f"Less({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}<{str(self.roperand)}"

    def evaluate(self) -> bool:
        # TODO: evaluate recursively?
        return self.loperand < self.roperand

    def substitute(self, subst: Dict[str, "Term"]) -> "Less":
        return Less(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst)
        )

    def match(self, other: "Expr", subst: Optional[Substitution]=None) -> Substitution:
        if subst is None:
            subst = Substitution()

        # 'other' is an less-than built-in atom
        if isinstance(other, Less):
            # match terms
            try:
                # match left operand
                term_subst = self.loperand.match(other.loperand)

                # combine substitutions
                subst.merge(term_subst)

                # match right operand
                term_subst = self.roperand.match(other.roperand)

                # combine substitutions
                subst.merge(term_subst)

                # return final substitution
                return subst
            except (MatchError, AssignmentError):
                raise MatchError(self, other)
        # 'other' is an greater-than built-in atom
        elif isinstance(other, Greater):
            # TODO: should we even do this?
            # match terms
            try:
                # match left operand with right operand
                term_subst = self.loperand.match(other.roperand)

                # combine substitutions
                subst.merge(term_subst)

                # match right operand with left operand
                term_subst = self.roperand.match(other.loperand)

                # combine substitutions
                subst.merge(term_subst)

                # return final substitution
                return subst
            except (MatchError, AssignmentError):
                raise MatchError(self, other)
        else:
            # cannot be matched
            raise MatchError(self, other)


class Greater(BuiltinLiteral):
    def __repr__(self) -> str:
        return f"Greater({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}>{str(self.roperand)}"

    def evaluate(self) -> bool:
        # TODO: evaluate recursively?
        return self.loperand > self.roperand

    def substitute(self, subst: Dict[str, "Term"]) -> "Greater":
        return Greater(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst)
        )

    def match(self, other: "Expr", subst: Optional[Substitution]=None) -> Substitution:
        if subst is None:
            subst = Substitution()

        # 'other' is an greater-than built-in atom
        if isinstance(other, Greater):
            # match terms
            try:
                # match left operand
                term_subst = self.loperand.match(other.loperand)

                # combine substitutions
                subst.merge(term_subst)

                # match right operand
                term_subst = self.roperand.match(other.roperand)

                # combine substitutions
                subst.merge(term_subst)

                # return final substitution
                return subst
            except (MatchError, AssignmentError):
                raise MatchError(self, other)
        # 'other' is an less-than built-in atom
        elif isinstance(other, Less):
            # TODO: should we even do this?
            # match terms
            try:
                # match left operand with right operand
                term_subst = self.loperand.match(other.roperand)

                # combine substitutions
                subst.merge(term_subst)

                # match right operand with left operand
                term_subst = self.roperand.match(other.loperand)

                # combine substitutions
                subst.merge(term_subst)

                # return final substitution
                return subst
            except (MatchError, AssignmentError):
                raise MatchError(self, other)
        else:
            # cannot be matched
            raise MatchError(self, other)


class LessEqual(BuiltinLiteral):
    def __repr__(self) -> str:
        return f"LessEqual({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}<={str(self.roperand)}"

    def evaluate(self) -> bool:
        # TODO: evaluate recursively?
        return self.loperand <= self.roperand

    def substitute(self, subst: Dict[str, "Term"]) -> "LessEqual":
        return LessEqual(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst)
        )

    def match(self, other: "Expr", subst: Optional[Substitution]=None) -> Substitution:
        if subst is None:
            subst = Substitution()

        # 'other' is an less-than-or-equal built-in atom
        if isinstance(other, LessEqual):
            # match terms
            try:
                # match left operand
                term_subst = self.loperand.match(other.loperand)

                # combine substitutions
                subst.merge(term_subst)

                # match right operand
                term_subst = self.roperand.match(other.roperand)

                # combine substitutions
                subst.merge(term_subst)

                # return final substitution
                return subst
            except (MatchError, AssignmentError):
                raise MatchError(self, other)
        # 'other' is an greater-than-or-equal built-in atom
        elif isinstance(other, GreaterEqual):
            # TODO: should we even do this?
            # match terms
            try:
                # match left operand with right operand
                term_subst = self.loperand.match(other.roperand)

                # combine substitutions
                subst.merge(term_subst)

                # match right operand with left operand
                term_subst = self.roperand.match(other.loperand)

                # combine substitutions
                subst.merge(term_subst)

                # return final substitution
                return subst
            except (MatchError, AssignmentError):
                raise MatchError(self, other)        
        else:
            # cannot be matched
            raise MatchError(self, other)


class GreaterEqual(BuiltinLiteral):
    def __repr__(self) -> str:
        return f"GreaterEqual({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}>={str(self.roperand)}"

    def evaluate(self) -> bool:
        # TODO: evaluate recursively?
        return self.loperand >= self.roperand

    def substitute(self, subst: Dict[str, "Term"]) -> "GreaterEqual":
        return GreaterEqual(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst)
        )

    def match(self, other: "Expr", subst: Optional[Substitution]=None) -> Substitution:
        if subst is None:
            subst = Substitution()

        # 'other' is an greater-than-or-equal built-in atom
        if isinstance(other, GreaterEqual):
            # match terms
            try:
                # match left operand
                term_subst = self.loperand.match(other.loperand)

                # combine substitutions
                subst.merge(term_subst)

                # match right operand
                term_subst = self.roperand.match(other.roperand)

                # combine substitutions
                subst.merge(term_subst)

                # return final substitution
                return subst
            except (MatchError, AssignmentError):
                raise MatchError(self, other)
        # 'other' is an less-than-or-equal built-in atom
        elif isinstance(other, LessEqual):
            # TODO: should we even do this?
            # match terms
            try:
                # match left operand with right operand
                term_subst = self.loperand.match(other.roperand)

                # combine substitutions
                subst.merge(term_subst)

                # match right operand with left operand
                term_subst = self.roperand.match(other.loperand)

                # combine substitutions
                subst.merge(term_subst)

                # return final substitution
                return subst
            except (MatchError, AssignmentError):
                raise MatchError(self, other)
        else:
            # cannot be matched
            raise MatchError(self, other)