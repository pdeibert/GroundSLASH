from typing import Tuple, List

from aspy.program.statements.statement import Statement, Fact, NormalFact, DisjunctiveFact, ChoiceFact, NormalRule, DisjunctiveRule, ChoiceRule


def edb_idb(statements: Tuple[Statement, ...]) -> Tuple[List[Tuple[str, int]], List[Tuple[str, int]]]:

    fact_definitions = set()
    rule_definitions = set()

    for statement in statements:
        if isinstance(statement, (NormalFact, NormalRule)):
            literals = tuple([statement.head])
        elif isinstance(statement, (DisjunctiveFact, DisjunctiveRule)):
            literals = statement.head
        elif isinstance(statement, (ChoiceFact, ChoiceRule)):
            literals = statement.head.literals
        else:
            continue

        for literal in literals:
            # get predicate symbol and arity
            symbol = literal.atom.name
            arity = len(literal.atom.terms)

            if isinstance(statement, Fact):
                fact_definitions.add( (symbol, arity) )
            else:
                rule_definitions.add( (symbol, arity) )

    # EDB predicates: predicates ONLY defined by facts
    edb_predicates = fact_definitions - rule_definitions
    # IDB predicates: all else
    idb_predicates = rule_definitions.union(fact_definitions - edb_predicates)

    return (edb_predicates, idb_predicates)