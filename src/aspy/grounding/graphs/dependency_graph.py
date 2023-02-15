# positive literals:
#       pos. classical literal
#       built-in literals are neither positive nor negative (???)
#       WHAT ABOUT NEGATIVE AGGREGATES?
#
# positive occurrences in aggregate elements E:
#       
#       

# literal.pos():
#       pos. classical literal/aggregate literal -> set(self)
#       _ -> set()
# literal.neg():
#       neg. classical literal/aggregate literal -> set(self)
#       _ -> set()
#
# aggr.pos():
#       -> set.union(*tuple(e.body for e in self.elements))
# aggr.neg():
#       aggr monotone (???) -> set()
#       _ -> set.union(*tuple(e.body for e in self.elements))
#
# literal_set.pos():
#       -> set().union(*tuple(literal.pos() for literal in self.literals))
# literal_set.neg():
#       -> set().union(*tuple(literal.pos() for literal in self.literals))

# pred(a) = "name/arity"
# pred(A) = {pred(atom) for atom in A}

# Inter-Rule dependency:
#       rule r1 pos. depends on rule r2 if pred(H(r2)) in pred(B(r1).pos())
#               neg.                                   in pred(B(r1).neg())
#           -> i.e. r2 requires predicates defined in r1 to infer its head
#
#       facts depend on no other rules

from typing import Tuple, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from aspy.program.statements import Statement


class DependencyGraph():
    def __init__(self, rules: Tuple["Statement", ...]) -> None:
        self.nodes = rules

        self.pos_edges = set()
        self.neg_edges = set()

        for dependee in rules:

            head_predicates = set(literal.pred() for literal in dependee.head)

            for depender in rules:

                # skip self
                if depender is dependee:
                    continue

                pos_body_predicates = set([literal.pred() for literal in depender.body.pos()])
                neg_body_predicates = set([literal.pred() for literal in depender.body.neg()])

                # positive dependency
                if head_predicates.intersection(pos_body_predicates):
                    self.pos_edges.add( (depender, dependee) )

                # negative dependency
                if head_predicates.intersection(neg_body_predicates):
                    self.neg_edges.add( (depender, dependee) )

    @property
    def edges(self) -> Set[Tuple["Statement", "Statement"]]:
        return self.pos_edges.union(self.neg_edges)