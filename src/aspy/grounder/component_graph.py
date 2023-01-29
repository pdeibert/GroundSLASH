from typing import Optional, List, Tuple
from itertools import product
from collections import defaultdict

from .scc import scc as compute_scc
from .edb_idb import edb_idb
from aspy.program.atom import DefaultAtom
from aspy.program.program import Program
from aspy.program.statements.statement import NormalRule, DisjunctiveRule, ChoiceRule


class ComponentGraph:
    """Component graph."""
    def __init__(self, prog: Program, idb_nodes: Optional[List[Tuple[str, int]]]=None) -> None:

        self.exit_rules = set()
        self.recursive_rules = set()
        # TODO: weak constraints?
        # TODO: aggregates?

        # TODO asign rules to components!!!!!

        # ----- compute dependency graph -----

        if idb_nodes is None:
            # nodes are the IDB predicates defined by a program (i.e., the predicates that are defined only by facts.)
            _, dep_nodes = edb_idb(prog.statements)
        else:
            dep_nodes = idb_nodes

        # edge (p,q) present if q appears in a rule head where p occurs in a positive/negative body literal.
        dep_pos_edges = set()
        dep_neg_edges = set()

        # dictionary mapping positive edges to rules (to distinguish recursive from exit rules)
        pos_rule_map = defaultdict(list)

        for rule in prog.non_facts:

            # TODO: combine?
            if isinstance(rule, NormalRule):
                head_literals = rule.head
            elif isinstance(rule, DisjunctiveRule):
                head_literals = rule.head
            elif isinstance(rule, ChoiceRule):
                head_literals = tuple([element.atom for element in rule.head.literals])
            else:
                # just in case
                raise Exception

            # get head predicates
            head_predicates = set([( literal.atom.name, len(literal.atom.terms) ) for literal in head_literals])

            # identify all IDB predicates appearing in the head
            q = head_predicates.intersection(dep_nodes)

            # skip if rule does not induce any IDB edges
            if not q:
                continue

            # get positive/negative body literals
            # TODO: refactor as statement method?
            pos_body_literals, neg_body_literals = [], []
            
            for literal in rule.body:
                # TODO: aggregates? builtin-atoms?
                if isinstance(literal, (DefaultAtom)):
                    if literal.dneg:
                        neg_body_literals.append(literal)
                    else:
                        pos_body_literals.append(literal)

            # get predicates appearing in positive/negative body literals
            pos_body_predicates = set([(literal.atom.name, literal.atom.arity) for literal in pos_body_literals])
            neg_body_predicates = set([(literal.atom.name, literal.atom.arity) for literal in neg_body_literals])

            # identify all IDB predicates appearing positively/negative in the body        
            p_pos = pos_body_predicates.intersection(dep_nodes)
            p_neg = neg_body_predicates.intersection(dep_nodes)

            # update edges
            if p_pos:
                edges = tuple(product(p_pos, q))

                # keep track of corresponding rule for each edge
                for edge in edges:
                    pos_rule_map[edge].append(rule)
    
                dep_pos_edges.update(edges)
            if p_neg:
                edges = tuple(product(p_neg, q))
                dep_neg_edges.update(tuple(product(p_neg, q)))

        # ----- compute component graph -----

        # compute strongly connected components
        self.nodes = compute_scc(dep_nodes, dep_pos_edges)

        # aggregate edges by SCCs
        self.pos_edges = []
        self.neg_edges = []

        # iterate over positive edges
        for (src, dst) in dep_pos_edges:
            for scc in self.nodes:
                if src in scc:
                    src_scc = scc
                if dst in scc:
                    dst_scc = scc
            
            # ignore edges within SCC
            if src_scc == dst_scc:
                # mark rule as recursive
                self.recursive_rules.update(pos_rule_map[(src, dst)])
            else:
                # mark rule as an exit rule
                self.exit_rules.update(pos_rule_map[(src, dst)])
                # append positive edge between SCCs
                self.pos_edges.append( (src_scc, dst_scc) )

        # iterate over negative edges
        for (src, dst) in dep_neg_edges:
            for scc in self.nodes:
                if src in scc:
                    src_scc = scc
                if dst in scc:
                    dst_scc = scc

            # ignore edges within SCC or edges that already have a positive counterpart
            if src_scc == dst_scc or (src, dst) in self.pos_edges:
                continue
            else:
                # append negative edge between SCCs
                self.neg_edges.append( (src_scc, dst_scc) )