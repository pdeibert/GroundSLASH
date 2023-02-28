from typing import Set, Dict, Tuple, List, TYPE_CHECKING
from itertools import chain

from aspy.program.statements import EpsRule, EtaRule
from aspy.program.literals import AlphaLiteral, AggregateLiteral

if TYPE_CHECKING:
    from aspy.program.terms import Term, Number
    from aspy.program.literals import AggregateFunction, AggregateCount, AggregateMin, AggregateMax, AggregateSum, AggregateElement, Literal, Unequal
    from aspy.program.operators import RelOp
    from aspy.program.statements import Statement


class Propagator():
    def __init__(self, aggr_map: Dict[int, Tuple["AggregateLiteral", "AlphaLiteral", EpsRule, List[EtaRule]]]) -> None:
        self.aggr_map = aggr_map
        self.instance_map = dict()

    def propagate(self, eps_instances, eta_instances, I: Set["Literal"], J: Set["Literal"]) -> Set[AlphaLiteral]:

        for rule in chain(eps_instances, eta_instances):

            # get corresponding alpha_literal
            aggr_literal, alpha_literal, *_ = self.aggr_map[rule.aggr_id]

            if isinstance(rule, EpsRule):
                # gather variable substitution
                subst = rule.gather_var_assignment()
                # ground corresponding alpha literal
                ground_alpha_literal = alpha_literal.substitute(subst)

                if ground_alpha_literal not in self.instance_map:
                    self.instance_map[ground_alpha_literal] = (
                        aggr_literal.func,
                        set(),
                        tuple(guard.substitute(subst) if guard is not None else None for guard in aggr_literal.guards)
                    )
            elif isinstance(rule, EtaRule):
                # gather variables
                subst = rule.gather_var_assignment()
                # ground corresponding alpha literal
                ground_alpha_literal = alpha_literal.substitute(subst)

                if ground_alpha_literal not in self.instance_map:
                    self.instance_map[ground_alpha_literal] = (
                        aggr_literal.func,
                        set(),
                        tuple(guard.substitute(subst) if guard is not None else None for guard in aggr_literal.guards)
                    )

                self.instance_map[ground_alpha_literal][1].add(rule.element.substitute(subst))

        possible_alpha_literals = set()

        for ground_alpha_literal, (aggr_func, ground_elements, ground_guards) in self.instance_map.items():
            # skip alpha literal if already derived (TODO: can this even happen?)
            if ground_alpha_literal in J: continue

            # propagate aggregate function to check satisfiability
            satisfiable = aggr_func.propagate(ground_guards, ground_elements, I, J)

            if satisfiable:
                possible_alpha_literals.add(ground_alpha_literal)

        return possible_alpha_literals

    def assemble(self, rules: Set["Statement"]) -> Set["Statement"]:
        # TODO: remove atoms in grounding from domain

        # map ground alpha literals to corresponding assembled aggregate literals to be replaced with
        assembling_map = {
            alpha_literal: AggregateLiteral(aggr_func, tuple(elements), guards, naf=alpha_literal.naf) for alpha_literal, (aggr_func, elements, guards) in self.instance_map.items()
        }

        # return assembled rules
        return set(rule.assemble_aggregates(assembling_map) for rule in rules)