from typing import Tuple, Set, Hashable, Optional

from aspy.program.program import Program
from aspy.program.statements.statement import Statement, NormalFact, DisjunctiveFact, ChoiceFact
from .component_graph import ComponentGraph
from .edb_idb import edb_idb


def instantiate(prog: Program) -> Program:
    # TODO: does not take constraints into account ???
    # strong constraint = constraint (as opposed to weak constraint)

    def instantiate_module(component: Tuple[Tuple[Hashable]]) -> None:

        def instantiate_rule(statement: Statement) -> None:
            # TODO: build ground instances of statement using 'atoms' & 'curr_atoms'
            # TODO: simplify ground instances (DLV: 4.3)
            # TODO: add ground instances to ground program
            # TODO: add head atoms of ground instances to 'new_atoms'
            pass

        new_atoms = set()
        curr_atoms = set()

        # TODO: exit rules (from component)?
        # TODO: filter by component!
        exit_statements = component_graph.exit_rules #(component)

        for statement in exit_statements:
            instantiate_rule(statement)

        done = False

        while not done:

            curr_atoms = new_atoms
            new_atoms = set()

            # TODO: recursive rules (from component)?
            # TODO: filter by component!
            recursive_statements = component_graph.recursive_rules #(component)

            for statement in recursive_statements:
                instantiate_rule(statement)
            
            atoms = atoms.union(curr_atoms)

            if not new_atoms:
                done = True

    # compute sets of EDB and IDB predicats
    edb_predicates, idb_predicates = edb_idb(prog.statements)

    # initialize set of ground statements
    ground_statements = []

    # initialize set of atoms with EDB literals
    atoms = set()

    for statement in prog.statements:
        # only facts relevant
        if isinstance(statement, NormalFact):
            literals = tuple([statement.head])
        elif isinstance(statement, DisjunctiveFact):
            literals = statement.head
        elif isinstance(statement, ChoiceFact):
            literals = statement.head.literals
        else:
            continue

        for literal in literals:
            # get predicate symbol and arity
            symbol = literal.atom.name
            arity = len(literal.atom.terms)

            # indeed EDB
            if (symbol, arity) in edb_predicates:
                atoms.add(literal)

    # construct component graph for program
    component_graph = ComponentGraph(prog, idb_predicates)

    # TODO: find a ordering (how?)
    components = component_graph.nodes

    for component in components:
        instantiate_module(prog, component, atoms, ground_statements)

    # TODO: instantiate constraints (DLV: 4.2)
    # TODO: exclude strong constraints earlier?
    # TODO: simplify ground constraints
    # TODO: if ground constraints end up with empty body -> violation! (abort since program is inconsistent)

    # TODO: deal with aggregates and weak constraints (DLV: 4.4!)