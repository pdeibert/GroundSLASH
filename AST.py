from typing import Set, Tuple
from abc import ABC
from enum import Enum
from dataclasses import dataclass


class Expr(ABC):
    """Abstract base class for all expressions."""
    pass

# ----- operators -----

class ArithOp(Enum):
    PLUS    = 0 
    MINUS   = 1
    TIMES   = 2
    DIV     = 3

    """
    @classmethod
    def from_operator(cls, operator: str):
        if operator == "+":
            value = 0
        elif operator == "-":
            value = 1
        elif operator == "*":
            value = 2
        elif operator == "/":
            value = 3
        else:
            # TODO
            raise Exception
        
        return cls(value)
    """

class RelOp(Enum):
    EQUAL           = 0
    UNEQUAL         = 1
    LESS            = 2
    GREATER         = 3
    LESS_OR_EQ      = 4
    GREATER_OR_EQ   = 5

    """
    @classmethod
    def from_operator(cls, operator: str):
        if operator == "=":
            value = 0
        elif operator == "!=":
            value = 1
        elif operator == "<":
            value = 2
        elif operator == ">":
            value = 3
        elif operator == "<=":
            value = 4
        elif operator == ">=":
            value = 5
        else:
            # TODO
            raise Exception

        return cls(value)
    """

class AggrOp(Enum):
    COUNT   = 0
    SUM     = 1
    MAX     = 2
    MIN     = 3

    """
    @classmethod
    def from_operator(cls, operator: str):
        if operator == "#count":
            value = 0
        elif operator == "#sum":
            value = 1
        elif operator == "#max":
            value = 2
        elif operator == "#min":
            value = 3
        else:
            # TODO
            raise Exception
        
        return cls(value)
    """

# ----- terms -----

class Term(ABC):
    """Abstract base class for all terms."""

@dataclass
class Id(Term):
    """Identifier."""
    name: str
    terms: Tuple[Term]

@dataclass
class Variable(Term):
    """Variable."""
    name: str

class AnonVariable(Term):
    """Anonymous variable."""
    pass

class ArithTerm(Term, ABC):
    """Abstract base class for all arithmetic terms."""
    pass

@dataclass
class UnaryArithTerm(ArithTerm):
    """Unary arithmetic term."""
    term: Term

@dataclass
class BinaryArithTerm(ArithTerm):
    """Binary arithmetic term."""
    operator: ArithOp
    lterm: Term
    rterm: Term

@dataclass
class FuncTerm(Term):
    """Functional term."""
    id: str
    term: Tuple[Term]

# ----- atoms & literals -----

class Atom(ABC):
    """Abstract base class for all atoms."""
    pass

class Literal(ABC):
    """Abstract base class for all literals."""
    pass

@dataclass
class PredAtom(Atom):
    """Predicate atom."""
    id: str
    terms: Tuple[Term]

@dataclass
class ClassicalAtom(Atom): # same as classical_literal
    """Classical atom."""
    atom: PredAtom
    neg: bool

@dataclass
class DefaultAtom(Expr): # not a strict atom; auxiliary class
    """Default atom."""
    atom: ClassicalAtom
    neg: bool

class NafLiteral(Literal, ABC):
    """Negation-as-failure (Naf) literal.
    
    Can be either a built-in atom, a classical atom or the (default) negation of a classical atom.

    A Naf-literal is positive, if it is a built-in atom or a classical atom, else negative.
    """
    pass

@dataclass
class BuiltinAtom(Atom, NafLiteral):
    """Built-in atom."""
    operator: RelOp
    lterm: Term
    rterm: Term

@dataclass
class AggrElement(Expr):
    """Aggregate element."""
    term: Tuple[Term]
    literals: Tuple[NafLiteral]

@dataclass
class AggrAtom(Atom):
    """Aggregate atom."""
    elements: Tuple[AggrElement] # TODO: infinite?
    term: Term
    aggr_operator: AggrOp
    rel_operator: RelOp

@dataclass
class AggrLiteral(Literal):
    """Aggregate literal."""
    atom: AggrAtom
    neg: bool

@dataclass
class ChoiceElement(Expr):
    """Choice element."""
    atom: ClassicalAtom
    literals: Tuple[NafLiteral]

@dataclass
class ChoiceAtom(Atom):
    """Choice atom."""
    elements: Tuple[ChoiceElement]
    term: Term
    rel_operator: RelOp

# ----- statements -----

class Statement(Expr, ABC):
    """Abstract base class for all statements."""
    pass

@dataclass
class Disjunction(Expr):
    literals: Tuple[ClassicalAtom]

    def __len__(self) -> int:
        return len(self.literals)

@dataclass
class Conjunction(Expr):
    literals: Tuple[Literal]

    def __len__(self) -> int:
        return len(self.literals)

    def getPositive(self) -> "Conjunction":

        positive_literals = []

        for literal in self.literals:
            if isinstance(literal, BuiltinAtom) or (isinstance(literal, ClassicalAtom) and not literal.neg):
                positive_literals.append(literal)
        
        return Conjunction(tuple(positive_literals))

    def getNegative(self) -> "Conjunction":

        negative_literals = []

        for literal in self.literals:
            if isinstance(literal, ClassicalAtom) and literal.neg:
                negative_literals.append(literal)
        
        return Conjunction(tuple(negative_literals))

class Rule(Statement, ABC):
    """Abstract base class for all rules."""
    pass

@dataclass
class DisjunctiveRule(Rule):
    """Disjunctive rule.
    
    Rule of form:

        h_1 | ... | h_m :- b_1,...,b_n.
    
    for classical atoms h_1,...,h_m and literals b_1,...,b_n.
    """
    head: Disjunction
    body: Conjunction

class NormalRule(DisjunctiveRule):
    """Normal rule.

    Special case of a disjunctive rule where the head contains a single literal:

        'h :- b_1, ..., b_n.'

    for classical atom h and literals b_1,...,b_n.
    """
    def __init__(self, head: ClassicalAtom, body: Conjunction):
        self.head = Disjunction( (ClassicalAtom,) )
        self.body = body

class Fact(DisjunctiveRule):
    """Fact.
    
    Special case of a disjunctive rule where the body is empty:

        h_1 | ... | h_m :-.

    or simply

        h_1 | ... | h_m.
    
    for classical atoms h_1,...,h_m.
    """
    def __init__(self, head: Disjunction):
        self.head = head
        self.body = Conjunction(tuple())

class Constraint(DisjunctiveRule):
    """Constraint.
    
    Special case of a disjunctive rule where the head is empty:

        :- b_1,...,b_n.
    
    for literals b_1,...,b_n.
    """
    def __init__(self, body: Conjunction):
        self.head = Disjunction(tuple())
        self.body = body

class WeakConstraint(Rule):
    # TODO
    pass

# Choice Rule
class ChoiceRule(Rule):
    # TODO
    pass

# Weight Rule ?
class WeightRule(Rule):
    # TODO
    pass

# Minimize Statement?
class MinimizeStatement(Statement):
    # TODO
    pass

# Disjunctive Rule (Rule that is not a normal rule!)

# Aggregate Relation
# TODO:

# ----- queries -----

@dataclass
class Query:
    """Query."""
    atom: ClassicalAtom