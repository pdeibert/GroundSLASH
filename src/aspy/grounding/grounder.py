#from typing import Set, Dict
from collections import defaultdict
from copy import deepcopy

from aspy.program.statements import Rule, Fact, Constraint, WeakConstraint, OptimizeStatement
from aspy.program.program import Program

from .graphs import ComponentGraph


class Grounder:
    def __init__(self, prog: Program) -> None:

        if not prog.safe:
            raise ValueError("Grounding requires program to be safe.")

        self.prog = prog

    def ground(self) -> Program:

        # TODO: flags for reassembling??? (e.g. optimize statements, choice rules, aggregates)

        # dictionary mapping original statements to their ground counterparts
        ground_dict = defaultdict(list)

        # group statements
        rules = []
        strong_constraints = []
        weak_constraints = []
        optimize = []

        for statement in self.prog.statements:
            # rule/fact
            if isinstance(statement, (Rule, Fact)):
                rules.append(rules)
            # strong constraint
            elif isinstance(statement, Constraint):
                strong_constraints.append(rules)
            # weak constraint
            elif isinstance(statement, WeakConstraint):
                weak_constraints.append(rules)
            # optimize statement
            else:
                optimize.append(rules)

        # TODO: rewrite rules ???

        # compute component graph for rules/facts only
        component_graph = ComponentGraph(rules)

        # compute refined instantiation sequence
        inst_sequence = sum((component.sequence() for component in component_graph.sequence()), ())

        # ground rules/facts
        for statement in inst_sequence:
            # skip matching if rule is already ground
            if statement.ground:
                ground_dict[statement].append(deepcopy(statement))
                continue

            # TODO: ground non-ground rules

        # TODO: ground strong constraints
        # TODO: ground weak constraints and optimize statements

        # TODO: remove redundant statements? maybe inside Program.__init__()? maybe as flag?
        # __hash__, __eq__ for statements and use (default)dict for eliminating duplicates while preserving order