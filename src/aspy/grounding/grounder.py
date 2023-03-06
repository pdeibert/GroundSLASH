from typing import Set, Optional, TYPE_CHECKING
from collections import defaultdict
from copy import deepcopy

from aspy.program.literals import Naf, PredicateLiteral, BuiltinLiteral, AggregateLiteral, Equal
from aspy.program.terms import ArithVariable
from aspy.program.substitution import Substitution
from aspy.program.program import Program

from .propagation import Propagator
from .graphs import ComponentGraph

if TYPE_CHECKING: # pragma: no cover
    from aspy.program.statements import Statement
    from aspy.program.literals import Literal, LiteralTuple


class Grounder:
    def __init__(self, prog: Program) -> None:

        if not prog.safe:
            raise ValueError("Grounding requires program to be safe.")

        self.prog = prog

    @classmethod
    def select(cls, literals: "LiteralTuple", subst: Optional[Substitution]=None) -> "Literal":
        if subst is None:
            # initialize with empty/identity substitution
            subst = Substitution()

        # find appropriate literal
        for literal in literals:
            if isinstance(literal, AggregateLiteral):
                # TODO: raise exception (should have been replaced)
                raise ValueError(f"Aggregate literals should be replaced before calling {cls.select} during grounding.")

            # either literal is positive (pos_occ() is non-empy) or the literal is ground under the substitution (all variables in 'literal' are replaced by 'subst')
            if literal.pos_occ() or all(subst[var].ground for var in literal.vars()):
                return literal

        raise ValueError("Tuple of literals does not contain any appropriate literals for 'select'.")

    @classmethod
    def matches(cls, literal: "Literal", certain: Optional[Set["Literal"]]=None, possible: Optional[Set["Literal"]]=None, subst: Optional["Substitution"]=None) -> Set["Substitution"]:
        # initialize optional arguments
        if subst is None:
            subst = Substitution()
        if certain is None:
            certain = set()
        if possible is None:
            possible = set()

        # apply (partial) substitution
        literal = literal.substitute(subst)

        if isinstance(literal, PredicateLiteral):
            # positive predicate literal
            if not literal.naf:
                matches = set()

                if literal.ground:
                    if literal in possible:
                        matches.add(subst)
                else:
                    # compute possible match substitutions
                    for target in possible:
                        match = literal.substitute(subst).match(target)

                        if match is not None:
                            matches.add(subst.compose(match))

                return matches
            # ground negative predicate literal
            elif literal.ground:
                # literal does not contradict set of certain (positive) literals (used as a check)
                return {subst} if Naf(deepcopy(literal), False) not in certain else set()
        # ground built-in literal
        elif isinstance(literal, BuiltinLiteral) and literal.ground:
            # relation holds (used as a check)
            return {subst} if literal.eval() else set()

        # should not happen (just in case)
        raise ValueError(f"{cls.matches} undefined for literal {str(literal)}.")

    @classmethod
    def ground_statement(cls, statement: "Statement", literals: Optional["LiteralTuple"]=None, certain: Optional[Set["Literal"]]=None, possible: Optional[Set["Literal"]]=None, prev_possible: Optional[Set["Literal"]]=None, subst: Optional["Substitution"]=None, duplicate: bool=False,) -> Set["Statement"]:
        """Algorithm 1 from TODO."""
        if statement.contains_aggregates:
            raise ValueError(f"{cls.ground_statement} requires statement to be free of aggregates.")
        if not statement.safe:
            raise ValueError(f"{cls.ground_statement} can only instantiate safe statements.")

        # initialize optional arguments
        if subst is None:
            subst = Substitution()
        if certain is None:
            certain = set()
        if possible is None:
            possible = set()
        if prev_possible is None:
            prev_possible = set()
        if literals is None:
            # get body literals
            literals = statement.body

        # while literals to be processed
        if literals:
            # select positive predicate or ground literal
            literal = cls.select(literals, subst)

            # compute matches for selected literal and move on to grounding remaining literals
            return set().union(
                *tuple(cls.ground_statement(statement, literals.without(literal), certain, possible, prev_possible, match, duplicate) for match in cls.matches(literal, certain, possible, subst))
            )
        else:
            # check replaced arithmetic terms
            for var, target in subst.items():
                if isinstance(var, ArithVariable):
                    # if arithmetic term is not valid -> no valid instantiation
                    if not Equal(target, var.orig_term.substitute(subst)).eval():
                        return set()

            # instantiate final (ground) statement
            ground_statement = statement.substitute(subst)

            if not duplicate or not ground_statement.body.pos_occ().issubset(prev_possible):
                return {ground_statement}

        # duplicate instantiation
        return set()

    def ground_component(self, component: Program, I: Optional[Set["Literal"]]=None, J: Optional[Set["Literal"]]=None) -> Set["Statement"]:
        if not component.statements:
            return set()

        # initialize optional arguments
        if I is None:
            I = set()
        if J is None:
            J = set()

        # initialize sets of instances/literals
        alpha_instances = set()
        eps_instances = set()
        eta_instances = set()

        # NOTE: as implemented by 'mu-gringo', different to the algorithm in the original paper. use of J, J' during grounding of epsilon & eta rules somehow results in incorrect groundings.
        K = I.union(J)
        prev_K = set()

        J_alpha = set()
        prev_J_alpha = set()
        prev_J = set()

        # initialize flag
        duplicate = False

        prog_alpha, prog_eps, prog_eta, aggr_map = component.rewrite_aggregates()
        # initialize propagator
        propagator = Propagator(aggr_map)

        converged = False

        while not converged:

            # ground epsilon rules (encode the satisfiability of aggregates without any element instances)
            eps_instances.update( set().union(*tuple(self.ground_statement(rule, rule.body, I, K, prev_K, Substitution(), duplicate) for rule in prog_eps.statements)) )
            # ground eta rules (encode the satisfiability of aggregate elements)
            eta_instances.update( set().union(*tuple(self.ground_statement(rule, rule.body, I, K, prev_K, Substitution(), duplicate) for rule in prog_eta.statements)) )

            # propagate aggregates
            J_alpha = propagator.propagate(eps_instances, eta_instances, I, J, J_alpha)

            # ground remaining rules (including non-aggregate rules)
            alpha_instances.update( set().union(*tuple(self.ground_statement(rule, rule.body, I, J.union(J_alpha), prev_J.union(prev_J_alpha), Substitution(), duplicate) for rule in prog_alpha.statements)) )

            # update state
            duplicate = True
            prev_J_alpha = J_alpha.copy()
            prev_J = J.copy()
            prev_K = K.copy()

            # NOTE: 'pos_occ' applicable since all head literals are positive predicate literals
            head_literals = set().union(*tuple(rule.head.pos_occ() for rule in alpha_instances))

            J.update(head_literals)
            K.update(head_literals)

            # enough to check lengths instead of elements (much cheaper)
            if len(J) == len(prev_J): 
                converged = True

        # assemble aggregates (if present)
        assembled_instances = propagator.assemble(alpha_instances)

        # return re-assembled rules
        return assembled_instances

    def ground(self) -> Program:

        # compute component graph for rules/facts only
        component_graph = ComponentGraph(self.prog.statements) # rules/facts only???

        # compute component instantiation sequence
        inst_sequence = component_graph.sequence()

        # initialize sets of certain and possible statement instantiations
        certain_inst = set()
        possible_inst = set()

        # initialize sets of certain and possible literal instantiations (follow from head literals of statement instantiations)
        certain_literals = set()
        possible_literals = set()

        for component in inst_sequence:
            # compute counter of occurring head predicates (used to indicate which predicates 
            pred_counter = defaultdict(int)

            for statement in component.nodes:
                # NOTE: 'pos_occ' applicable since all head literals are positive predicate literals
                for literal in statement.head.pos_occ():
                    # increment counter for literal predicate signature
                    pred_counter[literal.pred()] += 1

            ref_component_seq = component.sequence()

            for ref_component in ref_component_seq:
                # wrap refined component in 'Program' object
                ref_component_prog = Program(tuple(ref_component)) # TODO: correct ?

                # predicates which are still open (have not been fully processed yet)
                open_preds = {var for (var, count) in pred_counter.items() if count > 0}

                # can be pre-computed (used for both set updates; NOTE: 'pos_occ' applicable since all head literals are positive predicate literals)
                # TODO: make more efficient by updating incrementally and keeping '_prev' sets?
                possible_literals = set().union(*tuple(inst.head.pos_occ() for inst in possible_inst))

                # compute certain instances (NOTE: 'pos_occ' applicable since all head literals are positive predicate literals)
                certain_inst.update( self.ground_component(ref_component_prog.reduct(open_preds), possible_literals, certain_literals))

                # compute possible instances (NOTE: 'pos_occ' applicable since all head literals are positive predicate literals)
                # TODO: make more efficient by updating incrementally and keeping '_prev' sets?
                certain_literals = set().union(*tuple(inst.head.pos_occ() for inst in certain_inst))

                possible_inst.update( self.ground_component(ref_component_prog, certain_literals, possible_literals) )

                for statement in ref_component:
                    # TODO: decrease pred_counter?
                    for literal in statement.head.pos_occ():
                        # increment counter for literal predicate signature
                        pred_counter[literal.pred()] -= 1

        # return possible instances (includes certain instances)
        return Program(tuple(possible_inst))